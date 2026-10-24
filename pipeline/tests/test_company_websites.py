from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from universe_kb.artifacts import write_artifact
from universe_kb.build import (
    Built,
    OrgIndex,
    RawData,
    company_site_owners,
    link_websites,
    sync_website_backlinks,
)
from universe_kb.graph import write_graph
from universe_kb.models import Affiliation, Event, Organization, Participation, Person, Source
from universe_kb.people import AccountRegistry, identity_keys, website_id

SEED = Source(system="curation", snapshot="curation/example.yaml")


def raw_with(root: Path, pages: dict[str, Any]) -> RawData:
    path = root / "websites/homepages.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pages))
    return RawData(root, {"websites/homepages.json": {
        "url": "https://snapshot.example/pages", "retrieved_at": "2026-10-24T00:00:00Z"}})


def test_company_websites_have_one_authoritative_owner_independent_of_employee_order(
        tmp_path: Path) -> None:
    for order in (("one", "two"), ("two", "one")):
        orgs = OrgIndex({"organizations": {"example-company": {
            "name": "Example Company", "website": "https://www.company.example"}}}, {})
        company = orgs.ensure("Example Company", "affiliation", SEED)
        registry = AccountRegistry()
        registry.add_social("x", "company_example", company.id, "curated", SEED)
        for employee in order:
            registry.add_url("https://company.example", f"person:employee-{employee}",
                             "github_profile", SEED)
        raw = raw_with(tmp_path, {"https://company.example": {
            "status": 200, "title": "Example Company", "rel_me": [
                "https://x.com/company_example", "https://x.com/unrelated_profile"],
            "social_links": ["https://x.com/unrelated_profile"]}})

        link_websites(raw, registry, {}, orgs)

        site = registry.websites["site:company.example"]
        assert site.owner == site.website.owner == company.id
        assert site.website.kind == "company"
        assert registry.owned_by(company.id) == (["acct:x/company_example"], [site.website.id])
        assert registry.owned_by("person:employee-one") == ([], [])
        assert registry.owned_by("person:employee-two") == ([], [])
        assert site.website.linked_accounts == ["acct:x/company_example"]
        assert set(registry.accounts) == {"acct:x/company_example"}
        registry.add_url("https://company.example", "person:employee-three", "x_profile", SEED)
        link_websites(raw, registry, {}, orgs)
        assert site.owner == site.website.owner == company.id


def test_ambiguous_organization_domains_do_not_choose_an_owner(tmp_path: Path) -> None:
    for order in (("one", "two"), ("two", "one")):
        orgs = OrgIndex({"organizations": {}}, {})
        for suffix in order:
            org = orgs.ensure(f"Example {suffix}", "affiliation", SEED)
            org.website = "https://shared.example"
        registry = AccountRegistry()
        registry.add_url("https://shared.example", "person:example-employee", "x_profile", SEED)
        raw = raw_with(tmp_path, {"https://shared.example": {"status": 200}})

        link_websites(raw, registry, {}, orgs)

        assert registry.websites == {}
        assert registry.owned_by("person:example-employee") == ([], [])


def test_website_tracking_variants_collapse_without_collapsing_query_profiles(
        tmp_path: Path) -> None:
    registry = AccountRegistry()
    owner = "person:example-owner"
    variants = ["https://company.example?utm_source=profile?utm_campaign=example#about",
                "https://company.example#about", "https://company.example"]
    for url in variants:
        registry.add_url(url, owner, "github_profile", SEED)
    assert set(registry.websites) == {"site:company.example"}
    assert registry.websites["site:company.example"].website.url == "https://company.example"
    assert {website_id(url) for url in variants} == {"site:company.example"}
    assert len({key for url in variants for key in identity_keys({"website": url})}) == 1
    for handle in ("example-one", "example-two"):
        registry.add_url(f"https://news.ycombinator.com/user?id={handle}",
                         f"person:{handle}", "github_profile", SEED)
    assert len(registry.accounts) == 2
    assert {r.account.url for r in registry.accounts.values()} == {
        "https://news.ycombinator.com/user?id=example-one",
        "https://news.ycombinator.com/user?id=example-two"}
    assert identity_keys({"website": "https://news.ycombinator.com/user?id=example-one"}) != (
        identity_keys({"website": "https://news.ycombinator.com/user?id=example-two"}))
    raw = raw_with(tmp_path, {
        variants[0]: {"status": 200, "title": "Tracked copy"},
        variants[2]: {"status": 200, "title": "Canonical copy"}})
    link_websites(raw, registry, {}, OrgIndex({"organizations": {}}, {}))
    assert registry.websites["site:company.example"].website.title == "Canonical copy"


def test_unproven_company_ownership_is_omitted_instead_of_guessed(tmp_path: Path) -> None:
    orgs = OrgIndex({"organizations": {}}, {})
    organization = orgs.ensure("Example Company", "affiliation", SEED)
    person = Person(
        id="person:example-employee", name="Example Employee", inclusion_basis="curated",
        github_resolution="absent", sources=[SEED],
        participations=[Participation(event="event:github-universe-2026", role="speaker",
                                      status="confirmed")],
        affiliations=[Affiliation(organization=organization.id, current=True, basis="curated")])
    registry = AccountRegistry()
    registry.add_url("https://examplecompany.app", person.id, "github_profile", SEED)
    raw = raw_with(tmp_path, {"https://examplecompany.app": {"status": 200}})

    link_websites(raw, registry, {person.id: person}, orgs)

    assert registry.websites == {}
    assert registry.owned_by(organization.id) == ([], [])
    organization.website = "https://company.co.uk"
    assert company_site_owners("https://unrelated.co.uk", orgs) == set()
    assert company_site_owners("https://docs.company.co.uk", orgs) == {organization.id}


