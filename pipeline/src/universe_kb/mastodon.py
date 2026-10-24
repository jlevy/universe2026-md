"""
Mastodon profiles and hashtag timelines from each instance's public REST API.

The fediverse has no central directory: an account lives on its home instance, so
`lookup_profiles` asks each account's own instance, and `hashtag_posts` reads one
instance's view of a tag, which holds its local posts plus the remote posts it has
received. Both use only endpoints that need no account or token.
"""

from __future__ import annotations

import logging
import re
import urllib.parse
from datetime import UTC, datetime
from typing import Any

from universe_kb.html_tree import html_to_markdown, parse_html
from universe_kb.snapshot import Fetcher, FetchError

log = logging.getLogger(__name__)

# The largest page Mastodon serves for timelines.
PAGE_LIMIT = 40

_USER = r"[A-Za-z0-9_](?:[A-Za-z0-9_.-]*[A-Za-z0-9_])?"
# A domain name whose last label starts with a letter, which rules out IP addresses.
_HOST = r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z][A-Za-z0-9-]*[A-Za-z0-9]"
_ACCT = re.compile(rf"@?({_USER})@({_HOST})")
_PROFILE_URL = re.compile(rf"https?://({_HOST})/@({_USER})(?:@({_HOST}))?/?", re.IGNORECASE)
# Mastodon splits link text across spans (a hidden scheme, a truncated path) and the
# shared converter joins text nodes with spaces; unwrapping the spans keeps
# `https://example.com`, `@user` and `#tag` whole.
_SPAN_TAG = re.compile(r"</?span\b[^>]*>", re.IGNORECASE)


def parse_acct(handle: str | None) -> tuple[str, str] | None:
    """
    Split a Mastodon account reference (`user@host`, `@user@host` or a profile URL
    `https://host/@user`) into `(user, host)`, with the host lowercased. A profile URL
    that shows a remote account through another instance, `https://host/@user@home`,
    gives the account's home instance. Anything else gives None, including a bare
    `@user`, whose instance is unknown.
    """
    text = (handle or "").strip()
    if match := _ACCT.fullmatch(text):
        return match.group(1), match.group(2).lower()
    if match := _PROFILE_URL.fullmatch(text):
        return match.group(2), (match.group(3) or match.group(1)).lower()
    return None


def lookup_profiles(fetcher: Fetcher, handles: list[str]) -> dict[str, dict[str, Any] | None]:
    """
    Look up each account on its own instance, one request per distinct account. Each
    account maps, as lowercase `user@host`, to its profile, or to None when the instance
    has no such account or the request failed, so an unreachable instance costs only its
    own accounts. Handles that `parse_acct` rejects are left out.
    """
    accounts: dict[str, tuple[str, str]] = {}
    for handle in handles:
        if parsed := parse_acct(handle):
            accounts.setdefault(f"{parsed[0]}@{parsed[1]}".lower(), parsed)
    profiles: dict[str, dict[str, Any] | None] = {}
    for key, (user, host) in accounts.items():
        query = urllib.parse.urlencode({"acct": user})
        try:
            account = fetcher.json("GET", f"https://{host}/api/v1/accounts/lookup?{query}")
        # A host that answers with something other than JSON raises ValueError.
        except (FetchError, ValueError) as error:
            log.info("Mastodon lookup of %s failed: %s", key, error)
            profiles[key] = None
            continue
        profiles[key] = _profile_record(account, host) if isinstance(account, dict) else None
    return profiles


