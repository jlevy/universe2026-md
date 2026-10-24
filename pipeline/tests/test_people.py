"""
Identity across sources: account and website IDs, the registry that gives each one a
single owner and leaves out personal platforms, merging people by account or (for
speakers only) by name, and recognitions read from bios.
"""

from __future__ import annotations

from universe_kb.models import Source
from universe_kb.people import (
    AccountRegistry,
    PeopleIndex,
    identity_keys,
    recognition_claims,
    social_account_id,
    website_id,
)

EVENT_SOURCE = Source(system="rainfocus", record_id="u1", snapshot="raw/rainfocus/sessions.json")
GITHUB_SOURCE = Source(system="github", record_id="ada", snapshot="raw/github/owners.json")


def test_social_account_ids_are_lowercase_platform_paths() -> None:
    assert social_account_id("x", "AdaLovelace") == "acct:x/adalovelace"
    assert social_account_id("linkedin", "in/Grace-Hopper") == "acct:linkedin/in/grace-hopper"
    assert social_account_id("bluesky", "alanturing.dev") == "acct:bluesky/alanturing.dev"
    assert social_account_id("youtube", "@GraceHopper") == "acct:youtube/@gracehopper"
    assert social_account_id("mastodon", "katherinej@mastodon.social") == (
        "acct:mastodon/katherinej@mastodon.social")


def test_website_id_ignores_scheme_www_case_and_trailing_slash() -> None:
    assert {website_id(url) for url in ("https://www.Example.com/", "http://example.com",
                                        "https://example.com")} == {"site:example.com"}
    assert website_id("https://www.example.com/Blog/") == "site:example.com/blog"


def test_registry_merges_sightings_and_keeps_the_first_owner() -> None:
    registry = AccountRegistry()

    first = registry.add_social("x", "AdaLovelace", "person:ada-lovelace", "event_listing",
                                EVENT_SOURCE)
    again = registry.add_social("x", "adalovelace", "person:ada-lovelace", "github_profile",
                                GITHUB_SOURCE)
    rival = registry.add_social("x", "adalovelace", "org:analytical-engines", "github_profile",
                                GITHUB_SOURCE)

    assert first == again == "acct:x/adalovelace"
    assert rival is None
    account = registry.accounts["acct:x/adalovelace"].account
    assert (account.owner, account.handle, account.url) == (
        "person:ada-lovelace", "AdaLovelace", "https://x.com/AdaLovelace")
    assert account.link_basis == ["event_listing", "github_profile"]
    assert account.sources == [EVENT_SOURCE, GITHUB_SOURCE]
    assert registry.conflicts == [
        "acct:x/adalovelace claimed by person:ada-lovelace and org:analytical-engines"]
    assert registry.owned_by("org:analytical-engines") == ([], [])


def test_registry_routes_urls_to_accounts_or_websites() -> None:
    registry = AccountRegistry()
    ada = "person:ada"

    assert registry.add_url("https://www.linkedin.com/in/ada-lovelace/", ada, "event_listing",
                            EVENT_SOURCE) == "acct:linkedin/in/ada-lovelace"
    assert registry.add_url("ada.dev/", ada, "github_profile", GITHUB_SOURCE) == "site:ada.dev"
    assert registry.add_url("https://ada.medium.com", ada, "github_profile",
                            GITHUB_SOURCE) == "site:ada.medium.com"
    assert registry.add_website("https://kody.codes", "org:kody-codes", "github_profile",
                                GITHUB_SOURCE) == "site:kody.codes"
    # GitHub accounts are modeled on their own, and an employer's domain is not her site.
    assert registry.add_url("https://github.com/ada", ada, "github_profile", GITHUB_SOURCE) is None
    assert registry.add_website("https://learn.microsoft.com/en-us/", ada, "github_profile",
                                GITHUB_SOURCE) is None
    assert registry.add_website("http://www.ada.dev", "person:bob", "curated",
                                GITHUB_SOURCE) is None

    assert registry.owned_by(ada) == (["acct:linkedin/in/ada-lovelace"],
                                      ["site:ada.dev", "site:ada.medium.com"])
    linkedin = registry.accounts["acct:linkedin/in/ada-lovelace"].account
    assert (linkedin.platform, linkedin.handle, linkedin.url) == (
        "linkedin", "in/ada-lovelace", "https://www.linkedin.com/in/ada-lovelace")
    assert [(r.website.url, r.website.kind) for r in registry.websites.values()] == [
        ("https://ada.dev/", "personal"), ("https://ada.medium.com", "blog"),
        ("https://kody.codes", "company")]
    assert registry.conflicts == ["site:ada.dev claimed by person:ada and person:bob"]