def test_late_authoritative_domain_rehomes_an_already_fetched_site(tmp_path: Path) -> None:
    orgs = OrgIndex({"organizations": {}}, {})
    organization = orgs.ensure("Example Company", "affiliation", SEED)
    registry = AccountRegistry()
    registry.add_url("https://company.example", "person:example-employee", "x_profile", SEED)
    raw = raw_with(tmp_path, {"https://company.example": {"status": 200}})
    link_websites(raw, registry, {}, orgs, finalize_ownership=False)
    assert registry.websites["site:company.example"].website.fetch_status == "ok"
    organization.website = "https://www.company.example"

    link_websites(raw, registry, {}, orgs)

    site = registry.websites["site:company.example"]
    assert site.owner == site.website.owner == organization.id
    assert registry.owned_by("person:example-employee") == ([], [])


def test_nontracking_query_parameters_keep_distinct_identities_and_owners() -> None:
    registry = AccountRegistry()
    records = [("one", "person:example-one"), ("two", "person:example-two"),
               ("One", "person:example-capital")]
    keys = []
    for member, owner in records:
        url = f"https://directory.example/member?id={member}"
        keys.append(identity_keys({"website": url}))
        registry.add_url(url, owner, "github_profile", SEED)
        registry.add_url(url + "&UTM_SOURCE=profile?utm_campaign=example#bio", owner,
                         "x_profile", SEED)
    assert len({next(iter(key)) for key in keys}) == 3
    assert len(registry.websites) == 3
    assert {r.website.url for r in registry.websites.values()} == {
        f"https://directory.example/member?id={member}" for member, _ in records}
    assert {r.owner for r in registry.websites.values()} == {owner for _, owner in records}
    assert identity_keys({"website": "https://directory.example/member?ref=one"}) != (
        identity_keys({"website": "https://directory.example/member?ref=two"}))


def test_final_ownership_populates_serialized_org_backlinks_and_graph(tmp_path: Path) -> None:
    orgs = OrgIndex({"organizations": {"example-company": {
        "name": "Example Company", "website": "https://company.example"}}}, {})
    company = orgs.ensure("Example Company", "affiliation", SEED)
    registry = AccountRegistry()
    site_id = registry.add_url("https://company.example", "person:example-employee",
                               "github_profile", SEED)
    assert site_id is not None
    person = Person(
        id="person:example-employee", name="Example Employee", inclusion_basis="curated",
        github_resolution="absent", sources=[SEED], websites=[site_id],
        participations=[Participation(event="event:example-2026", role="speaker",
                                      status="confirmed")])
    organization = Organization(id=company.id, name=company.name, roles=["affiliation"],
                                sources=[SEED])
    event = Event(id="event:example-2026", name="Example Conference", series="Example",
                  edition="2026", organizer=company.id, start="2026-10-24T00:00:00Z",
                  end="2026-10-24T23:00:00Z", timezone="UTC", attendance_modes=["virtual"],
                  url="https://conference.example", days=[], sources=[SEED])
    raw = raw_with(tmp_path, {"https://company.example": {"status": 200}})
    link_websites(raw, registry, {person.id: person}, orgs)
    built = Built()
    built.add("organizations/example-company.md", "organization", organization)
    built.add("people/example-employee.md", "person", person)
    built.add("events/example-2026.md", "event", event)
    built.add("websites/company.example.yaml", "website", registry.websites[site_id].website)

    sync_website_backlinks(built, registry)
    kb = tmp_path / "kb"
    write_artifact(kb, kb / "_schemas", organization, envelope="organization",
                   rel_path="organizations/example-company.md", title=organization.name)
    write_graph(kb, built.models)

    assert person.websites == []
    assert organization.websites == [site_id]
    text = (kb / "organizations/example-company.md").read_text().split("---\n", 2)[1]
    assert yaml.safe_load(text)["organization"]["websites"] == [site_id]
    edges = [json.loads(line) for line in (kb / "_graph/edges.jsonl").read_text().splitlines()]
    assert [edge for edge in edges if edge["target"] == site_id] == [{
        "source": organization.id, "relation": "has_website", "target": site_id}]


def test_null_homepage_skips_metadata_without_skipping_ownership(tmp_path: Path) -> None:
    orgs = OrgIndex({"organizations": {"example-company": {
        "name": "Example Company", "website": "https://company.example"}}}, {})
    company = orgs.ensure("Example Company", "affiliation", SEED)
    registry = AccountRegistry()
    registry.add_url("https://company.example", "person:example-employee", "x_profile", SEED)
    raw = raw_with(tmp_path, {"https://company.example": None})

    link_websites(raw, registry, {}, orgs)

    site = registry.websites["site:company.example"]
    assert site.website.fetch_status == "not_fetched"
    assert site.owner == site.website.owner == company.id
