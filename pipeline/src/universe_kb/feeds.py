"""
RSS 2.0, Atom and JSON Feed parsing, for listing what a person has published lately.

Each feed is reduced to its items' titles, links and publication dates; bodies are not
kept. Feeds come from personal websites, so the XML is untrusted input.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import UTC, date, datetime
from email.utils import parsedate_to_datetime
from typing import Any

from universe_kb.html_tree import parse_html
from universe_kb.snapshot import Fetcher, utc_now

ATOM = "{http://www.w3.org/2005/Atom}"
DUBLIN_CORE = "{http://purl.org/dc/elements/1.1/}"
XML_BASE = "{http://www.w3.org/XML/1998/namespace}base"

# Whitespace, the XML declaration, processing instructions and comments: everything that
# may precede the root element except a DOCTYPE.
_PROLOG_ITEM = re.compile(r"\s+|<\?.*?\?>|<!--.*?-->", re.DOTALL)
_DATE_ONLY = re.compile(r"\d{4}-\d{2}-\d{2}")
_HEADER_CHARSET = re.compile(r"charset\s*=\s*\"?([\w.:-]+)", re.IGNORECASE)
_XML_ENCODING = re.compile(rb"""<\?xml[^>]*encoding\s*=\s*["']([\w.:-]+)""")


class FeedError(ValueError):
    """The text is not a feed `parse_feed` can read, or was refused as unsafe."""


def parse_feed(text: str, base_url: str) -> list[dict[str, Any]]:
    """
    Read the items of an RSS 2.0, Atom or JSON Feed 1.x document as `{title, url,
    published}`, in feed order. `url` is resolved against `base_url` (and any `xml:base`
    on the feed or item) and must be http(s). `published` is `YYYY-MM-DD` when the feed
    gives only a date, `YYYY-MM-DDTHH:MM:SSZ` in UTC when it gives a time (a time without
    a zone is taken as UTC), and None when it is missing or unreadable; RFC 822 and ISO
    8601 are both accepted in every format. Items without a title or URL are dropped.
    Raises `FeedError` for anything that is not such a feed.
    """
    text = text.lstrip("﻿")
    if text.lstrip().startswith("{"):
        return _parse_json_feed(text, base_url)
    return _parse_xml_feed(text, base_url)


def fetch_feed(fetcher: Fetcher, url: str, *, max_items: int = 10) -> dict[str, Any]:
    """
    Fetch and parse one feed without raising: a non-200 response or a document that
    `parse_feed` refuses sets `error` and leaves `items` empty. Items are newest first,
    with undated items last in feed order, and at most `max_items` are kept.
    """
    response = fetcher.fetch(url)
    record: dict[str, Any] = {
        "url": url,
        "final_url": response.final_url,
        "status": response.status,
        "error": response.error,
        "items": [],
        "fetched_at": utc_now(),
    }
    if response.status != 200:
        record["error"] = response.error or f"HTTP {response.status}"
        return record
    try:
        items = parse_feed(_decode(response.body, response.content_type),
                           response.final_url or url)
    except FeedError as error:
        record["error"] = f"not a readable feed: {error}"
        return record
    # Normalized dates sort chronologically as strings; a bare date sorts as its midnight.
    dated = sorted((i for i in items if i["published"]), key=lambda i: i["published"],
                   reverse=True)
    undated = [i for i in items if not i["published"]]
    record["items"] = (dated + undated)[:max_items]
    return record


def _parse_xml_feed(text: str, base_url: str) -> list[dict[str, Any]]:
    # Entities can only be declared in a DTD, which must come before the root element, so
    # refusing any `<!...>` there rules out entity expansion ("billion laughs") and
    # external entities without a hardened-parser dependency, while `<!DOCTYPE html>`
    # quoted inside CDATA content stays harmless.
    position = 0
    while match := _PROLOG_ITEM.match(text, position):
        position = match.end()
    if text.startswith("<!", position):
        raise FeedError("refused a DOCTYPE or other declaration before the root element")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise FeedError(f"malformed XML: {error}") from error
    base = _absolute_url(base_url, root.get(XML_BASE)) or base_url
    if root.tag == "rss":
        channel = root.find("channel")
        items = [] if channel is None else [_rss_item(i, base) for i in channel.findall("item")]
    elif root.tag == f"{ATOM}feed":
        items = [_atom_entry(e, base) for e in root.findall(f"{ATOM}entry")]
    else:
        raise FeedError(f"unsupported root element {root.tag!r}")
    return [i for i in items if i["title"] and i["url"]]