def test_identity_keys_agree_across_handle_and_url_spellings() -> None:
    from_urls = identity_keys({
        "x": "https://twitter.com/AdaLovelace",
        "linkedin": "https://www.linkedin.com/in/gracehopperc/",
        "bluesky": "https://bsky.app/profile/alanturing.dev",
        "mastodon": "https://bolha.us/@gracehopper",
        "website": "https://www.adalovelace.com/",
        "github": "AdaLovelace",
    })
    from_handles = identity_keys({
        "x": "@adalovelace", "linkedin": "in/gracehopperc", "bluesky": "@Alanturing.dev",
        "mastodon": "gracehopper@bolha.us", "website": "adalovelace.com", "github": "adalovelace",
        "youtube": None,
    })

    assert from_urls == from_handles == {
        "acct:x/adalovelace", "acct:linkedin/in/gracehopperc", "acct:bluesky/alanturing.dev",
        "acct:mastodon/gracehopper@bolha.us", "site:adalovelace.com", "gh:adalovelace"}


def test_people_merge_on_a_shared_account_and_on_a_name_only_for_a_unique_speaker() -> None:
    index = PeopleIndex()
    index.register("person:ada-lovelace", "Ada C. Lovelace",
                   identity_keys({"x": "https://twitter.com/AdaLovelace"}))
    index.register("person:jose-nunez", "José Núñez", set())
    index.register("person:jane-doe", "Jane Doe", set())
    index.register("person:jane-doe-2", "Jane Doe", set())

    # An attendee post under a different display name is the same X account.
    assert index.resolve("Ada Lovelace", identity_keys({"x": "adalovelace"}),
                         claims_speaking=False) == "person:ada-lovelace"
    # Two attendees can share a name, so a bare name merges only a speaking claim.
    assert index.resolve("Jose Nunez", set(), claims_speaking=False) is None
    assert index.resolve("Jose Nunez", set(), claims_speaking=True) == "person:jose-nunez"
    assert index.resolve("Jane Doe", set(), claims_speaking=True) is None
    assert index.resolve("Jane Doe", identity_keys({"x": "AdaLovelace"}),
                         claims_speaking=True) == "person:ada-lovelace"


def test_recognition_claims_cite_the_sentence_and_rate_by_source() -> None:
    bio = ("Grace is the first Brazilian GitHub Star and has been a Microsoft MVP for 10 years. "
           "He is the Chief Architect and GenAI Lead at Wynxx and GFT.")

    claims = recognition_claims([
        ("bio", bio, None),
        ("bluesky_profile", "Docker Captain | Microsoft MVP | AWS Community Builder", None),
    ])

    # Each program is claimed once, from the first text that names it.
    assert [(c.label, c.basis, c.confidence) for c in claims] == [
        ("Microsoft MVP", "bio", "high"), ("GitHub Star", "bio", "high"),
        ("Docker Captain", "bluesky_profile", "medium")]
    assert [e.quote for e in claims[0].evidence] == [
        "Grace is the first Brazilian GitHub Star and has been a Microsoft MVP for 10 years."]

    profile = recognition_claims([("github_profile", "GitHub Star | AAIF Ambassador",
                                   "https://github.com/hedylamarr")])
    assert [(c.label, c.confidence, c.evidence[0].url) for c in profile] == [
        ("GitHub Star", "high", "https://github.com/hedylamarr")]


