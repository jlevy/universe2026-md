"""Enrichment targets chosen from saved snapshots and the built knowledge base."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from universe_kb.enrich import (
    GitHubClient,
    kb_person_handles,
    kb_person_websites,
    profile_github_logins,
    refresh_repositories,
)
from universe_kb.snapshot import FetchError, Snapshot


def snapshot_with(root: Path, files: dict[str, Any]) -> Snapshot:
    for rel_path, data in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
    return Snapshot(root)


def test_profile_github_logins_come_from_people_s_own_profile_links(tmp_path: Path) -> None:
    snapshot = snapshot_with(tmp_path, {
        "brightdata/linkedin_profiles.json": {"https://www.linkedin.com/in/ada": {"records": [
            {"bio_links": [{"title": "Portfolio", "link": "https://github.com/AdaL"},
                           {"title": "Blog", "link": "https://ada.dev"}]}]}},
        "brightdata/x_profiles.json": {"https://x.com/alan": {"records": [
            {"external_link": "https://github.com/alan-t/"}, {"external_link": None}]}},
        "mastodon/profiles.json": {
            "grace@hachyderm.io": {"fields": [
                {"url": "https://github.com/ghopper", "verified_at": "2022-11-04T17:15:34Z"},
                {"url": "https://github.com/unverified", "verified_at": None}]},
            "gone@gone.example": None},
        "websites/homepages.json": {"https://joan.dev": {
            "rel_me": ["https://github.com/joanclarke", "https://hachyderm.io/@joan"]}},
    })

    # Repository links and unverified Mastodon fields are not identity claims.
    assert profile_github_logins(snapshot) == ["AdaL", "alan-t", "ghopper", "joanclarke"]


def test_kb_person_websites_lists_only_people_s_sites(tmp_path: Path) -> None:
    websites = tmp_path / "kb" / "websites"
    websites.mkdir(parents=True)
    for name, owner in (("ada.dev", "person:ada"), ("example.com", "org:example")):
        (websites / f"{name}.yaml").write_text(
            f"website:\n  id: site:{name}\n  url: https://{name}/\n  owner: {owner}\n")

    assert kb_person_websites(tmp_path / "kb") == ["https://ada.dev/"]


def test_kb_person_handles_lists_people_s_accounts_on_one_platform(tmp_path: Path) -> None:
    accounts = tmp_path / "kb" / "accounts" / "bluesky"
    accounts.mkdir(parents=True)
    for handle, owner in (("ada.bsky.social", "person:ada"), ("acme.com", "org:acme")):
        (accounts / f"{handle}.yaml").write_text(
            f"social_account:\n  handle: {handle}\n  owner: {owner}\n")

    assert kb_person_handles(tmp_path / "kb", "bluesky") == ["ada.bsky.social"]
    assert kb_person_handles(tmp_path / "kb", "mastodon") == []


def test_an_owner_whose_stars_time_out_is_fetched_without_star_detail() -> None:
    class Client(GitHubClient):
        def __init__(self) -> None:
            self.queries: list[str] = []

        def query(self, query: str) -> dict[str, Any]:
            self.queries.append(query)
            if "STARRED_AT" in query:
                raise FetchError("POST https://api.github.com/graphql failed: HTTP 502")
            return {"o0": {"login": "starry", "isGitHubStar": False}}

    client = Client()

    assert client.owners(["Starry"]) == {"starry": {"login": "starry", "isGitHubStar": False}}
    assert ["STARRED_AT" in q for q in client.queries] == [True, False]


def test_an_owner_that_times_out_even_without_stars_is_skipped_not_fatal() -> None:
    class Client(GitHubClient):
        def __init__(self) -> None:
            pass

        def query(self, query: str) -> dict[str, Any]:
            if "stuck" in query:
                raise FetchError("POST https://api.github.com/graphql failed: HTTP 504")
            return {"o0": {"login": "fine"}}

    assert Client().owners(["stuck", "fine"]) == {"fine": {"login": "fine"}}


def repo_node(full_name: str, stars: int) -> dict[str, Any]:
    return {"nameWithOwner": full_name, "stargazerCount": stars, "forkCount": 1,
            "isArchived": False, "pushedAt": "2026-10-01T00:00:00Z",
            "watchers": {"totalCount": 3}, "issues": {"totalCount": 4}}


def write_kb_repositories(kb_dir: Path, full_names: list[str]) -> None:
    for full_name in full_names:
        path = kb_dir / "repositories" / f"{full_name.lower()}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"repository:\n  id: repo:{full_name.lower()}\n"
                        f"  full_name: {full_name}\n  stars: 1\n")


class FakeRepoClient(GitHubClient):
    """Answers repository queries from `known`; a name in `failing` breaks its request."""

    def __init__(self, known: dict[str, int], failing: frozenset[str] = frozenset()) -> None:
        self.known = known
        self.failing = failing
        self.queries: list[str] = []

    def query(self, query: str) -> dict[str, Any]:
        self.queries.append(query)
        if any(f'name: "{name.split("/")[1]}"' in query for name in self.failing):
            raise FetchError("POST https://api.github.com/graphql failed: HTTP 502")
        data: dict[str, Any] = {}
        for alias, owner, name in re.findall(
                r'(r\d+): repository\(owner: "([^"]+)", name: "([^"]+)"\)', query):
            stars = self.known.get(f"{owner}/{name}".lower())
            data[alias] = None if stars is None else repo_node(f"{owner}/{name}", stars)
        return data


def test_refresh_repositories_records_counts_missing_and_unfetched(tmp_path: Path) -> None:
    kb_dir = tmp_path / "kb"
    write_kb_repositories(kb_dir, ["octo/Alive", "octo/gone", "octo/flaky", "octo/other"])
    snapshot = snapshot_with(tmp_path / "raw", {})
    github = FakeRepoClient({"octo/alive": 120, "octo/flaky": 7, "octo/other": 9},
                            failing=frozenset({"octo/flaky"}))

    report = refresh_repositories(snapshot, github, kb_dir)

    stats = json.loads((tmp_path / "raw/github/repo-stats.json").read_text())
    assert set(stats) == {"octo/alive", "octo/gone", "octo/other"}
    assert stats["octo/alive"]["stargazerCount"] == 120
    assert stats["octo/alive"]["watchers"] == {"totalCount": 3}
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", stats["octo/alive"]["fetched_at"])
    # A deleted repository is a fact to record; a server error is not.
    assert stats["octo/gone"] == {"missing": True, "fetched_at": stats["octo/alive"]["fetched_at"]}
    assert report["refreshed"] == 2
    assert report["missing"] == 1
    assert report["unfetched_names"] == ["octo/flaky"]
    # The failing batch was split until the bad repository stood alone.
    assert len(github.queries) > 1
    manifest = json.loads((tmp_path / "raw/manifest.json").read_text())["files"]
    assert manifest["github/repo-stats.json"]["method"] == "POST"


def test_refresh_repositories_saves_each_group_and_resumes(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    kb_dir = tmp_path / "kb"
    names = [f"octo/r{i:03d}" for i in range(5)]
    write_kb_repositories(kb_dir, names)
    snapshot = snapshot_with(tmp_path / "raw", {})
    monkeypatch.setattr("universe_kb.enrich.REPO_STATS_SAVE_EVERY", 2)
    monkeypatch.setattr("universe_kb.enrich.REPO_STATS_BATCH", 2)
    saved: list[int] = []
    save_json = snapshot.save_json

    def counting_save(rel_path: str, data: Any, **kwargs: Any) -> None:
        saved.append(len(data))
        save_json(rel_path, data, **kwargs)

    monkeypatch.setattr(snapshot, "save_json", counting_save)

    class Interrupted(GitHubClient):
        """Serves the first four repositories, then the run is interrupted."""

        def __init__(self) -> None:
            self.inner = FakeRepoClient({n: 1 for n in names})

        def query(self, query: str) -> dict[str, Any]:
            if "r004" in query:
                raise KeyboardInterrupt
            return self.inner.query(query)

    with pytest.raises(KeyboardInterrupt):
        refresh_repositories(snapshot, Interrupted(), kb_dir)

    # Progress was saved after each group of two, before the interruption.
    assert saved == [2, 4]
    stats = json.loads((tmp_path / "raw/github/repo-stats.json").read_text())
    assert sorted(stats) == names[:4]

    # A second run reads only what is not fresh yet.
    resumed = FakeRepoClient({n: 2 for n in names})
    report = refresh_repositories(Snapshot(tmp_path / "raw"), resumed, kb_dir)
    assert report["skipped_fresh"] == 4
    assert report["refreshed"] == 1
    assert len(resumed.queries) == 1 and "r004" in resumed.queries[0]
    # With no age limit, everything is read again.
    again = refresh_repositories(Snapshot(tmp_path / "raw"), resumed, kb_dir, max_age_hours=0)
    assert again["refreshed"] == 5
