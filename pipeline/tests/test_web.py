"""
Homepage parsing, social URL classification, and the non-raising fetch beneath them. The
HTTP transport is mocked, including DNS answers and redirects.
"""

from __future__ import annotations

import hashlib
import io
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from email.message import Message
from textwrap import dedent
from typing import Any, ClassVar, cast

import pytest

from universe_kb import fetch_safety
from universe_kb.snapshot import Fetcher, FetchResponse
from universe_kb.web import classify_social_url, fetch_homepage, parse_homepage

HOMEPAGE = dedent("""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Ada Lovelace &middot; Engineer</title>
      <meta name="description" content="Notes on engines and analysis.">
      <meta property="og:title" content="Ada Lovelace">
      <meta property="og:description" content="Open Graph description.">
      <meta property="og:image" content="/img/ada.png">
      <meta property="og:site_name" content="Ada's Notes">
      <meta property="og:type" content="website">
      <meta property="og:locale" content="en_GB">
      <link rel="me" href="https://hachyderm.io/@ada">
      <link rel="alternate" type="application/rss+xml" title="RSS" href="/rss.xml">
      <link rel="alternate" type="application/atom+xml; charset=utf-8" href="atom.xml">
      <link rel="alternate" type="application/json" href="/wp-json/wp/v2/pages/2">
      <link rel="stylesheet" href="/style.css">
    </head>
    <body>
      <svg><title>Menu</title></svg>
      <nav><a href="/">Home</a> <a href="blog/">Blog</a></nav>
      <a rel="me noopener" href="https://github.com/ada">GitHub</a>
      <a href="https://github.com/ada">GitHub again</a>
      <a href="https://github.com/ada/engine">A repository</a>
      <a href="https://github.com/features/copilot">Not a profile</a>
      <a href="https://twitter.com/ada_l">Twitter</a>
      <a href="https://www.linkedin.com/in/ada-lovelace/">LinkedIn</a>
      <a href="https://bsky.app/profile/ada.example">Bluesky</a>
      <a href="https://www.youtube.com/@AdaTalks">YouTube</a>
      <a href="https://twitter.com/ada_l">Twitter again</a>
      <a rel="me" href="about">About me</a>
      <a rel="me" href="mailto:ada@example.com">Email</a>
    </body>
    </html>
    """)


def test_parse_homepage() -> None:
    page = parse_homepage(HOMEPAGE, "https://ada.example/home/")

    assert page["title"] == "Ada Lovelace · Engineer"
    assert page["description"] == "Notes on engines and analysis."
    assert page["og"] == {
        "title": "Ada Lovelace",
        "description": "Open Graph description.",
        "image": "https://ada.example/img/ada.png",
        "site_name": "Ada's Notes",
        "type": "website",
    }
    assert page["rel_me"] == [
        "https://hachyderm.io/@ada",
        "https://github.com/ada",
        "https://ada.example/home/about",
    ]
    assert page["feeds"] == ["https://ada.example/rss.xml", "https://ada.example/home/atom.xml"]
    assert page["social_links"] == [
        "https://hachyderm.io/@ada",
        "https://github.com/ada",
        "https://twitter.com/ada_l",
        "https://www.linkedin.com/in/ada-lovelace/",
        "https://bsky.app/profile/ada.example",
        "https://www.youtube.com/@AdaTalks",
        "https://ada.example/home/about",
    ]

    # An icon title is not the page title, and og:description stands in for a description.
    bare = parse_homepage(
        '<svg><title>Logo</title></svg><meta property="og:description" content="From OG.">',
        "https://b.example/",
    )
    assert (bare["title"], bare["description"]) == (None, "From OG.")


def test_classify_social_url() -> None:
    cases: dict[str, tuple[str, str] | None] = {
        "https://github.com/ada": ("github", "ada"),
        "https://github.com/Ada-L/?tab=repositories": ("github", "Ada-L"),
        "github.com/ada": ("github", "ada"),
        "https://x.com/ada_l": ("x", "ada_l"),
        "https://mobile.twitter.com/ada_l": ("x", "ada_l"),
        "https://www.linkedin.com/in/ada-lovelace/": ("linkedin", "in/ada-lovelace"),
        "https://uk.linkedin.com/company/engines": ("linkedin", "company/engines"),
        "https://bsky.app/profile/Ada.Example": ("bluesky", "ada.example"),
        "https://bsky.app/profile/did:plc:abc123": ("bluesky", "did:plc:abc123"),
        "https://www.youtube.com/@AdaTalks/videos": ("youtube", "@AdaTalks"),
        "https://youtube.com/channel/UC123": ("youtube", "channel/UC123"),
        "https://www.instagram.com/ada.l/": ("instagram", "ada.l"),
        "https://www.threads.net/@ada.l": ("threads", "ada.l"),
        "https://hachyderm.io/@ada": ("mastodon", "ada@hachyderm.io"),
        "https://mastodon.social/@ada@hachyderm.io": ("mastodon", "ada@hachyderm.io"),
        "https://github.com/features": None,
        "https://github.com/ada/engine": None,
        "https://x.com/home": None,
        "https://x.com/ada_l/status/1": None,
        "https://www.linkedin.com/feed/": None,
        "https://bsky.app/profile/ada.example/post/3k": None,
        "https://www.youtube.com/watch?v=abc": None,
        "https://www.instagram.com/p/abc/": None,
        "https://www.threads.net/@ada.l/post/abc": None,
        "https://medium.com/@ada": None,
        "https://ada.example/": None,
        "mailto:ada@example.com": None,
    }
    assert {url: classify_social_url(url) for url in cases} == cases