def test_registry_leaves_out_accounts_on_personal_platforms() -> None:
    registry = AccountRegistry()
    owner = "person:ada"

    for url in ("https://www.instagram.com/ada.l/", "https://www.threads.net/@ada.l",
                "https://www.facebook.com/ada.lovelace", "https://www.tiktok.com/@ada"):
        assert registry.add_url(url, owner, "github_profile", GITHUB_SOURCE) is None
    assert registry.add_social("instagram", "ada.l", owner, "curated", GITHUB_SOURCE) is None
    # Professional platforms, including an X account named after an excluded platform.
    assert registry.add_url("https://x.com/instagram", owner, "github_profile",
                            GITHUB_SOURCE) == "acct:x/instagram"
    assert registry.add_url("https://www.youtube.com/@AdaTalks", owner, "github_profile",
                            GITHUB_SOURCE) == "acct:youtube/@adatalks"

    assert registry.owned_by(owner) == (["acct:x/instagram", "acct:youtube/@adatalks"], [])
    assert {platform: len(ids) for platform, ids in registry.excluded.items()} == {
        "instagram": 1, "threads": 1, "facebook": 1, "tiktok": 1}


def test_registry_drops_curated_rejected_links() -> None:
    registry = AccountRegistry(rejected={("person:charles-babbage", "acct:x/harlesbabbage"),
                                         ("person:mary-somerville", "site:somerville.rocks")})

    assert registry.add_social("x", "harlesbabbage", "person:charles-babbage", "event_listing",
                               EVENT_SOURCE) is None
    assert registry.add_url("https://somerville.rocks/", "person:mary-somerville", "github_profile",
                            GITHUB_SOURCE) is None
    # The same account is still accepted for anyone else, and other links still register.
    assert registry.add_social("x", "charlesbabbage", "person:charles-babbage", "event_listing",
                               EVENT_SOURCE) == "acct:x/charlesbabbage"
    assert sorted(registry.accounts) == ["acct:x/charlesbabbage"]
    assert registry.websites == {}


def test_catalog_only_x_profiles_need_temporal_and_name_consistency() -> None:
    from universe_kb.models import Person
    from universe_kb.people import catalog_x_mismatch

    registry = AccountRegistry()
    old = Source(system="rainfocus", snapshot="raw/editions/universe23/sessions.json")
    registry.add_social("x", "adal", "person:ada", "event_listing", old)
    account = registry.accounts["acct:x/adal"].account
    person = Person.model_construct(name="Ada Lovelace", listed_for="event:github-universe-2023")
    assert catalog_x_mismatch(account, person, "Ada Lovelace", "2025-01-08T00:00:00Z")
    assert catalog_x_mismatch(account, person, "Unrelated Profile", "2010-01-01T00:00:00Z")
    assert not catalog_x_mismatch(account, person, "Ada L.", "2010-01-01T00:00:00Z")
    assert not catalog_x_mismatch(account, person, None, None)
    account.link_basis.append("github_profile")
    assert not catalog_x_mismatch(account, person, "Unrelated Profile", "2025-01-08T00:00:00Z")


def test_registry_rejects_webmail_and_non_web_addresses() -> None:
    registry = AccountRegistry()
    for value in ("gmail.com", "mailto:ada@example.org", "https://[broken"):
        assert registry.add_url(value, "person:ada", "event_listing", EVENT_SOURCE) is None


def test_pair_rejections_survive_missing_profile_cache_without_excluding_correct_owner() -> None:
    from universe_kb.people import rejected_link_fingerprint

    fingerprint = rejected_link_fingerprint("person:ada", "acct:x/renamed")
    assert fingerprint == rejected_link_fingerprint(" Person:Ada ", " ACCT:X/Renamed ")
    registry = AccountRegistry(rejected_hashes={fingerprint})
    assert registry.add_social("x", "renamed", "person:ada", "event_listing", EVENT_SOURCE) is None
    assert registry.add_social("x", "renamed", "person:grace", "github_profile", GITHUB_SOURCE) == (
        "acct:x/renamed")
    assert registry.accounts["acct:x/renamed"].owner == "person:grace"
