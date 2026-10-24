from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from universe_kb.build import OrgIndex, RawData
from universe_kb.models import Participation, Person, Source, WritingItem
from universe_kb.people import (
    AccountRegistry,
    PeopleIndex,
    filter_catalog_people,
    source_record_fingerprint,
)
from universe_kb.profile_sources import fill_linkedin, writing_from_feeds

SEED = Source(system="curation", snapshot="curation/test.yaml")
OWNER = "person:example-owner"


def raw_with(root: Path, files: dict[str, Any]) -> RawData:
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
    return RawData(root, {name: {"url": "https://snapshot.example/data",
                                "retrieved_at": "2026-10-24T00:00:00Z"} for name in files})


def test_linkedin_outbound_links_require_independent_owner_evidence(tmp_path: Path) -> None:
    person = Person(
        id=OWNER, name="Example Owner", inclusion_basis="curated", github="gh:example-owner",
        github_resolution="resolved", sources=[SEED],
        participations=[Participation(event="event:github-universe-2026", role="speaker",
                                      status="confirmed")])
    registry = AccountRegistry()
    registry.add_social("linkedin", "in/example-owner", OWNER, "event_listing", SEED)
    registry.add_social("x", "example_owner", OWNER, "github_profile", SEED)
    registry.add_website("https://owner.example", OWNER, "github_profile", SEED)
    registry.add_website("https://other.example", "person:example-other", "curated", SEED)
    links = ["https://github.com/other-project", "https://github.com/example-owner",
             "https://product.example", "https://x.com/another_person",
             "https://x.com/example_owner", "https://owner.example", "https://other.example"]
    raw = raw_with(tmp_path, {"brightdata/linkedin_profiles.json": {
        "https://www.linkedin.com/in/example-owner": {"snapshot_id": "snapshot-1", "records": [{
            "name": "Example Owner", "bio_links": [{"link": url} for url in links]}]}}})

    fill_linkedin(raw, registry, {OWNER: person}, OrgIndex({"organizations": {}}, {}))

    assert set(registry.accounts) == {"acct:linkedin/in/example-owner", "acct:x/example_owner"}
    assert set(registry.websites) == {"site:owner.example", "site:other.example"}
    assert registry.github_claims == {OWNER: {"example-owner": {"linkedin_profile"}}}
    assert registry.accounts["acct:x/example_owner"].account.link_basis == [
        "github_profile", "linkedin_profile"]
    assert registry.websites["site:owner.example"].website.link_basis == [
        "github_profile", "linkedin_profile"]
    assert registry.websites["site:other.example"].website.link_basis == ["curated"]


def test_identity_matching_rejects_conflicting_account_owners_and_handle_collisions() -> None:
    for order in (("one", "two"), ("two", "one")):
        index = PeopleIndex()
        for suffix in order:
            index.register(f"person:{suffix}", "Example Owner", {f"gh:{suffix}"})
        assert index.resolve("Example Owner", {"gh:one", "gh:two"},
                             claims_speaking=True) is None
        assert index.resolve("Example Owner", {"gh:one"},
                             claims_speaking=False) == "person:one"
        index.register("person:two", "Example Owner", {"gh:one"})
        assert index.resolve("Example Owner", {"gh:one"}, claims_speaking=True) is None

    index = PeopleIndex()
    index.register("person:one", "Example Owner", {"gh:shared"})
    index.register("person:two", "Example Owner", {"acct:x/shared"})
    assert index.resolve("Example Owner", {"acct:mastodon/shared@social.example"},
                         claims_speaking=True) is None


def test_shared_feeds_have_no_author_but_same_owner_aliases_are_allowed(tmp_path: Path) -> None:
    shared = "https://publisher.example/feed"
    own = "https://owner.example/feed"
    for reverse in (False, True):
        sites = [("https://owner.example", OWNER),
                 ("https://other.example", "person:example-other"),
                 ("https://alias.example", OWNER)]
        if reverse:
            sites.reverse()
        registry = AccountRegistry()
        for url, owner in sites:
            registry.add_website(url, owner, "github_profile", SEED)
        raw = raw_with(tmp_path, {
            "websites/homepages.json": {url: {"feeds": [shared, own] if owner == OWNER
                                              else [shared]} for url, owner in sites},
            "feeds/feeds.json": {
                shared: {"items": [{"title": "Shared article", "url": "https://publisher.example/a"}]},
                own: {"items": [{"title": "Owner article", "url": "https://owner.example/a"}]}}})

        assert writing_from_feeds(raw, registry) == {OWNER: [WritingItem(
            title="Owner article", url="https://owner.example/a", channel="blog")]}


def test_catalog_rejection_is_bounded_to_a_source_record_and_survives_renaming() -> None:
    snapshot = "rainfocus/sessions.json"
    rejected = {source_record_fingerprint(snapshot, "source-record-1")}
    bad = {"userRef": "source-record-1", "fullName": "Example Catalog Name",
           "bio": "Different Example builds compilers.",
           "photoURL": "https://images.example/different-example.png"}
    good = {"userRef": "source-record-2", "fullName": "Example Catalog Name"}
    test = {"userRef": "test-record", "testRecord": True}
    items = [{"participants": [bad, test, good]}, {"participants": [bad, good]}]

    filter_catalog_people(items, f"raw/{snapshot}", rejected)

    assert [item["participants"] for item in items] == [[good], [good]]
    # Curated name changes or missing enrichment cannot revive this source record.
    changed = [{"participants": [dict(bad, fullName="Another Example Name")]}]
    filter_catalog_people(changed, snapshot, rejected)
    assert changed[0]["participants"] == []
    independent = [{"participants": [bad, good, test]}]
    filter_catalog_people(independent, "editions/universe25/sessions.json", rejected)
    assert independent[0]["participants"] == [bad, good]