def _rss_item(item: ET.Element, base: str) -> dict[str, Any]:
    base = _absolute_url(base, item.get(XML_BASE)) or base
    link = _text(item.find("link"))
    guid = item.find("guid")
    if not link and guid is not None and guid.get("isPermaLink", "true").lower() != "false":
        link = _text(guid)
    return {
        "title": _text(item.find("title")),
        "url": _absolute_url(base, link),
        "published": _normalize_date(
            _text(item.find("pubDate")) or _text(item.find(f"{DUBLIN_CORE}date"))
        ),
    }


def _atom_entry(entry: ET.Element, base: str) -> dict[str, Any]:
    base = _absolute_url(base, entry.get(XML_BASE)) or base
    alternates = [link for link in entry.findall(f"{ATOM}link")
                  if link.get("href") and link.get("rel", "alternate") == "alternate"]
    # Prefer the HTML page when an entry links several representations.
    alternates.sort(key=lambda link: link.get("type", "text/html") != "text/html")
    return {
        "title": _atom_text(entry.find(f"{ATOM}title")),
        "url": _absolute_url(base, alternates[0].get("href")) if alternates else None,
        "published": _normalize_date(
            _text(entry.find(f"{ATOM}published")) or _text(entry.find(f"{ATOM}updated"))
        ),
    }


def _parse_json_feed(text: str, base_url: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(text)
    # Deeply nested arrays exhaust the recursive decoder.
    except (ValueError, RecursionError) as error:
        raise FeedError(f"malformed JSON: {error}") from error
    if not isinstance(data, dict) or "jsonfeed.org/version/1" not in str(data.get("version")):
        raise FeedError("not a JSON Feed 1.x document")
    items = [item for item in data.get("items") or [] if isinstance(item, dict)]
    records = [
        {
            "title": _clean(_string(item.get("title"))),
            "url": _absolute_url(
                base_url, _string(item.get("url")) or _string(item.get("external_url"))
            ),
            "published": _normalize_date(
                _string(item.get("date_published")) or _string(item.get("date_modified"))
            ),
        }
        for item in items
    ]
    return [r for r in records if r["title"] and r["url"]]


def _atom_text(element: ET.Element | None) -> str | None:
    if element is None:
        return None
    kind = element.get("type", "text")
    if kind == "xhtml":
        return _clean("".join(element.itertext()))
    if kind == "html":
        return _clean(parse_html(element.text or "").text())
    return _text(element)


def _text(element: ET.Element | None) -> str | None:
    return None if element is None else _clean(element.text)


def _clean(text: str | None) -> str | None:
    return " ".join((text or "").split()) or None


def _string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _absolute_url(base: str, href: str | None) -> str | None:
    href = (href or "").strip()
    if not href:
        return None
    try:
        url = urllib.parse.urljoin(base, href)
    except ValueError:
        return None
    return url if url.lower().startswith(("http://", "https://")) else None


def _normalize_date(value: str | None) -> str | None:
    text = (value or "").strip()
    if _DATE_ONLY.fullmatch(text):
        try:
            return date.fromisoformat(text).isoformat()
        except ValueError:
            return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = parsedate_to_datetime(text)
        # Older Pythons raise TypeError, and some malformed dates IndexError.
        except (TypeError, ValueError, IndexError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    try:
        utc = parsed.astimezone(UTC)
    # A zone offset can push a year-1 or year-9999 date out of range.
    except OverflowError:
        return None
    return utc.replace(microsecond=0, tzinfo=None).isoformat() + "Z"


def _decode(body: bytes, content_type: str | None) -> str:
    """Decode by the HTTP charset, else the XML declaration, else UTF-8."""
    encoding = "utf-8-sig"
    if header := _HEADER_CHARSET.search(content_type or ""):
        encoding = header.group(1)
    elif declared := _XML_ENCODING.match(body.lstrip()[:200]):
        encoding = declared.group(1).decode("ascii")
    try:
        return body.decode(encoding, errors="replace")
    except LookupError:
        return body.decode("utf-8-sig", errors="replace")
