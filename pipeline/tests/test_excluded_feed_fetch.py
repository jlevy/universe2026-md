"""Cached homepage exclusions hold before standalone feed collection can make requests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from universe_kb.enrich import enrich_social
from universe_kb.policy import exclusion_fingerprint
from universe_kb.snapshot import Fetcher, FetchResponse, Snapshot


class FakeFetcher:
    def __init__(self, allowed: set[str]) -> None:
        self.allowed = allowed
        self.requested: list[str] = []

    def fetch(self, url: str, **_: Any) -> FetchResponse:
        self.requested.append(url)
        if url not in self.allowed:
            raise AssertionError(f"Excluded or unexpected destination was contacted: {url}")
        body = json.dumps({"version": "https://jsonfeed.org/version/1.1", "items": [
            {"title": "Public project update", "url": "https://kept.example/posts/new",
             "date_published": "2026-10-24T00:00:00Z"}]}).encode()
        return FetchResponse(200, url, "application/feed+json", body, None)


def test_exclusion_added_after_caching_blocks_feed_requests_and_replaces_stale_entries(
        tmp_path: Path) -> None:
    excluded_feeds = {"https://excluded.example/feed.xml", "https://feeds.example/excluded.xml"}
    kept_feed = "https://kept.example/feed.json"
    shared_feed = "https://feeds.example/shared.json"
    for shared in (False, True):
        root = tmp_path / str(shared)
        curation = root / "curation"
        curation.mkdir(parents=True)
        people = curation / "people.yaml"
        people.write_text("people: []\n")
        snapshot = Snapshot(root / "raw")
        snapshot.save_json("rainfocus/sessions.json", {"items": []}, url="https://event.example")
        snapshot.save_json("websites/homepages.json", {
            # Match the existing removal policy's scheme and www normalization.
            "WWW.Excluded.example/": {"status": 200,
                                      "feeds": [*sorted(excluded_feeds), shared_feed]},
            "https://kept.example/": {"status": 200, "feeds": [kept_feed, *(
                [shared_feed] if shared else [])]},
        }, url="https://")
        snapshot.save_json("feeds/feeds.json", {
            url: {"items": [{"title": "Old cached entry"}]} for url in [
                *sorted(excluded_feeds), kept_feed, shared_feed]}, url="https://")
        snapshot.write_manifest()

        # The homepage and feed caches existed before the removal fingerprint.
        people.write_text("people: []\nexclude:\n  - sha256: "
                          + exclusion_fingerprint("site:excluded.example") + "\n")
        allowed = {kept_feed, *([shared_feed] if shared else [])}
        fetcher = FakeFetcher(allowed)
        report = enrich_social(snapshot, cast(Fetcher, fetcher), curation, root / "kb",
                               steps=("feeds",))

        assert fetcher.requested == sorted(allowed)
        saved = Snapshot(snapshot.root).load_json("feeds/feeds.json")
        assert set(saved) == allowed
        assert all(record["items"] == [{"title": "Public project update",
                                       "url": "https://kept.example/posts/new",
                                       "published": "2026-10-24T00:00:00Z"}]
                   for record in saved.values())
        assert report == {"feeds_ok": len(allowed)}
