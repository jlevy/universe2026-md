"""
Mastodon handle parsing, profile lookup and hashtag paging, against fake instances.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from universe_kb.mastodon import hashtag_posts, lookup_profiles, parse_acct
from universe_kb.snapshot import Fetcher, FetchError


def test_parse_acct() -> None:
    cases: dict[str | None, tuple[str, str] | None] = {
        "Ada_L@Hachyderm.IO": ("Ada_L", "hachyderm.io"),
        " @ada@fosstodon.org ": ("ada", "fosstodon.org"),
        "https://Hachyderm.io/@ada": ("ada", "hachyderm.io"),
        "http://hachyderm.io/@ada/": ("ada", "hachyderm.io"),
        "https://mastodon.social/@ada@Hachyderm.io": ("ada", "hachyderm.io"),
        "@ada": None,
        "ada": None,
        "ada@localhost": None,
        "ada@192.168.0.1": None,
        "https://hachyderm.io/@ada/112233": None,
        "https://hachyderm.io/users/ada": None,
        "mailto:" + "@".join(["ada", "hachyderm.io"]): None,
        None: None,
    }
    assert {raw: parse_acct(raw) for raw in cases} == cases


@dataclass
class FakeInstances:
    """Answers `Fetcher.json` from `responses` by URL, raising any exception stored there."""

    responses: dict[str, Any]
    urls: list[str] = field(default_factory=list)

    def json(self, method: str, url: str) -> Any:
        assert method == "GET"
        self.urls.append(url)
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        return response


LINK_FIELD = (
    '<a href="https://ada.example/" target="_blank" rel="nofollow noopener me" translate="no">'
    '<span class="invisible">https://</span><span class="">ada.example/</span>'
    '<span class="invisible"></span></a>'
)
ADA = {
    "id": "109",
    "username": "ada",
    "acct": "ada",
    "display_name": "Ada Lovelace",
    "note": '<p>Engines at <span class="h-card"><a href="https://hachyderm.io/@babbage" '
            'class="u-url mention">@<span>babbage</span></a></span>.</p><p>Second line.</p>',
    "url": "https://hachyderm.io/@ada",
    "avatar": "https://media.hachyderm.io/ada.png",
    "created_at": "2022-11-05T00:00:00.000Z",
    "followers_count": 120,
    "following_count": 30,
    "statuses_count": 450,
    "fields": [
        {"name": "Site", "value": LINK_FIELD, "verified_at": "2024-02-03T04:05:06.789+00:00"},
        {"name": "Pronouns", "value": "she/her &amp; they", "verified_at": None},
    ],
}


def test_lookup_profiles() -> None:
    lookup = "/api/v1/accounts/lookup?acct="
    instances = FakeInstances({
        f"https://hachyderm.io{lookup}Ada": ADA,
        f"https://mastodon.social{lookup}ghost": FetchError("GET ... failed: HTTP 404"),
        f"https://gone.example{lookup}bob": FetchError("GET ... failed: nodename not known"),
        f"https://notmastodon.example{lookup}eve": ValueError("Expecting value"),
    })
    handles = ["https://hachyderm.io/@Ada", "@ada@Hachyderm.io", "ghost@mastodon.social",
               "bob@gone.example", "eve@notmastodon.example", "not a handle"]

    result = lookup_profiles(cast(Fetcher, instances), handles)

    assert instances.urls == list(instances.responses)
    assert result == {
        "ada@hachyderm.io": {
            "acct": "ada@hachyderm.io",
            "url": "https://hachyderm.io/@ada",
            "display_name": "Ada Lovelace",
            "bio": "Engines at [@babbage](https://hachyderm.io/@babbage).\n\nSecond line.",
            "bot": False,
            "followers": 120,
            "following": 30,
            "statuses": 450,
            "created_at": "2022-11-05T00:00:00Z",
            "avatar": "https://media.hachyderm.io/ada.png",
            "fields": [
                {"name": "Site", "value": "https://ada.example/", "url": "https://ada.example/",
                 "verified_at": "2024-02-03T04:05:06Z"},
                {"name": "Pronouns", "value": "she/her & they", "url": None,
                 "verified_at": None},
            ],
        },
        "ghost@mastodon.social": None,
        "bob@gone.example": None,
        "eve@notmastodon.example": None,
    }


def _status(status_id: str, created_at: str, acct: str, *, tags: list[str]) -> dict[str, Any]:
    user = acct.split("@")[0]
    return {
        "id": status_id,
        "created_at": created_at,
        "url": f"https://mastodon.social/@{acct}/{status_id}",
        "language": "en",
        "content": f'<p>Post {status_id} <a href="https://mastodon.social/tags/{tags[0]}" '
                   f'class="mention hashtag" rel="tag">#<span>{tags[0]}</span></a></p>',
        "tags": [{"name": name, "url": f"https://mastodon.social/tags/{name}"} for name in tags],
        "account": {"acct": acct, "url": f"https://example/@{user}", "display_name": "",
                    "note": ""},
    }


TIMELINE = "https://mastodon.social/api/v1/timelines/tag/GitHubUniverse?limit=40"
PAGES = {
    TIMELINE: [
        _status("40", "2026-10-29T18:00:00.000Z", "ada", tags=["GitHubUniverse", "copilot"]),
        _status("39", "2026-10-28T09:00:00.000Z", "bob@fosstodon.org", tags=["githubuniverse"]),
    ],
    f"{TIMELINE}&max_id=39": [
        _status("38", "2026-10-27T23:59:59.000Z", "cy@hachyderm.io", tags=["GitHubUniverse"]),
        _status("37", "2026-09-30T12:00:00.000Z", "ada", tags=["GitHubUniverse"]),
    ],
    f"{TIMELINE}&max_id=37": [],
}


def test_hashtag_posts_pages_back_to_since() -> None:
    instance = FakeInstances(PAGES)

    result = hashtag_posts(cast(Fetcher, instance), "Mastodon.Social", "#GitHubUniverse",
                           since="2026-10-01")

    assert instance.urls == [TIMELINE, f"{TIMELINE}&max_id=39"]
    assert (result["host"], result["tag"], result["error"]) == (
        "mastodon.social", "GitHubUniverse", None)
    assert result["posts"][0] == {
        "id": "40",
        "url": "https://mastodon.social/@ada/40",
        "created_at": "2026-10-29T18:00:00Z",
        "text": "Post 40 [#GitHubUniverse](https://mastodon.social/tags/GitHubUniverse)",
        "language": "en",
        "tags": ["githubuniverse", "copilot"],
        "account": {"acct": "ada@mastodon.social", "url": "https://example/@ada",
                    "display_name": None, "bio": None, "bot": False},
    }
    assert [(p["id"], p["account"]["acct"]) for p in result["posts"]] == [
        ("40", "ada@mastodon.social"), ("39", "bob@fosstodon.org"), ("38", "cy@hachyderm.io"),
    ]

    # An earlier `since` reads to the empty page; `max_pages` caps the requests.
    everything = hashtag_posts(cast(Fetcher, FakeInstances(PAGES)), "mastodon.social",
                               "GitHubUniverse", since="2026-01-01T00:00:00+00:00")
    assert [p["id"] for p in everything["posts"]] == ["40", "39", "38", "37"]
    capped = FakeInstances(PAGES)
    one_page = hashtag_posts(cast(Fetcher, capped), "mastodon.social", "GitHubUniverse",
                             since="2026-01-01", max_pages=1)
    assert (capped.urls, [p["id"] for p in one_page["posts"]]) == ([TIMELINE], ["40", "39"])


def test_hashtag_posts_keeps_posts_read_before_an_error() -> None:
    refusal = FetchError(f"GET {TIMELINE}&max_id=39 failed: HTTP 401")
    instance = FakeInstances({TIMELINE: PAGES[TIMELINE], f"{TIMELINE}&max_id=39": refusal})

    result = hashtag_posts(cast(Fetcher, instance), "mastodon.social", "GitHubUniverse",
                           since="2026-10-01")

    assert result["error"] == str(refusal)
    assert [p["id"] for p in result["posts"]] == ["40", "39"]