@dataclass
class StubFetcher:
    response: FetchResponse

    def fetch(self, url: str) -> FetchResponse:
        return self.response


def test_fetch_homepage() -> None:
    body = '<title>Café</title><a rel="me" href="about">About</a>'.encode("iso-8859-1")
    redirected = FetchResponse(
        200, "https://ada.example/home/", "text/html; charset=ISO-8859-1", body, None
    )

    page = fetch_homepage(cast(Fetcher, StubFetcher(redirected)), "http://ada.example")

    assert {k: page[k] for k in ("requested_url", "final_url", "status", "error")} == {
        "requested_url": "http://ada.example",
        "final_url": "https://ada.example/home/",
        "status": 200,
        "error": None,
    }
    assert (page["sha256"], page["bytes"]) == (hashlib.sha256(body).hexdigest(), len(body))
    assert page["fetched_at"].endswith("Z")
    assert (page["title"], page["rel_me"]) == ("Café", ["https://ada.example/home/about"])
    assert body not in page.values()

    not_found = FetchResponse(404, "https://ada.example/x", "text/html", b"<title>404</title>",
                              "HTTP 404")
    pdf = FetchResponse(200, "https://ada.example/cv", "application/pdf", b"%PDF", None)
    for response in (not_found, pdf):
        page = fetch_homepage(cast(Fetcher, StubFetcher(response)), "https://ada.example/x")
        assert (page["status"], page["error"]) == (response.status, response.error)
        assert (page["title"], page["og"], page["social_links"]) == (None, {}, [])


def test_fetcher_fetch_reports_instead_of_raising(monkeypatch: pytest.MonkeyPatch) -> None:
    user_agents: list[str | None] = []
    base = "https://ada.example"

    class Response(io.BytesIO):
        status = 200
        headers: ClassVar = {"Content-Type": "text/html"}

        def geturl(self) -> str:
            return f"{base}/page"

    def open_page(request: urllib.request.Request, *_: Any) -> Any:
        user_agents.append(request.get_header("User-agent"))
        if request.full_url.endswith("/old"):
            headers = Message()
            headers["Location"] = "/page"
            raise urllib.error.HTTPError(request.full_url, 301, "redirect", headers, io.BytesIO())
        if request.full_url.endswith("/page"):
            return Response(b"x" * 100)
        raise urllib.error.HTTPError(request.full_url, 404, "missing", Message(), io.BytesIO())

    monkeypatch.setattr(socket, "getaddrinfo", lambda _host, port, **_kwargs: [
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("93.184.216.34", port))])
    monkeypatch.setattr(fetch_safety, "_open_once", open_page)
    fetcher = Fetcher(delay=0)
    page = fetcher.fetch(f"{base}/old", max_bytes=10)
    missing = fetcher.fetch(f"{base}/missing")

    def refused_connection(*_args: Any, **_kwargs: Any) -> Any:
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(fetch_safety, "_open_once", refused_connection)
    refused = fetcher.fetch(f"{base}/page", timeout=5)
    not_http = fetcher.fetch("ftp://ada.example/notes.txt")

    assert page == FetchResponse(200, f"{base}/page", "text/html", b"x" * 10, None)
    assert (missing.status, missing.final_url, missing.error) == (
        404, f"{base}/missing", "HTTP 404")
    assert user_agents == [fetcher.user_agent] * 3
    assert (refused.status, refused.body) == (None, b"")
    assert refused.error is not None and refused.error.startswith("URLError:")
    assert not_http == FetchResponse(None, None, None, b"", "not an http(s) URL: 'ftp://ada.example/notes.txt'")


def test_profile_classification_rejects_credentials_and_truncated_linkedin_paths() -> None:
    for url in ("https://user:password" + "@x.com/ada", "https://linkedin.com/in/m",
                "https://linkedin.com/in/in", "https://linkedin.com/in/ada/posts/1"):
        assert classify_social_url(url) is None
