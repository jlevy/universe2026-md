"""
Enrichment snapshots applied to people and organizations: LinkedIn, X and Mastodon
profile details, website feeds, X posts, Mastodon hashtag timelines and organization
descriptions. Each test writes a small raw snapshot and reads it through the real
`RawData`, so provenance comes from the same `source` the build uses.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from universe_kb.build import OrgIndex, OrgRecord, RawData, adopt_github_claims
from universe_kb.models import (
    Activity,
    Affiliation,
    Credential,
    EducationEntry,
    Evidence,
    OrgDescription,
    Participation,
    Person,
    Source,
    SourceSystem,
    Sponsorship,
    WritingItem,
)
from universe_kb.people import AccountRegistry
from universe_kb.profile_sources import (
    fill_linkedin,
    fill_mastodon,
    fill_x,
    hashtag_records,
    headline_title,
    organization_details,
    patent_url,
    writing_from_feeds,
    x_posts,
)

RETRIEVED = "2026-10-24T08:52:15Z"
SEED = Source(system="curation", snapshot="curation/test.yaml")
ADA = "person:ada-lovelace"
ADA_LINKEDIN = "https://www.linkedin.com/in/ada-lovelace"
DETAIL_FIELDS = {"display_name", "headline", "bio", "location", "website", "followers",
                 "following", "connections", "posts_count", "verified", "avatar_url",
                 "banner_url", "created_at", "details_fetched"}


def raw_with(root: Path, files: dict[str, Any]) -> RawData:
    """A raw directory holding `files` as JSON, with the manifest entries `source` reads."""
    for rel_path, data in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
    return RawData(root, {rel_path: {"url": f"https://snapshots.test/{rel_path}",
                                     "retrieved_at": RETRIEVED} for rel_path in files})


def snapshot_source(rel_path: str, record_id: str, url: str, system: SourceSystem) -> Source:
    return Source(system=system, url=url, record_id=record_id, retrieved_at=RETRIEVED,
                  snapshot=f"raw/{rel_path}")


def person(person_id: str, name: str) -> Person:
    return Person(
        id=person_id, name=name, inclusion_basis="curated", github_resolution="absent",
        sources=[SEED],
        participations=[Participation(event="event:github-universe-2026", role="speaker",
                                      status="confirmed")])


def test_fill_linkedin_details_affiliation_company_account_and_sections(tmp_path: Path) -> None:
    people = {p.id: p for p in (person(ADA, "Ada Lovelace"), person("person:alan", "Alan Turing"),
                                person("person:joan", "Joan Clarke"),
                                person("person:grace", "Grace Hopper"))}
    registry = AccountRegistry()
    for handle, owner in (("in/ada-lovelace", ADA), ("in/alan", "person:alan"),
                          ("in/joan", "person:joan"), ("in/grace", "person:grace")):
        registry.add_social("linkedin", handle, owner, "event_listing", SEED)
    orgs = OrgIndex({"organizations": {}}, {})
    raw = raw_with(tmp_path, {"brightdata/linkedin_profiles.json": {
        # Input URLs differ from the account URL in case and trailing slash.
        "https://www.linkedin.com/in/Ada-Lovelace/": {"snapshot_id": "sd_1", "records": [{
            "timestamp": "2026-10-24T08:11:35.417Z",
            "name": "Ada  Lovelace", "position": "Principal Engineer",
            "about": "  Writes compilers.\n", "location": None, "city": "London, England",
            "followers": 1200, "connections": 500,
            "default_avatar": True, "avatar": "https://static.licdn.com/default.png",
            "banner_image": "https://media.licdn.com/banner.jpg",
            "current_company": {"name": "Analytical Engines, Inc.",
                                "company_id": "analytical-engines"},
            "education": [None, {"title": "University of London", "degree": "BSc",
                                 "field": "Mathematics", "start_year": "1832",
                                 "end_year": "1835"},
                          {"start_year": "1830"}],
            "honors_and_awards": [{"title": "Lovelace Medal", "publication": "BCS",
                                   "date": "Jan 1998"}, {"title": "  "}],
            "certifications": [None, {"title": "Engine Operator", "subtitle": "-",
                                      "meta": "Issued Feb 1840"}],
            "languages": [{"title": "English", "subtitle": "Native"}, None, {"title": "French"}],
            "volunteer_experience": [{"title": "Mentor", "subtitle": "Girls Who Code",
                                      "cause": "Education", "start_date": "Jan 2020"}],
            "projects": [{"title": "Note G", "start_date": "1842",
                          "description": "First published program."}],
            "posts": [{"title": "On the Analytical Engine", "created_at": "2026-09-01",
                       "link": "https://www.linkedin.com/pulse/analytical-engine",
                       "attribution": "Notes on a machine."},
                      {"title": "A post without a link"}],
        }]},
        "https://www.linkedin.com/in/alan": {"snapshot_id": "sd_1", "records": [{
            "name": "Alan Turing", "default_avatar": False,
            "avatar": "https://media.licdn.com/alan.jpg",
            # LinkedIn's numeric company IDs are not page handles.
            "current_company": {"name": "Bletchley Park", "company_id": "1234567"}}]},
        "https://www.linkedin.com/in/joan": {"snapshot_id": "sd_1", "records": [{
            "name": "Joan Clarke", "current_company_name": "Freelance"}]},
        "https://www.linkedin.com/in/grace": {"snapshot_id": "sd_1", "records": [{
            "error": "The profile is hidden or private.", "error_code": "dead_page"}]},
    }})

    extras = fill_linkedin(raw, registry, people, orgs)

    source = snapshot_source("brightdata/linkedin_profiles.json", "sd_1", ADA_LINKEDIN,
                             "brightdata")
    evidence = Evidence(url=ADA_LINKEDIN, observed_at="2026-10-24T08:11:35Z")
    ada = registry.accounts["acct:linkedin/in/ada-lovelace"].account
    assert ada.model_dump(include=DETAIL_FIELDS, exclude_none=True) == {
        "display_name": "Ada Lovelace", "headline": "Principal Engineer",
        "bio": "Writes compilers.", "location": "London, England", "followers": 1200,
        "connections": 500, "banner_url": "https://media.licdn.com/banner.jpg",
        "details_fetched": True}
    assert ada.sources == [SEED, source]
    assert registry.accounts["acct:linkedin/in/alan"].account.avatar_url == (
        "https://media.licdn.com/alan.jpg")

    assert people[ADA].affiliations == [Affiliation(
        organization="org:analytical-engines", title="Principal Engineer", current=True,
        basis="linkedin", label="Analytical Engines, Inc.", evidence=[evidence])]
    company = registry.accounts["acct:linkedin/company/analytical-engines"].account
    assert (company.owner, company.link_basis, company.url) == (
        "org:analytical-engines", ["linkedin_profile"],
        "https://www.linkedin.com/company/analytical-engines")
    assert [a.organization for a in people["person:alan"].affiliations] == ["org:bletchley-park"]
    assert registry.owned_by("org:bletchley-park") == ([], [])
    assert people["person:joan"].affiliations == []

    found = extras[ADA]
    assert found.education == [EducationEntry(
        school="University of London", degree="BSc", field_of_study="Mathematics",
        start_year="1832", end_year="1835", evidence=evidence)]
    assert found.credentials == [
        Credential(kind="honor", title="Lovelace Medal", issuer="BCS", date="Jan 1998",
                   evidence=evidence),
        Credential(kind="certification", title="Engine Operator", issuer=None,
                   date="Feb 1840", evidence=evidence)]
    assert found.spoken_languages == ["English", "French"]
    assert found.activities == [
        Activity(kind="volunteering", title="Mentor",
                 detail="Girls Who Code · Education · Jan 2020", evidence=evidence),
        Activity(kind="project", title="Note G", detail="First published program. · 1842",
                 evidence=evidence)]
    assert found.writing == [WritingItem(
        title="On the Analytical Engine", url="https://www.linkedin.com/pulse/analytical-engine",
        published="2026-09-01", channel="linkedin", summary="Notes on a machine.")]

    grace = registry.accounts["acct:linkedin/in/grace"].account
    assert (grace.details_fetched, grace.sources) == (False, [SEED])
    assert "person:grace" not in extras
    assert people["person:grace"].affiliations == []


def test_fill_linkedin_drops_placeholder_activity_details(tmp_path: Path) -> None:
    people = {ADA: person(ADA, "Ada Lovelace")}
    registry = AccountRegistry()
    registry.add_social("linkedin", "in/ada-lovelace", ADA, "event_listing", SEED)
    raw = raw_with(tmp_path, {"brightdata/linkedin_profiles.json": {
        ADA_LINKEDIN: {"snapshot_id": "sd_1", "records": [{
            "courses": [{"subtitle": "-", "title": "CCNP - ROUTE"}]}]}}})

    extras = fill_linkedin(raw, registry, people, OrgIndex({"organizations": {}}, {}))

    assert [(a.title, a.detail) for a in extras[ADA].activities] == [("CCNP - ROUTE", None)]


def test_fill_x_details_and_profile_website(tmp_path: Path) -> None:
    registry = AccountRegistry()
    registry.add_social("x", "AdaL", ADA, "event_listing", SEED)
    account = registry.accounts["acct:x/adal"].account
    account.display_name = "Ada Lovelace"
    raw = raw_with(tmp_path, {"brightdata/x_profiles.json": {
        "https://x.com/adal": {"snapshot_id": "sd_x", "records": [
            {"warning_code": "partial", "name": "Not Ada"},
            {"name": None, "biography": " Compilers and engines. ", "location": "London",
             "external_link": "https://ada.dev/", "followers": 10, "following": 5,
             "posts_count": 42, "is_verified": False,
             "profile_image_link": "https://pbs.twimg.com/ada.jpg", "banner_image": None,
             "date_joined": "2012-08-15T00:38:36.000Z"}]}}})

    fill_x(raw, registry)

    source = snapshot_source("brightdata/x_profiles.json", "sd_x", "https://x.com/AdaL",
                             "brightdata")
    assert account.model_dump(include=DETAIL_FIELDS, exclude_none=True) == {
        "display_name": "Ada Lovelace", "bio": "Compilers and engines.", "location": "London",
        "website": "https://ada.dev/", "followers": 10, "following": 5, "posts_count": 42,
        "verified": False, "avatar_url": "https://pbs.twimg.com/ada.jpg",
        "created_at": "2012-08-15T00:38:36Z", "details_fetched": True}
    assert account.sources == [SEED, source]
    site = registry.websites["site:ada.dev"].website
    assert (site.owner, site.link_basis, site.sources) == (ADA, ["x_profile"], [source])


def test_fill_mastodon_links_only_verified_fields(tmp_path: Path) -> None:
    registry = AccountRegistry()
    registry.add_social("mastodon", "AdaEngine@infosec.exchange", "person:ada-e",
                        "github_profile", SEED)
    raw = raw_with(tmp_path, {"mastodon/profiles.json": {"adaengine@infosec.exchange": {
        "url": "https://infosec.exchange/@adaengine", "display_name": "Ada",
        "bio": "Parentheses enthusiast.", "followers": 854, "following": 298, "statuses": 2,
        "created_at": "2022-11-04T00:00:00Z", "avatar": "https://media.infosec.exchange/a.jpeg",
        "fields": [
            {"name": "Rants", "url": "https://adaengine.dev",
             "verified_at": "2022-11-04T17:15:34Z"},
            {"name": "Old blog", "url": "https://old.example", "verified_at": None},
            # GitHub accounts come from GitHub's own data, never from a profile link.
            {"name": "Code", "url": "https://github.com/adaengine",
             "verified_at": "2024-09-06T20:18:57Z"},
            {"name": "Pronouns", "value": "they/them", "verified_at": None}]}}})

    fill_mastodon(raw, registry)

    account = registry.accounts["acct:mastodon/adaengine@infosec.exchange"].account
    assert account.model_dump(include=DETAIL_FIELDS, exclude_none=True) == {
        "display_name": "Ada", "bio": "Parentheses enthusiast.", "followers": 854,
        "following": 298, "posts_count": 2, "created_at": "2022-11-04T00:00:00Z",
        "avatar_url": "https://media.infosec.exchange/a.jpeg", "details_fetched": True}
    source = snapshot_source("mastodon/profiles.json", "AdaEngine@infosec.exchange",
                             "https://infosec.exchange/@adaengine", "mastodon")
    assert account.sources == [SEED, source]
    assert list(registry.accounts) == ["acct:mastodon/adaengine@infosec.exchange"]
    assert list(registry.websites) == ["site:adaengine.dev"]
    site = registry.websites["site:adaengine.dev"].website
    assert (site.owner, site.link_basis) == ("person:ada-e", ["mastodon_verified"])


def feed_files(feeds: list[str], results: dict[str, Any]) -> dict[str, Any]:
    return {"websites/homepages.json": {
                "http://ada.dev": {"feeds": feeds},
                "https://stranger.example": {"feeds": ["https://stranger.example/feed"]}},
            "feeds/feeds.json": {
                **results,
                "https://stranger.example/feed": {"items": [
                    {"title": "Not Ada's", "url": "https://stranger.example/post"}]}}}


def test_writing_from_feeds_reaches_the_website_owner(tmp_path: Path) -> None:
    registry = AccountRegistry()
    registry.add_website("https://ada.dev", ADA, "github_profile", SEED)
    raw = raw_with(tmp_path, feed_files(
        ["https://ada.dev/feed.xml", "https://ada.dev/broken.xml"],
        {"https://ada.dev/feed.xml": {"error": None, "items": [
            {"title": " Notes  on G ", "url": "https://ada.dev/notes-on-g",
             "published": "2026-09-01T00:00:00Z"},
            {"title": "", "url": "https://ada.dev/untitled"},
            {"title": "Relative link", "url": "/relative"}]},
         "https://ada.dev/broken.xml": {"error": "HTTP 500", "items": [
             {"title": "Stale", "url": "https://ada.dev/stale"}]}}))

    writing = writing_from_feeds(raw, registry)

    assert writing == {ADA: [WritingItem(title="Notes on G", url="https://ada.dev/notes-on-g",
                                         published="2026-09-01T00:00:00Z", channel="blog")]}


def test_writing_from_feeds_skips_comment_feeds(tmp_path: Path) -> None:
    registry = AccountRegistry()
    registry.add_website("https://ada.dev", ADA, "github_profile", SEED)
    raw = raw_with(tmp_path, feed_files(
        ["https://ada.dev/feed/", "https://ada.dev/comments/feed/",
         "https://ada.dev/?feed=comments-rss2"],
        {"https://ada.dev/feed/": {"items": [
            {"title": "Notes on G", "url": "https://ada.dev/notes-on-g"}]},
         "https://ada.dev/comments/feed/": {"items": [
             {"title": "Comment on Notes on G by Charles Babbage",
              "url": "https://ada.dev/notes-on-g/#comment-1"}]},
         "https://ada.dev/?feed=comments-rss2": {"items": [
             {"title": "Comment on Notes on G by Mary Somerville",
              "url": "https://ada.dev/notes-on-g/#comment-2"}]}}))

    writing = writing_from_feeds(raw, registry)

    assert [item.title for item in writing[ADA]] == ["Notes on G"]


def test_x_posts_writing_is_original_posts_and_evidence_is_this_years_universe(
        tmp_path: Path) -> None:
    registry = AccountRegistry()
    registry.add_social("x", "AdaL", ADA, "event_listing", SEED)

    def post(day: str, text: str, url: str | None) -> dict[str, Any]:
        return {"date_posted": f"{day}T10:00:00.000Z", "description": text, "post_url": url}

    posts = [
        post("2025-10-30", "Loved GitHub Universe 2025!", "https://x.com/AdaL/status/1"),
        post("2026-10-20", "Speaking at GitHub Universe next week.", "https://x.com/AdaL/status/2"),
        post("2026-07-01", "Shipping a new compiler.", "https://x.com/AdaL/status/3"),
        post("2026-10-21", "@grace See you at #GitHubUniverse", "https://x.com/AdaL/status/4"),
        post("2026-09-01", "RT @github: New release notes", "https://x.com/AdaL/status/5"),
        post("2026-10-22", "#GitHubUniverse photo without a link", None),
        post("2026-10-23", "   ", "https://x.com/AdaL/status/7"),
    ]
    raw = raw_with(tmp_path, {"brightdata/x_profiles.json": {
        "https://x.com/AdaL": {"snapshot_id": "sd_x", "records": [{"posts": posts}]}}})

    writing, universe = x_posts(raw, registry)

    # Newest first; replies and reposts are not the person's own writing.
    assert [(w.title, w.published) for w in writing[ADA]] == [
        ("Speaking at GitHub Universe next week.", "2026-10-20T10:00:00Z"),
        ("Shipping a new compiler.", "2026-07-01T10:00:00Z"),
        ("Loved GitHub Universe 2025!", "2025-10-30T10:00:00Z")]
    assert {w.channel for w in writing[ADA]} == {"x"}
    # A reply about this year's event is still evidence; last year's post is not.
    assert universe == {ADA: [
        Evidence(url="https://x.com/AdaL/status/4", quote="@grace See you at #GitHubUniverse",
                 observed_at="2026-10-21T10:00:00Z"),
        Evidence(url="https://x.com/AdaL/status/2",
                 quote="Speaking at GitHub Universe next week.",
                 observed_at="2026-10-20T10:00:00Z")]}


def test_hashtag_records_skip_bots_clean_names_and_rate_attendance(tmp_path: Path) -> None:
    def post(url: str, acct: str, display_name: str, text: str, *, bot: bool = False
             ) -> dict[str, Any]:
        return {"url": url, "created_at": "2026-10-16T14:01:57Z", "text": text,
                "account": {"acct": acct, "display_name": display_name, "bot": bot,
                            "bio": f"Bio of {acct}"}}

    jesse = post("https://hachyderm.io/@gracehopper/1", "gracehopper@hachyderm.io",
                 "gracehopper :verified:", "With #GitHubUniverse around the corner, lots ship!")
    raw = raw_with(tmp_path, {"mastodon/hashtags.json": {
        "mastodon.social#GitHubUniverse": {"posts": [
            jesse,
            post("https://botsin.space/@feed/1", "feed@botsin.space", "Feed",
                 "I'll be at #GitHubUniverse", bot=True),
            post("https://hachyderm.io/@ada/2", "Ada@Hachyderm.io",
                 ":python: Ada :verified:  Lovelace", "I'll be at #GitHubUniverse next week"),
            post("https://x.social/@grace/3", "grace@x.social", ":verified:",
                 "Watching the #GitHubUniverse keynote stream"),
        ]},
        # The same post can appear on several servers' timelines.
        "hachyderm.io#GitHubUniverse": {"posts": [
            jesse,
            post("https://hachyderm.io/@gracehopper/4", "gracehopper@hachyderm.io",
                 "gracehopper", "Great #GitHubUniverse recap"),
            post("https://x.social/@grace/5", "grace@x.social", ":verified:",
                 "Heading to #GitHubUniverse tomorrow"),
        ]},
    }})

    records = hashtag_records(raw)

    # Tagged posts that never say the poster will attend add no one (gracehopper).
    assert [(r["accounts"]["mastodon"], r["name"], r["participation"]["status"],
             len(r["participation"]["evidence"])) for r in records] == [
        ("ada@hachyderm.io", "Ada Lovelace", "self_reported", 1),
        # A display name of only emoji falls back to the user name; a later post saying
        # they will be there counts, with both posts as evidence.
        ("grace@x.social", "grace", "self_reported", 2)]
    # The poster's untrusted profile text is not carried over as a bio.
    assert records[0] == {
        "source": "mastodon_hashtag", "snapshot": "mastodon/hashtags.json",
        "record_id": "https://hachyderm.io/@ada/2", "name": "Ada Lovelace",
        "accounts": {"mastodon": "ada@hachyderm.io"},
        "participation": {"role": "attendee", "status": "self_reported", "evidence": [
            {"url": "https://hachyderm.io/@ada/2", "quote": "I'll be at #GitHubUniverse next week",
             "observed_at": "2026-10-16T14:01:57Z"}]},
        "interests": [], "inclusion_basis": "public_self_report"}


def test_organization_details_prefer_linkedin_then_listing_github_website(
        tmp_path: Path) -> None:
    registry = AccountRegistry()
    registry.add_social("linkedin", "company/acme", "org:acme", "linkedin_profile", SEED)
    records = {
        "acme": OrgRecord(key="acme", name="Acme", website="https://acme.example",
                          github_login="Acme", sponsorship=Sponsorship(
                              tier="gold", summary="Gold sponsor Acme.", exhibitor_id="e1")),
        "globex": OrgRecord(key="globex", name="Globex", website="https://globex.example",
                            github_login="globex", sponsorship=Sponsorship(
                                tier="silver", summary="Globex sells.", exhibitor_id="e2")),
        "initech": OrgRecord(key="initech", name="Initech", website="https://initech.example"),
    }
    # Globex's GitHub description repeats its sponsor listing, which is kept once.
    owners = {"acme": {"description": "Rockets and anvils."},
              "globex": {"description": "Globex sells."}}
    raw = raw_with(tmp_path, {
        "brightdata/linkedin_companies.json": {"https://www.linkedin.com/company/acme/": {
            "snapshot_id": "sd_c", "records": [{
                "name": "Acme", "about": " Acme builds rockets. ", "slogan": "To the moon",
                "industries": ["Aerospace", "Software"], "company_size": "51-200 employees",
                "headquarters": "Phoenix, AZ", "founded": 1949, "specialties": "rockets, anvils",
                "logo": "https://media.licdn.com/acme.png", "image": "https://media.licdn.com/b.png",
                "followers": 900, "website": "https://acme.example"}]}},
        "websites/org-homepages.json": {
            "https://acme.example": {"status": 200, "description": "Acme homepage.",
                                     "og": {"image": "https://acme.example/og.png"},
                                     "final_url": "https://acme.example/"},
            "https://globex.example": {"status": 200, "description": "Globex homepage.",
                                       "og": {"image": "https://globex.example/og.png"}},
            "https://initech.example": {"status": 503, "description": "Service unavailable",
                                        "og": {"image": "https://initech.example/og.png"}}},
    })

    details = organization_details(raw, records, owners, registry)

    acme = details["org:acme"]
    assert [(d.basis, d.text) for d in acme.descriptions] == [
        ("linkedin", "Acme builds rockets."), ("sponsor_listing", "Gold sponsor Acme."),
        ("github", "Rockets and anvils."), ("website", "Acme homepage.")]
    assert (acme.tagline, acme.industry, acme.size, acme.headquarters, acme.founded,
            acme.specialties, acme.logo_url) == (
        "To the moon", "Aerospace, Software", "LinkedIn size range: 51-200 employees",
        "Phoenix, AZ", "1949",
        ["rockets", "anvils"], "https://media.licdn.com/acme.png")
    company = snapshot_source("brightdata/linkedin_companies.json", "sd_c",
                              "https://www.linkedin.com/company/acme", "brightdata")
    homepage = snapshot_source("websites/org-homepages.json", "https://acme.example",
                               "https://acme.example/", "website")
    assert acme.sources == [company, homepage]
    account = registry.accounts["acct:linkedin/company/acme"].account
    assert account.model_dump(include=DETAIL_FIELDS, exclude_none=True) == {
        "display_name": "Acme", "bio": "Acme builds rockets.", "followers": 900,
        "website": "https://acme.example", "avatar_url": "https://media.licdn.com/acme.png",
        "details_fetched": True}

    globex = details["org:globex"]
    assert globex.descriptions == [
        OrgDescription(text="Globex sells.", basis="sponsor_listing"),
        OrgDescription(text="Globex homepage.", basis="website")]
    assert globex.logo_url == "https://globex.example/og.png"
    initech = details["org:initech"]
    assert (initech.descriptions, initech.logo_url, initech.sources) == ([], None, [])


def test_headline_title_keeps_the_job_title_part() -> None:
    assert headline_title("Senior Software Engineer @GitHub | Deinfluencer | Career") == (
        "Senior Software Engineer")
    assert headline_title("Staff Engineer at Stripe • Speaker") == "Staff Engineer"
    assert headline_title("Principal Engineer") == "Principal Engineer"
    assert headline_title(None) is None


def test_github_claims_from_own_profiles_are_adopted_when_the_listing_had_none(
        tmp_path: Path) -> None:
    people = {p.id: p for p in (person(ADA, "Ada Lovelace"), person("person:alan", "Alan Turing"))}
    people["person:alan"].github = "gh:alan-listed"
    registry = AccountRegistry()
    registry.add_url("https://github.com/AdaL", ADA, "linkedin_profile", SEED)
    registry.add_url("https://github.com/AdaL", ADA, "x_profile", SEED)
    registry.add_url("https://github.com/analytical-engine", ADA, "x_profile", SEED)
    registry.add_url("https://github.com/alan-other", "person:alan", "x_profile", SEED)
    assert registry.github_claims[ADA] == {"adal": {"linkedin_profile", "x_profile"},
                                           "analytical-engine": {"x_profile"}}
    owners = {"adal": {"__typename": "User", "login": "AdaL", "name": "Ada Lovelace"},
              "analytical-engine": {"__typename": "Organization", "login": "analytical-engine"},
              "alan-other": {"__typename": "User", "login": "alan-other", "name": "Alan"}}
    raw = raw_with(tmp_path, {"github/owners.json": owners})

    adopted = adopt_github_claims(raw, people, owners, registry)

    # The best-corroborated user account; organizations and listed handles are kept apart.
    assert list(adopted) == [ADA]
    assert (people[ADA].github, people[ADA].github_resolution, people[ADA].github_match) == (
        "gh:adal", "resolved", "name")
    assert people["person:alan"].github == "gh:alan-listed"


def test_patent_url_links_granted_numbers_only() -> None:
    assert patent_url("US 9286046") == "https://patents.google.com/patent/US9286046"
    assert patent_url("US 11,234,567") == "https://patents.google.com/patent/US11234567"
    assert patent_url("EP 1234567 B1") == "https://patents.google.com/patent/EP1234567B1"
    # An application serial, not a granted patent.
    assert patent_url("US 18930687") is None
    assert patent_url(None) is None


def test_fill_linkedin_publications_and_patents(tmp_path: Path) -> None:
    people = {ADA: person(ADA, "Ada Lovelace")}
    registry = AccountRegistry()
    registry.add_social("linkedin", "in/ada-lovelace", ADA, "event_listing", SEED)
    raw = raw_with(tmp_path, {"brightdata/linkedin_profiles.json": {
        ADA_LINKEDIN: {"snapshot_id": "sd_1", "records": [{
            "publications": [{"title": "Notes on the Analytical Engine", "subtitle":
                              "Scientific Memoirs", "date": "1843", "description": " Note G. "},
                             None, {"subtitle": "untitled"}],
            "patents": [{"title": "Engine", "patents_id": "US 9286046",
                         "date_issued": "Mar 15, 2016"}]}]}}})

    extras = fill_linkedin(raw, registry, people, OrgIndex({"organizations": {}}, {}))[ADA]

    assert [(p.title, p.venue, p.date, p.description) for p in extras.publications] == [
        ("Notes on the Analytical Engine", "Scientific Memoirs", "1843", "Note G.")]
    assert [(p.title, p.number, p.date, p.url) for p in extras.patents] == [
        ("Engine", "US 9286046", "Mar 15, 2016", "https://patents.google.com/patent/US9286046")]
