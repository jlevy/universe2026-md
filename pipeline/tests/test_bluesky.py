"""
Bluesky handle normalization and batched profile lookup, against a fake AppView.
"""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field
from typing import Any, cast

from universe_kb.bluesky import GET_PROFILES_URL, fetch_profiles, normalize_handle
from universe_kb.snapshot import Fetcher

DID = "did:plc:z72i7hdynmk6r22z27h6tvur"


def test_normalize_handle() -> None:
    cases: dict[str | None, tuple[str | None, bool]] = {
        "https://bsky.app/profile/Ada.Example": ("ada.example", False),
        "bsky.app/profile/ada.bsky.social/": ("ada.bsky.social", False),
        f"https://bsky.app/profile/{DID}": (DID, False),
        DID: (DID, False),
        "@Ada.bsky.social": ("ada.bsky.social", False),
        "ada": ("ada.bsky.social", True),
        "@ada": ("ada.bsky.social", True),
        None: (None, False),
        "  ": (None, False),
        "N/A": (None, False),
        "Ada Lovelace": (None, False),
    }
    assert {raw: normalize_handle(raw) for raw in cases} == cases


@dataclass
class FakeAppView:
    """Answers getProfiles from `profiles`, keyed by the actor as requested."""

    profiles: dict[str, dict[str, Any]]
    urls: list[str] = field(default_factory=list)

    def json(self, method: str, url: str) -> Any:
        assert method == "GET"
        self.urls.append(url)
        actors = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)["actors"]
        return {"profiles": [self.profiles[a] for a in actors if a in self.profiles]}


def test_fetch_profiles_batches_and_reports_missing() -> None:
    users = [f"user{i}.bsky.social" for i in range(26)]
    profiles = {u: {"did": f"did:plc:u{i}", "handle": u, "followersCount": i}
                for i, u in enumerate(users)}
    profiles[DID] = {
        "did": DID, "handle": "ada.example", "displayName": "Ada", "description": "Engines.",
        "followersCount": 10, "followsCount": 2, "postsCount": 3,
        "createdAt": "2024-01-01T00:00:00.000Z", "avatar": "https://cdn.example/ada.jpg",
        "labels": [],
    }
    app_view = FakeAppView(profiles)
    actors = ["User0.bsky.social", *users[1:], "USER1.bsky.social", DID, "ghost.bsky.social"]

    result = fetch_profiles(cast(Fetcher, app_view), actors)

    assert all(url.startswith(f"{GET_PROFILES_URL}?") for url in app_view.urls)
    batches = [urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)["actors"]
               for url in app_view.urls]
    assert batches == [users[:25], [users[25], DID, "ghost.bsky.social"]]
    assert list(result) == [*users, DID, "ghost.bsky.social"]
    assert result[DID] == {
        "did": DID, "handle": "ada.example", "display_name": "Ada", "description": "Engines.",
        "followers": 10, "follows": 2, "posts": 3, "created_at": "2024-01-01T00:00:00.000Z",
        "avatar": "https://cdn.example/ada.jpg",
    }
    assert [(r or {}).get("followers") for r in result.values()][:3] == [0, 1, 2]
    assert result["ghost.bsky.social"] is None
