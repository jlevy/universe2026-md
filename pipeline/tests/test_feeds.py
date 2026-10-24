"""
RSS, Atom and JSON Feed parsing, refusal of DTDs, and the non-raising feed fetch.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from textwrap import dedent
from typing import cast

from universe_kb.feeds import FeedError, fetch_feed, parse_feed
from universe_kb.snapshot import Fetcher, FetchResponse

# Out of date order, in Latin-1, with HTML quoted in CDATA that mentions a DOCTYPE.
RSS = dedent("""
    <?xml version="1.0" encoding="ISO-8859-1"?>
    <rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:content="http://purl.org/rss/1.0/modules/content/">
      <channel>
        <title>Ada's Notes</title>
        <link>https://ada.example/</link>
        <item>
          <title>Undated</title>
          <link>notes/undated.html</link>
          <pubDate>sometime soon</pubDate>
        </item>
        <item>
          <title>Permalink guid</title>
          <guid>https://ada.example/posts/guid/</guid>
          <dc:date>2026-08-15</dc:date>
        </item>
        <item>
          <title>Opaque guid</title>
          <guid isPermaLink="false">tag:ada.example,2026:3</guid>
        </item>
        <item>
          <link>https://ada.example/untitled/</link>
        </item>
        <item>
          <title>Engines &amp; café
            analysis</title>
          <link>/posts/engines/</link>
          <pubDate>Tue, 01 Sep 2026 10:00:00 +0200</pubDate>
          <content:encoded><![CDATA[<!DOCTYPE html><p>A quoted page.</p>]]></content:encoded>
        </item>
      </channel>
    </rss>
    """).strip()

ATOM = dedent("""
    <?xml version="1.0" encoding="utf-8"?>
    <!-- generator: hand -->
    <feed xmlns="http://www.w3.org/2005/Atom" xml:base="https://ada.example/atom/">
      <title>Ada</title>
      <entry>
        <title type="html">&lt;em&gt;Difference&lt;/em&gt; engine</title>
        <link rel="edit" href="/api/1"/>
        <link rel="alternate" type="application/json" href="/difference.json"/>
        <link href="difference/"/>
        <published>2026-09-02T09:30:00.123-07:00</published>
        <updated>2026-09-03T00:00:00Z</updated>
      </entry>
      <entry>
        <title>Updated only</title>
        <link rel="alternate" type="text/html" href="https://elsewhere.example/post"/>
        <updated>Wed, 02 Sep 2026 12:00:00 GMT</updated>
      </entry>
      <entry xml:base="/xhtml/">
        <title type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">A <b>bold</b>
          one</div></title>
        <link href="page"/>
        <updated>2026-09-05T10:00:00</updated>
      </entry>
      <entry>
        <title>No link</title>
        <link rel="related" href="https://elsewhere.example/related"/>
      </entry>
    </feed>
    """).strip()

JSON_FEED = json.dumps({
    "version": "https://jsonfeed.org/version/1.1",
    "title": "Ada",
    "items": [
        {"id": "1", "title": "JSON first", "url": "/j/1",
         "date_published": "2026-09-04T08:00:00+00:00"},
        {"id": "2", "content_text": "An untitled micro post.", "url": "/j/2"},
        {"id": "3", "title": "External only", "external_url": "https://elsewhere.example/x",
         "date_modified": "2026-09-01"},
    ],
})


def test_parse_feed_formats() -> None:
    assert parse_feed(RSS, "https://ada.example/blog/feed.xml") == [
        {"title": "Undated", "url": "https://ada.example/blog/notes/undated.html",
         "published": None},
        {"title": "Permalink guid", "url": "https://ada.example/posts/guid/",
         "published": "2026-08-15"},
        {"title": "Engines & café analysis", "url": "https://ada.example/posts/engines/",
         "published": "2026-09-01T08:00:00Z"},
    ]
    assert parse_feed(ATOM, "https://feeds.example/ada.atom") == [
        {"title": "Difference engine", "url": "https://ada.example/atom/difference/",
         "published": "2026-09-02T16:30:00Z"},
        {"title": "Updated only", "url": "https://elsewhere.example/post",
         "published": "2026-09-02T12:00:00Z"},
        {"title": "A bold one", "url": "https://ada.example/xhtml/page",
         "published": "2026-09-05T10:00:00Z"},
    ]
    assert parse_feed("﻿" + JSON_FEED, "https://ada.example/feed.json") == [
        {"title": "JSON first", "url": "https://ada.example/j/1",
         "published": "2026-09-04T08:00:00Z"},
        {"title": "External only", "url": "https://elsewhere.example/x",
         "published": "2026-09-01"},
    ]


def _refusal(text: str) -> str:
    try:
        parse_feed(text, "https://evil.example/feed.xml")
    except FeedError as error:
        return str(error)
    raise AssertionError(f"parse_feed accepted {text[:40]!r}")


def test_parse_feed_refuses_dtds_and_non_feeds() -> None:
    billion_laughs = dedent("""
        <?xml version="1.0"?>
        <!-- looks harmless -->
        <!DOCTYPE rss [
          <!ENTITY lol "lol">
          <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
        ]>
        <rss version="2.0"><channel><item>
          <title>&lol2;</title><link>https://evil.example/</link>
        </item></channel></rss>
        """).strip()
    external = '<!doctype rss SYSTEM "file:///etc/passwd"><rss version="2.0"/>'
    for text in (billion_laughs, external):
        assert _refusal(text).startswith("refused a DOCTYPE")

    assert _refusal("<html><body>Not a feed</body></html>").startswith("unsupported root")
    assert _refusal("<rss><channel>").startswith("malformed XML")
    assert _refusal('{"items": []}') == "not a JSON Feed 1.x document"
    assert _refusal('{"items": ' + "[" * 100_000).startswith("malformed JSON")


@dataclass
class StubFetcher:
    responses: dict[str, FetchResponse]

    def fetch(self, url: str) -> FetchResponse:
        return self.responses[url]


def test_fetch_feed_sorts_caps_and_reports() -> None:
    stub = StubFetcher({
        "http://ada.example/feed": FetchResponse(
            200, "https://ada.example/blog/feed.xml", "application/rss+xml",
            RSS.encode("iso-8859-1"), None),
        "https://ada.example/gone": FetchResponse(
            404, "https://ada.example/gone", "text/html", b"<title>404</title>", "HTTP 404"),
        "https://ada.example/": FetchResponse(
            200, "https://ada.example/", "text/html", b"<html>home</html>", None),
        "https://dead.example/feed": FetchResponse(
            None, None, None, b"", "URLError: nodename not known"),
    })
    fetcher = cast(Fetcher, stub)

    feed = fetch_feed(fetcher, "http://ada.example/feed", max_items=10)
    capped = fetch_feed(fetcher, "http://ada.example/feed", max_items=2)

    assert {k: feed[k] for k in ("url", "final_url", "status", "error")} == {
        "url": "http://ada.example/feed",
        "final_url": "https://ada.example/blog/feed.xml",
        "status": 200,
        "error": None,
    }
    assert feed["fetched_at"].endswith("Z")
    assert [i["title"] for i in feed["items"]] == [
        "Engines & café analysis", "Permalink guid", "Undated"]
    assert feed["items"][2]["url"] == "https://ada.example/blog/notes/undated.html"
    assert capped["items"] == feed["items"][:2]

    errors = {url: fetch_feed(fetcher, url) for url in list(stub.responses)[1:]}
    assert {url: (r["status"], r["error"], r["items"]) for url, r in errors.items()} == {
        "https://ada.example/gone": (404, "HTTP 404", []),
        "https://ada.example/": (200, "not a readable feed: unsupported root element 'html'",
                                 []),
        "https://dead.example/feed": (None, "URLError: nodename not known", []),
    }