def hashtag_posts(
    fetcher: Fetcher, host: str, tag: str, *, since: str, max_pages: int = 10
) -> dict[str, Any]:
    """
    Read `host`'s public timeline for `tag`, newest first, back to `since` (an ISO date
    or datetime; one without a zone is UTC). Different instances give different views of
    the same tag, since each holds only the remote posts it has received. A refusal (many
    instances require sign-in for timelines) or any other failure sets `error` and keeps
    the posts already read.
    """
    host = host.strip().lower()
    tag = tag.strip().removeprefix("#")
    cutoff = _parse_time(since)
    if cutoff is None:
        raise ValueError(f"`since` is not an ISO date or datetime: {since!r}")
    timeline_url = f"https://{host}/api/v1/timelines/tag/{urllib.parse.quote(tag, safe='')}"
    posts: list[dict[str, Any]] = []
    error: str | None = None
    params = {"limit": str(PAGE_LIMIT)}
    for _ in range(max_pages):
        try:
            page = fetcher.json("GET", f"{timeline_url}?{urllib.parse.urlencode(params)}")
        except (FetchError, ValueError) as fetch_error:
            error = str(fetch_error)
            break
        if not isinstance(page, list):
            error = f"{host} returned {type(page).__name__} instead of a list of statuses"
            break
        reached_cutoff = False
        for status in page:
            created = _parse_time(status.get("created_at"))
            if created is not None and created < cutoff:
                reached_cutoff = True
                break
            posts.append(_post_record(status, host))
        if reached_cutoff or not page or not page[-1].get("id"):
            break
        params["max_id"] = str(page[-1]["id"])
    return {"host": host, "tag": tag, "error": error, "posts": posts}


def _account_record(account: dict[str, Any], host: str) -> dict[str, Any]:
    # The API gives local accounts as a bare username, relative to the instance asked.
    acct = account.get("acct") or account.get("username") or ""
    if "@" not in acct:
        acct = f"{acct}@{host}"
    return {
        "acct": acct,
        "url": account.get("url"),
        "display_name": account.get("display_name") or None,
        "bio": _markdown(account.get("note")) or None,
        # Bots (news relays and aggregators) post hashtags without attending anything.
        "bot": bool(account.get("bot")),
    }


def _profile_record(account: dict[str, Any], host: str) -> dict[str, Any]:
    return _account_record(account, host) | {
        "followers": account.get("followers_count"),
        "following": account.get("following_count"),
        "statuses": account.get("statuses_count"),
        "created_at": _utc_seconds(account.get("created_at")),
        "avatar": account.get("avatar"),
        "fields": [_field_record(f) for f in account.get("fields") or [] if isinstance(f, dict)],
    }


def _field_record(field: dict[str, Any]) -> dict[str, Any]:
    tree = parse_html(_SPAN_TAG.sub("", field.get("value") or ""))
    hrefs = (a.attrs.get("href", "") for a in tree.find_all("a"))
    return {
        "name": field.get("name"),
        "value": tree.text(),
        "url": next((h for h in hrefs if h.lower().startswith(("http://", "https://"))), None),
        "verified_at": _utc_seconds(field.get("verified_at")),
    }


def _post_record(status: dict[str, Any], host: str) -> dict[str, Any]:
    tags = [t["name"].lower() for t in status.get("tags") or []
            if isinstance(t, dict) and isinstance(t.get("name"), str)]
    return {
        "id": status.get("id"),
        "url": status.get("url") or status.get("uri"),
        "created_at": _utc_seconds(status.get("created_at")),
        "text": _markdown(status.get("content")),
        "language": status.get("language"),
        "tags": list(dict.fromkeys(tags)),
        "account": _account_record(status.get("account") or {}, host),
    }


def _markdown(html: str | None) -> str:
    return html_to_markdown(_SPAN_TAG.sub("", html or ""))


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _utc_seconds(value: Any) -> str | None:
    """Mastodon timestamps carry milliseconds; keep whole seconds, in UTC."""
    parsed = _parse_time(value)
    if parsed is None:
        return None
    try:
        utc = parsed.astimezone(UTC)
    # Remote servers supply their own timestamps, and an offset can overflow year 1 or 9999.
    except OverflowError:
        return None
    return utc.replace(microsecond=0, tzinfo=None).isoformat() + "Z"
