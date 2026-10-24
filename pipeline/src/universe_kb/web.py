"""
Personal homepages and social profile URLs, for modeling each person's online presence.

A homepage is fetched once and reduced to the metadata that says who owns it and where
else they are: title, description, Open Graph tags, `rel=me` links, feeds and links to
social profiles. The body is not kept; its SHA-256 records which bytes the metadata came
from.
"""

from __future__ import annotations

import hashlib
import re
import urllib.parse
from typing import Any

from universe_kb.bluesky import normalize_handle
from universe_kb.html_tree import Node, parse_html
from universe_kb.snapshot import Fetcher, FetchResponse, utc_now

OG_KEYS = ("title", "description", "image", "site_name", "type")
# Plain `application/json` alternates are left out: WordPress emits them for its REST API.
FEED_TYPES = {"application/rss+xml", "application/atom+xml", "application/feed+json"}
HTML_TYPES = {"text/html", "application/xhtml+xml"}

_GITHUB_USER = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")
_GITHUB_RESERVED = frozenset({
    "about", "account", "apps", "codespaces", "collections", "contact", "copilot",
    "customer-stories", "dashboard", "discussions", "education", "enterprise", "enterprises",
    "events", "explore", "features", "home", "issues", "join", "login", "logout",
    "marketplace", "mcp", "mobile", "new", "newsroom", "nonprofit", "notifications",
    "open-source", "organizations", "orgs", "partners", "premium-support", "pricing",
    "pulls", "readme", "resources", "search", "security", "sessions", "settings", "signup",
    "site", "solutions", "sponsors", "stars", "team", "topics", "trending", "users",
})
_X_USER = re.compile(r"[A-Za-z0-9_]{1,15}")
_X_RESERVED = frozenset({
    "about", "account", "compose", "download", "explore", "hashtag", "home", "i", "intent",
    "jobs", "login", "logout", "messages", "notifications", "privacy", "search", "settings",
    "share", "signup", "tos",
})
_INSTAGRAM_USER = re.compile(r"[A-Za-z0-9._]{1,30}")
_INSTAGRAM_RESERVED = frozenset({
    "about", "accounts", "developer", "direct", "explore", "legal", "privacy", "reels",
})
# `@user` or, for a remote account viewed through another instance, `@user@host`.
_MASTODON_PATH = re.compile(r"@([A-Za-z0-9_](?:[A-Za-z0-9_.-]*[A-Za-z0-9_])?)(?:@([a-z0-9.-]+))?")
# Sites outside the fediverse that also put profiles at `/@user`.
_NOT_MASTODON = frozenset({
    "figma.com", "glitch.com", "hashnode.com", "jsr.io", "medium.com", "observablehq.com",
    "producthunt.com", "replit.com", "skool.com", "substack.com", "tiktok.com", "unsplash.com",
})
_META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?([\w.:-]+)""", re.IGNORECASE)


def parse_homepage(html: str, base_url: str) -> dict[str, Any]:
    """
    Extract identity metadata from a homepage. Relative URLs resolve against `base_url`,
    which should be the final URL after redirects. Only http(s) URLs are kept, so a
    `mailto:` rel=me link is dropped, and each list is de-duplicated in document order.
    """
    tree = parse_html(html)
    title = next(
        (node.text() or None for node in tree.find_all("title") if not _inside_svg(node)), None
    )

    meta: dict[str, str] = {}
    for node in tree.find_all("meta"):
        content = node.attrs.get("content", "").strip()
        # Some pages put `name` and `property` on one tag, so register both.
        for attr in ("name", "property"):
            key = node.attrs.get(attr, "").strip().lower()
            if key and content:
                meta.setdefault(key, content)
    og = {key: meta[f"og:{key}"] for key in OG_KEYS if f"og:{key}" in meta}
    if "image" in og:
        og["image"] = urllib.parse.urljoin(base_url, og["image"])

    rel_me: list[str] = []
    feeds: list[str] = []
    social_links: list[str] = []
    for node in tree.iter():
        if node.tag not in ("a", "link"):
            continue
        url = _absolute_http_url(base_url, node.attrs.get("href", ""))
        if url is None:
            continue
        rel = node.attrs.get("rel", "").lower().split()
        if "me" in rel:
            rel_me.append(url)
        feed_type = _media_type(node.attrs.get("type"))
        if node.tag == "link" and "alternate" in rel and feed_type in FEED_TYPES:
            feeds.append(url)
        if "me" in rel or (node.tag == "a" and classify_social_url(url) is not None):
            social_links.append(url)

    return {
        "title": title,
        "description": meta.get("description") or og.get("description"),
        "og": og,
        "rel_me": _unique(rel_me),
        "feeds": _unique(feeds),
        "social_links": _unique(social_links),
    }


def fetch_homepage(fetcher: Fetcher, url: str) -> dict[str, Any]:
    """
    Fetch one homepage and summarize it without storing the body. A failed fetch is an
    ordinary result: `status` and `error` say what happened and the parse fields are
    empty. Only an HTML response with status 200 is parsed.
    """
    response = fetcher.fetch(url)
    got_response = response.status is not None
    record: dict[str, Any] = {
        "requested_url": url,
        "final_url": response.final_url,
        "status": response.status,
        "error": response.error,
        "content_type": response.content_type,
        "sha256": hashlib.sha256(response.body).hexdigest() if got_response else None,
        "bytes": len(response.body),
        "fetched_at": utc_now(),
    }
    if response.status == 200 and _is_html(response):
        html = _decode(response.body, response.content_type)
        return record | parse_homepage(html, response.final_url or url)
    return record | {
        "title": None, "description": None, "og": {}, "rel_me": [], "feeds": [],
        "social_links": [],
    }


def classify_social_url(url: str) -> tuple[str, str] | None:
    """
    Identify a social profile URL as `(platform, handle)`, or return None for anything
    else, including repositories, posts and site pages such as `github.com/features`. A
    URL without a scheme is read as https.

    Handles keep the case written in the URL, except Bluesky handles, which the protocol
    lowercases, so compare handles case-insensitively. LinkedIn handles are `in/<slug>`
    or `company/<slug>`. YouTube handles are `@name`, or `c/<name>`, `channel/<id>` or
    `user/<name>` for older channel URLs. Mastodon handles are `user@host` and are
    recognized by the `https://<host>/@<user>` shape alone, so a site not listed in
    `_NOT_MASTODON` that uses the same shape is misread as Mastodon.
    """
    url = url.strip()
    if not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", url):
        url = "https://" + url.lstrip("/")
    try:
        parts = urllib.parse.urlsplit(url)
        host = (parts.hostname or "").lower()
        _ = parts.port  # raises on malformed ports
    except ValueError:
        return None
    if (parts.scheme.lower() not in ("http", "https") or not host
            or parts.username is not None or any(ch.isspace() for ch in url)):
        return None
    segments = [urllib.parse.unquote(s) for s in parts.path.split("/") if s]
    first = segments[0] if segments else ""
    site = re.sub(r"^(?:www|m|mobile)\.", "", host)

    if site == "github.com":
        if (len(segments) == 1 and _GITHUB_USER.fullmatch(first)
                and first.lower() not in _GITHUB_RESERVED):
            return "github", first
        return None
    if site in ("x.com", "twitter.com"):
        if len(segments) == 1 and _X_USER.fullmatch(first) and first.lower() not in _X_RESERVED:
            return "x", first
        return None
    if site == "linkedin.com" or site.endswith(".linkedin.com"):
        if (len(segments) == 2 and first.lower() in ("in", "company")
                and len(segments[1]) >= 2 and re.fullmatch(r"[\w%.-]+", segments[1])
                and segments[1].lower() not in {"in", "company", "na", "n-a"}):
            return "linkedin", f"{first.lower()}/{segments[1]}"
        return None
    if site == "bsky.app":
        if len(segments) == 2 and first == "profile":
            handle, _ = normalize_handle(segments[1])
            return ("bluesky", handle) if handle else None
        return None
    if site == "youtube.com":
        if len(first) > 1 and first.startswith("@"):
            return "youtube", first
        if len(segments) >= 2 and first in ("c", "channel", "user"):
            return "youtube", f"{first}/{segments[1]}"
        return None
    if site == "instagram.com":
        if (len(segments) == 1 and _INSTAGRAM_USER.fullmatch(first)
                and first.lower() not in _INSTAGRAM_RESERVED):
            return "instagram", first
        return None
    if site in ("threads.net", "threads.com"):
        if len(segments) == 1 and first.startswith("@") and _INSTAGRAM_USER.fullmatch(first[1:]):
            return "threads", first[1:]
        return None
    if len(segments) == 1 and site not in _NOT_MASTODON:
        match = _MASTODON_PATH.fullmatch(first)
        if match:
            return "mastodon", f"{match.group(1)}@{match.group(2) or host}"
    return None


def _inside_svg(node: Node) -> bool:
    parent = node.parent
    while parent is not None:
        if parent.tag == "svg":
            return True
        parent = parent.parent
    return False


def _absolute_http_url(base_url: str, href: str) -> str | None:
    href = href.strip()
    if not href:
        return None
    try:
        url = urllib.parse.urljoin(base_url, href)
    except ValueError:
        return None
    return url if url.lower().startswith(("http://", "https://")) else None


def _media_type(content_type: str | None) -> str:
    return (content_type or "").split(";")[0].strip().lower()


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def _is_html(response: FetchResponse) -> bool:
    if response.content_type:
        return _media_type(response.content_type) in HTML_TYPES
    # No Content-Type header: sniff, as browsers do.
    return response.body.lstrip()[:15].lower().startswith((b"<!doctype html", b"<html"))


def _decode(body: bytes, content_type: str | None) -> str:
    charset = "utf-8"
    if header := re.search(r"charset\s*=\s*\"?([\w.:-]+)", content_type or "", re.IGNORECASE):
        charset = header.group(1)
    elif declared := _META_CHARSET.search(body[:4096]):
        charset = declared.group(1).decode("ascii")
    try:
        return body.decode(charset, errors="replace")
    except LookupError:
        return body.decode("utf-8", errors="replace")
