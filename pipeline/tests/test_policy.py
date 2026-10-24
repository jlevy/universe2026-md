"""
The data policy in code: what raw caches keep, which accounts are left out, how removal
requests propagate, and who may be listed as attending.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from universe_kb.bios import drop_bios
from universe_kb.brightdata import sanitize
from universe_kb.build import curated_people, remove_people
from universe_kb.enrich import enrich_social
from universe_kb.models import Participation, Person, Session, SessionSpeaker, Source
from universe_kb.people import AccountRegistry
from universe_kb.policy import (
    Exclusions,
    forget_raw,
    prune_raw,
    sanitize_raw,
    says_attending,
)
from universe_kb.snapshot import Fetcher, Snapshot

SOURCE: dict[str, Any] = {"system": "curation", "snapshot": "curation/people.yaml"}


def test_linkedin_profiles_keep_the_owner_s_own_profile_only() -> None:
    record = {
        "id": "ada", "name": "Ada Lovelace 🏳️‍🌈", "position": "Engineer at Analytical Engines",
        "about": "I build engines. Proud mom of two. Mail ada.lovelace@example.com",
        "city": "12 Example Street, London, Greater London EC1A 1BB, UK",
        "input": {"url": "https://www.linkedin.com/in/ada"}, "memorialized_account": False,
        "influencer": True, "followers": 120, "default_avatar": True, "avatar": "https://a/b",
        "people_also_viewed": [{"name": "Charles Babbage"}],
        "experience": [{"title": "Analytical Engines", "description": "Engines.",
                        "description_html": "<p>Engines.</p>", "location": "London"}],
        "education": [{"title": "University of London", "degree": "BSc", "start_year": "1830"}],
        "volunteer_experience": [{"title": "Organizer", "cause": "Politics"},
                                 {"title": "Mentor", "cause": "Education"}],
        "organizations": [{"title": "St. Mary's Church choir"}, {"title": "IEEE"}],
        "certifications": [{"title": "CKA", "credential_id": "X1", "meta": "Credential ID X1",
                            "credential_url": "https://drive.google.com/file/d/1"}],
        "bio_links": [{"link": "https://www.instagram.com/ada"}, {"link": "https://ada.dev"}],
    }

    clean = sanitize("linkedin_profiles", record)

    assert not {"input", "memorialized_account", "influencer", "people_also_viewed",
                "default_avatar", "avatar"} & set(clean)
    # What the owner wrote about themselves stays verbatim, apart from contact details.
    assert clean["name"] == "Ada Lovelace 🏳️‍🌈"
    assert clean["about"] == "I build engines. Proud mom of two. Mail [email removed]"
    assert clean["city"] == "London, Greater London, UK"
    assert clean["experience"] == [{"title": "Analytical Engines", "description": "Engines.",
                                    "location": "London"}]
    # School years would let a reader work out someone's age.
    assert clean["education"] == [{"title": "University of London", "degree": "BSc"}]
    assert clean["volunteer_experience"] == [{"title": "Mentor", "cause": "Education"}]
    assert [o["title"] for o in clean["organizations"]] == ["IEEE"]
    assert clean["certifications"] == [{"title": "CKA", "meta": ""}]
    assert clean["bio_links"] == [{"title": None, "link": "https://ada.dev"}]
    assert sanitize("linkedin_profiles", clean) == clean
    assert sanitize("linkedin_profiles", {"error": "hidden", "error_code": "dead_page"}) == {
        "error_code": "dead_page"}


def test_x_profiles_keep_only_the_owner_s_own_posts_without_media() -> None:
    def post(author: str, text: str) -> dict[str, Any]:
        return {"post_id": "1", "post_url": f"https://twitter.com/{author}/status/1",
                "description": text, "photos": ["https://p/1.jpg"], "likes": 9}

    record = {"x_id": "42", "biography": "Builder. Husband, Dad, Rustacean, Speaker",
              "birth_date": "1815-12-10", "category_name": [], "max_number_of_posts": 100,
              "location": "London", "external_link": "https://www.tiktok.com/@ada",
              "posts": [post("42", "Shipping the engine today"),
                        post("42", "@grace agreed, see you at Universe"),
                        post("7", "Someone else's words"),
                        post("42", "RT @grace: hello"),
                        post("42", "Proud of my daughter today")]}

    clean = sanitize("x_profiles", record)

    assert not {"birth_date", "category_name", "max_number_of_posts"} & set(clean)
    assert clean["biography"] == "Builder. Husband, Dad, Rustacean, Speaker"
    assert clean["external_link"] is None
    assert [p["description"] for p in clean["posts"]] == [
        "Shipping the engine today", "@grace agreed, see you at Universe"]
    assert all(set(p) == {"post_id", "post_url", "description"} for p in clean["posts"])


def test_linkedin_companies_keep_untagged_updates_and_city_level_offices() -> None:
    record = {"name": "Acme", "company_id": "acme",
              "about": "We build. Contact: sales" + "@" + "acme.co, 200 Berkeley St, Boston",
              "employees": [{"title": "Ada Lovelace"}], "alumni_information": [{"t": 1}],
              "similar": [{"title": "Other Co"}], "affiliated": [{"title": "Acme Labs"}],
              "get_directions_url": [{"u": "x"}], "unformatted_about": "We build.",
              "formatted_locations": ["200 Berkeley St, Boston, Massachusetts 02116, US",
                                      "1 Main St, Boston, Massachusetts 02110, US"],
              "updates": [
                  {"text": "We shipped", "text_html": "We shipped", "date": "2026-10-02",
                   "time": "2h", "repost": {"tagged_users": ["grace"]}, "likes_count": 3},
                  {"text": "Welcome Ada!", "date": "2026-10-03",
                   "text_html": '<a href="https://www.linkedin.com/in/ada">Ada</a>'}]}

    clean = sanitize("linkedin_companies", record)

    assert sorted(clean) == ["about", "formatted_locations", "id", "name", "updates"]
    assert clean["about"] == "We build. Contact: [email removed], [address removed], Boston"
    assert clean["formatted_locations"] == ["Boston, Massachusetts, US"]
    assert clean["updates"] == [{"text": "We shipped", "date": "2026-10-02", "likes_count": 3}]


def test_raw_rules_strip_personal_platforms_finances_likes_and_tokens() -> None:
    owners = {"ada": {
        "__typename": "User", "login": "ada", "bio": "Compilers. Proud father of twins.",
        "company": "@acme @Latina-Dev", "location": "Seattle, WA 98101",
        "sponsoring": {"nodes": [{"login": "grace"}]},
        "starredRepositories": {"totalCount": 2, "nodes": [{"nameWithOwner": "octo/a"}]},
        "lists": {"nodes": [{"name": "Health"}]},
        "socialAccounts": {"nodes": [{"provider": "INSTAGRAM", "url": "https://instagram.com/a"},
                                     {"provider": "MASTODON", "url": "https://hachyderm.io/@a"}]},
    }, "acme": {"__typename": "Organization", "login": "acme",
                "location": "1 Main St, Boston, MA 02110"}}
    homepages = {"https://ada" + "@" + "mail.co/": {"title": "x"},
                 "https://ada.dev": {"title": "Ada", "social_links": [
                     "https://www.facebook.com/ada", "https://github.com/ada"]},
                 "https://www.skool.com/group/about": {"social_links": ["https://x.com/bo"]}}
    catalog = {"searchTimestamp": 1, "items": [{"participants": [{
        "bio": "Ada builds compilers. She lives in London with her husband.",
        "modified": "2026", "userRef": "u1",
        "attributevalues": [{"attribute": "Facebook", "value": "https://facebook.com/ada"},
                            {"attribute": "GitHub Handle", "value": "ada"}]}]}]}
    page = {"data": {"widgetConf": {"widgetToken": "t", "apiProfileToken": "p"},
                     "eventsettings": {"videoPlayerFPToken": "jwt", "title": "Universe"}}}

    owner = sanitize_raw("github/owners.json", owners)
    sites = sanitize_raw("websites/homepages.json", homepages)
    participant = sanitize_raw("rainfocus/sessions.json", catalog)["items"][0]["participants"][0]
    feeds = sanitize_raw("feeds/feeds.json", {"https://ada.dev/comments/feed/": {},
                                              "https://ada.dev/feed/": {"items": []}})

    node = owner["ada"]
    assert (node["bio"], node["company"], node["location"]) == (
        "Compilers. Proud father of twins.", "@acme @Latina-Dev", "Seattle, WA")
    assert "sponsoring" not in node and "lists" not in node
    assert node["starredRepositories"] == {"totalCount": 2}
    assert [s["provider"] for s in node["socialAccounts"]["nodes"]] == ["MASTODON"]
    assert owner["acme"]["location"] == "Boston, MA"
    assert list(sites) == ["https://ada.dev", "https://www.skool.com/group/about"]
    assert sites["https://ada.dev"]["social_links"] == ["https://github.com/ada"]
    assert sites["https://www.skool.com/group/about"]["social_links"] == []
    assert participant == {"bio": "Ada builds compilers. She lives in London with her husband.",
                           "userRef": "u1",
                           "attributevalues": [{"attribute": "GitHub Handle", "value": "ada"}]}
    assert list(feeds) == ["https://ada.dev/feed/"]
    assert sanitize_raw("rainfocus/pages/sessioncatalog.json", page) == {
        "data": {"widgetConf": {}, "eventsettings": {"title": "Universe"}}}


def test_hashtag_timelines_keep_only_attendees_who_say_so() -> None:
    def post(acct: str, text: str, **account: Any) -> dict[str, Any]:
        return {"id": "1", "url": f"https://hachyderm.io/@{acct}/1", "text": text,
                "language": "en", "tags": ["githubuniverse"],
                "account": {"acct": f"{acct}@hachyderm.io", "display_name": acct,
                            "bio": "Loves Rust", "bot": False, **account}}

    timeline = {"host": "hachyderm.io", "posts": [
        post("ada", "I'll be at #GitHubUniverse next week!"), post("ada", "Shipping today"),
        post("bo", "Watching the #GitHubUniverse keynote stream"),
        post("cy", "I'll be at #GitHubUniverse", bio="#nobot, posts are mine"),
        post("dee", "Not attending #GitHubUniverse this year, sadly"),
        post("news", "I'll be at #GitHubUniverse", bot=True)]}

    kept = sanitize_raw("mastodon/hashtags.json", {"t": timeline})["t"]["posts"]

    assert [(p["account"]["acct"], p["text"]) for p in kept] == [
        ("ada@hachyderm.io", "I'll be at #GitHubUniverse next week!"),
        ("ada@hachyderm.io", "Shipping today")]
    assert set(kept[0]) == {"id", "url", "text", "account"}
    assert "bio" not in kept[0]["account"]
    assert not says_attending("I won't be at GitHub Universe this year")



@pytest.mark.parametrize("personal_clause", [
    "I have ADHD.", "I am married.", "I am Catholic.",
])
def test_hashtag_snapshot_removes_sensitive_clauses_but_preserves_attendance(
    tmp_path: Path, personal_clause: str,
) -> None:
    quote = "I'll be at #GitHubUniverse to discuss compilers."
    post_url = "https://social.example/@example/1"
    account = {"acct": "example@social.example", "display_name": "Example", "bot": False}
    post = {"id": "1", "url": post_url, "created_at": "2026-10-24T00:00:00Z",
            "text": quote + "\n" + personal_clause, "account": account}
    snapshot = Snapshot(tmp_path / "raw")
    snapshot.save_json("mastodon/hashtags.json", {"tag": {"posts": [
        post, {**post, "id": "2", "text": personal_clause},
        {**post, "id": "3", "text": "Shipping a compiler today."},
    ]}}, url="https://social.example/api/v1/timelines/tag/githubuniverse")

    saved = snapshot.load_json("mastodon/hashtags.json")
    posts = saved["tag"]["posts"]
    assert [p["text"] for p in posts] == [quote, "Shipping a compiler today."]
    assert posts[0]["url"] == post_url
    assert posts[0]["id"] == "1"
    assert posts[0]["created_at"] == "2026-10-24T00:00:00Z"
    assert posts[0]["account"] == account
    assert says_attending(posts[0]["text"])
    assert sanitize_raw("mastodon/hashtags.json", saved) == saved


@pytest.mark.parametrize("statement", [
    "I'll be at #GitHubUniverse with my wife.",
    "I won't be attending #GitHubUniverse with my wife. I'll be at the stream.",
])
def test_hashtag_requires_attendance_proof_in_original_and_sanitized_text(
    statement: str,
) -> None:
    account = {"acct": "example@social.example", "display_name": "Example", "bot": False}
    data = {"tag": {"posts": [
        {"id": "1", "text": statement, "account": account},
        {"id": "2", "text": "Shipping a compiler today.", "account": account},
    ]}}
    assert sanitize_raw("mastodon/hashtags.json", data)["tag"]["posts"] == []


def write_raw(root: Path, files: dict[str, Any]) -> Snapshot:
    manifest = {}
    for rel, data in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
        manifest[rel] = {"url": "https://example.org/", "method": "GET",
                         "retrieved_at": "2026-10-24T00:00:00Z", "bytes": 0, "sha256": ""}
    (root / "manifest.json").write_text(json.dumps({"files": manifest}))
    return Snapshot(root)


def test_scrub_deletes_a_removed_person_s_raw_data_and_bio(tmp_path: Path) -> None:
    snapshot = write_raw(tmp_path / "raw", {
        "github/owners.json": {"ada": {"login": "ada"}, "grace": {"login": "grace"}},
        "brightdata/x_profiles.json": {"https://x.com/AdaL": {"records": []},
                                       "https://x.com/grace": {"records": []}},
        "websites/homepages.json": {"https://ada.dev": {"feeds": ["https://ada.dev/feed"]}},
        "feeds/feeds.json": {"https://ada.dev/feed": {"items": []}},
        "mastodon/hashtags.json": {"t": {"posts": [
            {"text": "I'll be at Universe", "account": {"acct": "ada@hachyderm.io"}},
            {"text": "I'll be at Universe", "account": {"acct": "bo@hachyderm.io"}}]}},
    })
    keys = {"gh:ada", "acct:x/adal", "site:ada.dev", "acct:mastodon/ada@hachyderm.io"}
    (tmp_path / "brief-bios.yaml").write_text(
        "bios:\n- person: person:ada\n  text: x\n- person: person:grace\n  text: y\n")

    exclusions = Exclusions()
    exclusions.add_keys(keys)
    report = forget_raw(snapshot, exclusions)
    snapshot.write_manifest()

    assert report == {"github/owners.json": 1, "brightdata/x_profiles.json": 1,
                      "websites/homepages.json": 1, "mastodon/hashtags.json": 1,
                      "feeds/feeds.json": 1}
    assert list(snapshot.load_json("github/owners.json")) == ["grace"]
    entry = json.loads((tmp_path / "raw/manifest.json").read_text())["files"]
    assert entry["github/owners.json"]["retrieved_at"] == "2026-10-24T00:00:00Z"
    assert drop_bios(tmp_path, {"person:ada"}) == ["person:ada"]
    assert "person:ada" not in (tmp_path / "brief-bios.yaml").read_text()


def test_prune_keeps_only_what_the_kb_uses(tmp_path: Path) -> None:
    snapshot = write_raw(tmp_path, {
        "mastodon/profiles.json": {"ada@hachyderm.io": {"bio": "x"}, "bo@skool.example": None},
        "brightdata/x_profiles.json": {
            "https://x.com/ada": {"records": [{"posts": [
                {"post_url": "https://x.com/ada/status/1", "description": "Old"},
                {"post_url": "https://x.com/ada/status/2", "description": "Shipped"}]}]},
            "https://x.com/gone": {"records": [{"error_code": "dead_page"}]}},
        "websites/homepages.json": {"https://ada.dev": {
            "feeds": ["https://ada.dev/feed"],
            "social_links": ["https://x.com/ada", "https://x.com/colleague"]}},
        "feeds/feeds.json": {"https://ada.dev/feed": {}, "https://old.example/feed": {}},
    })
    payloads: dict[str, dict[str, Any]] = {
        "acct:mastodon/ada@hachyderm.io": {}, "acct:x/ada": {},
        "site:ada.dev": {"linked_accounts": ["acct:x/ada"]},
        "profile:ada": {"person": "person:ada",
                        "recent_writing": [{"url": "https://x.com/ada/status/2"}]}}

    prune_raw(snapshot, payloads)

    assert list(snapshot.load_json("mastodon/profiles.json")) == ["ada@hachyderm.io"]
    x = snapshot.load_json("brightdata/x_profiles.json")
    assert x == {"https://x.com/ada": {"records": [{"posts": [
        {"post_url": "https://x.com/ada/status/2", "description": "Shipped"}]}]}}
    assert snapshot.load_json("websites/homepages.json")["https://ada.dev"][
        "social_links"] == ["https://x.com/ada"]
    assert list(snapshot.load_json("feeds/feeds.json")) == ["https://ada.dev/feed"]


def test_removed_people_leave_sessions_and_their_accounts(tmp_path: Path) -> None:
    keys = ("person:ada-lovelace", "person:someone-renamed", "acct:x/graceh")
    (tmp_path / "people.yaml").write_text("exclude:\n" + "".join(
        f"  - sha256: {hashlib.sha256(key.encode()).hexdigest()}\n" for key in keys))
    exclusions = Exclusions.load(tmp_path)
    source = Source(**SOURCE)
    registry = AccountRegistry()
    people = {}
    for pid, name in (("person:ada-lovelace", "Ada"), ("person:grace", "Grace"),
                      ("person:alan", "Alan")):
        people[pid] = Person(id=pid, name=name, inclusion_basis="published_by_event",
                             github_resolution="absent", sources=[source],
                             participations=[Participation(event="event:e", role="speaker",
                                                           status="confirmed")])
    registry.add_url("https://ada.dev", "person:ada-lovelace", "curated", source)
    registry.add_url("https://x.com/graceh", "person:grace", "curated", source)
    session = Session.model_construct(speakers=[
        SessionSpeaker(person=pid, role="speaker", order=i) for i, pid in enumerate(people)])

    removed = remove_people(exclusions, people, [session], registry)

    assert removed == ["person:ada-lovelace", "person:grace"]
    assert list(people) == ["person:alan"]
    assert [s.person for s in session.speakers] == ["person:alan"]
    assert registry.accounts == {} and registry.websites == {}


def test_curated_people_need_a_role_and_a_public_source(tmp_path: Path) -> None:
    def curate(entry: str) -> list[dict[str, Any]]:
        (tmp_path / "people.yaml").write_text(f"people:\n  - {entry}\n")
        return curated_people(tmp_path)

    listed = curate("{name: Ada, role: attendee, status: self_reported, evidence: "
                    "[{url: 'https://x.com/ada/status/1', quote: 'See you at Universe'}]}")
    assert listed[0]["participation"]["role"] == "attendee"
    for entry in ("{name: Ada, status: self_reported, evidence: [{url: 'https://x.com/a/1'}]}",
                  "{name: Ada, role: attendee, status: candidate, "
                  "evidence: [{url: 'https://x.com/a/1'}]}",
                  "{name: Ada, role: attendee, status: self_reported, "
                  "evidence: [{quote: 'a friend said so'}]}"):
        with pytest.raises(ValueError):
            curate(entry)


def test_fingerprint_exclusions_match_without_publishing_identity(tmp_path: Path) -> None:
    digest = hashlib.sha256(b"acct:x/graceh").hexdigest()
    (tmp_path / "people.yaml").write_text(f"exclude:\n  - sha256: {digest}\n")
    exclusions = Exclusions.load(tmp_path)
    assert exclusions.covers("person:renamed", {"acct:x/graceh"})
    assert not exclusions.covers("person:other", {"acct:x/other"})


def test_exclusions_reject_identifying_or_malformed_entries(tmp_path: Path) -> None:
    for value in ("person: example-person", "sha256: invalid", "sha256: null", "sha256: 12"):
        (tmp_path / "people.yaml").write_text(f"exclude:\n  - {value}\n")
        with pytest.raises(ValueError, match="fingerprint"):
            Exclusions.load(tmp_path)


def test_collection_excludes_fingerprints_from_kb_links_and_timeline_posts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    snapshot = write_raw(tmp_path / "raw", {
        "rainfocus/sessions.json": {"items": []},
        "websites/homepages.json": {"https://shared.example.org": {
            "rel_me": ["https://bsky.app/profile/ada.example.org"]}},
    })
    curation = tmp_path / "curation"
    curation.mkdir()
    keys = ("site:ada.example.org", "acct:bluesky/ada.example.org",
            "acct:mastodon/ada@hachyderm.io")
    (curation / "people.yaml").write_text("exclude:\n" + "".join(
        f"  - sha256: {hashlib.sha256(key.encode()).hexdigest()}\n" for key in keys))
    kb = tmp_path / "kb"
    (kb / "websites").mkdir(parents=True)
    (kb / "websites/ada.yaml").write_text(
        "website: {owner: 'person:ada', url: 'https://ada.example.org'}\n")
    for platform, handle in (("bluesky", "ada.example.org"),
                             ("mastodon", "ada@hachyderm.io")):
        (kb / "accounts" / platform).mkdir(parents=True)
        (kb / "accounts" / platform / "ada.yaml").write_text(
            f"social_account: {{owner: 'person:ada', handle: '{handle}'}}\n")

    def unexpected_fetch(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("Excluded accounts must never be fetched")

    def timeline(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {"posts": [{"account": {"acct": acct}, "text": "I'll be at Universe"}
                          for acct in ("ada@hachyderm.io", "grace@hachyderm.io")]}

    monkeypatch.setattr(Fetcher, "request", unexpected_fetch)
    monkeypatch.setattr(Fetcher, "fetch", unexpected_fetch)
    monkeypatch.setattr("universe_kb.enrich.hashtag_posts", timeline)
    enrich_social(snapshot, Fetcher(), curation, kb,
                  steps=("websites", "bluesky", "mastodon", "hashtags"))
    assert snapshot.load_json("bluesky/profiles.json") == {}
    assert snapshot.load_json("mastodon/profiles.json") == {}
    for posts in snapshot.load_json("mastodon/hashtags.json").values():
        assert [p["account"]["acct"] for p in posts["posts"]] == ["grace@hachyderm.io"]


def test_personal_music_readme_blocks_are_not_published() -> None:
    text = (
        "I build compilers.\n\n"
        "[![Listening](https://spotify-recently-played-readme.vercel.app/api?user=private)]"
        "(https://open.spotify.com/user/private)\n\n"
        "Projects: https://github.com/ada/engine"
    )
    owners = {"ada": {"__typename": "User", "userReadme": {"object": {"text": text}}}}

    cleaned = sanitize_raw("github/owners.json", owners)["ada"]["userReadme"]["object"]["text"]

    assert "spotify" not in cleaned and "private" not in cleaned
    assert cleaned == "I build compilers.\n\nProjects: https://github.com/ada/engine"


def test_readme_filter_applies_existing_personal_platform_policy_and_tolerates_bad_links() -> None:
    from universe_kb.policy import professional_readme

    for url in ("https://instagram.com/example", "https://www.facebook.com/example"):
        assert professional_readme("I build tools.\n\nPersonal: " + url) == "I build tools."
    assert professional_readme("Project: https://[broken") == "Project: https://[broken"
