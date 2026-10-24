from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from universe_kb.artifacts import path_for
from universe_kb.build import (
    OrgIndex,
    RawData,
    adopt_github_claims,
    build,
    build_github,
    discover_github_claims,
    link_github_profiles,
)
from universe_kb.models import Participation, Person, Source
from universe_kb.people import AccountRegistry

SEED = Source(system="curation", snapshot="curation/example.yaml")
PIPELINE = Path(__file__).resolve().parents[1]


def person(suffix: str, github: str | None = None) -> Person:
    return Person(
        id=f"person:example-{suffix}", name=f"Example {suffix}",
        github=github, accounts=[github] if github else [],
        github_resolution="resolved" if github else "absent", sources=[SEED],
        inclusion_basis="curated", participations=[Participation(
            event="event:github-universe-2026", role="speaker", status="confirmed")])


def raw_with(root: Path) -> RawData:
    return RawData(root, {"github/owners.json": {
        "url": "https://api.github.com/graphql", "retrieved_at": "2026-10-24T00:00:00Z"}})


def owner(login: str = "shared-example") -> dict[str, Any]:
    return {"__typename": "User", "login": login, "name": "Example one",
            "url": f"https://github.com/{login}"}


def test_two_people_cannot_adopt_the_same_github_login(tmp_path: Path) -> None:
    for order in (("one", "two"), ("two", "one")):
        people = {p.id: p for p in (person(suffix) for suffix in order)}
        registry = AccountRegistry()
        for entity in people.values():
            registry.add_url("https://github.com/shared-example", entity.id,
                             "linkedin_profile", SEED)
        owners = {"shared-example": owner()}
        raw = raw_with(tmp_path)

        adopted = adopt_github_claims(raw, people, owners, registry)
        accounts, repositories = build_github(
            raw, owners, list(people.values()), OrgIndex({"organizations": {}}, {}))

        assert adopted == {}
        assert accounts == repositories == {}
        assert all(p.github is None and not p.accounts for p in people.values())
        assert all(p.sources == [SEED] for p in people.values())
        assert set(registry.github_claims) == set(people)


def test_direct_github_conflicts_are_rejected_for_people_and_organizations(
        tmp_path: Path) -> None:
    for with_org in (False, True):
        for order in (("one", "two"), ("two", "one")):
            people = [person(suffix, "gh:shared-example") for suffix in order]
            orgs = OrgIndex({"organizations": {}}, {})
            if with_org:
                people = people[:1]
                orgs.ensure("Example Company", "affiliation", SEED).github_login = (
                    "SHARED-example")
            accounts, repositories = build_github(
                raw_with(tmp_path), {"shared-example": owner()}, people, orgs)

            assert accounts == repositories == {}
            assert all(p.github is None and not p.accounts for p in people)
            assert all(p.github_resolution == "unverified" for p in people)
            assert all(p.links[0].url == "https://github.com/shared-example" for p in people)
            assert all(p.sources == [SEED] for p in people)
            assert all(org.github_login is None for org in orgs.records.values())


def test_listed_login_conflicts_with_another_persons_profile_claim(tmp_path: Path) -> None:
    first, second = person("one", "gh:shared-example"), person("two")
    people = {p.id: p for p in (first, second)}
    registry = AccountRegistry()
    registry.add_url("https://github.com/shared-example", second.id, "x_profile", SEED)

    adopted = adopt_github_claims(
        raw_with(tmp_path), people, {"shared-example": owner()}, registry)

    assert adopted == {}
    assert first.github is second.github is None
    assert first.accounts == second.accounts == []
    assert first.sources == second.sources == [SEED]


def test_external_claim_discovery_precedes_github_social_and_employer_enrichment(
        tmp_path: Path) -> None:
    snapshot = "brightdata/x_profiles.json"
    path = tmp_path / snapshot
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"https://x.com/example_two": {
        "snapshot_id": "example-snapshot", "records": [{
            "profile_name": "Example two", "external_link": "https://github.com/shared-example"}]}}))
    for order in (("one", "two"), ("two", "one")):
        people = {p.id: p for p in (
            person(suffix, "gh:shared-example" if suffix == "one" else None) for suffix in order)}
        registry = AccountRegistry()
        registry.add_social("x", "example_two", "person:example-two", "curated", SEED)
        orgs = OrgIndex({"organizations": {}}, {})
        raw = raw_with(tmp_path)
        raw.manifest[snapshot] = {"url": "https://snapshot.example/x", "retrieved_at":
                                  "2026-10-24T00:00:00Z"}
        node = {**owner(), "company": "Example Employer", "twitterUsername": "wrong_owner"}
        owners = {"shared-example": node}

        discover_github_claims(raw, people, owners, registry, orgs)
        link_github_profiles(raw, people, owners, registry, orgs)

        assert all(p.github is None and not p.accounts for p in people.values())
        assert all(not p.affiliations and p.sources == [SEED] for p in people.values())
        assert set(registry.accounts) == {"acct:x/example_two"}
        assert registry.websites == {}
        assert orgs.records == {}
        # The real source profile and its initial provenance survived the private discovery pass.
        assert registry.accounts["acct:x/example_two"].account.sources == [SEED]
        assert registry.accounts["acct:x/example_two"].account.details_fetched is False


def test_full_build_github_owners_and_profile_repositories_agree(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    build(PIPELINE / "raw", PIPELINE / "curation", kb, PIPELINE / "schemas")
    nodes = [json.loads(line) for line in (kb / "_graph/nodes.jsonl").read_text().splitlines()]

    def payload(ref: str) -> dict[str, Any]:
        text = (kb / path_for(ref)).read_text()
        if text.startswith("---\n"):
            text = text.removeprefix("---\n").split("\n---\n", 1)[0]
        data = yaml.load(text, Loader=yaml.CSafeLoader)
        return data[data["softschema"]["envelope"]]

    entities = {n["id"]: payload(n["id"]) for n in nodes
                if n["kind"] in {"person", "organization"}}
    accounts = {n["id"]: payload(n["id"]) for n in nodes if n["kind"] == "github_account"}
    listers: dict[str, list[str]] = {}
    for ref, entity in entities.items():
        github = entity.get("github")
        if github:
            assert github in entity.get("accounts", [])
        for account in entity.get("accounts", []):
            if account.startswith("gh:"):
                listers.setdefault(account, []).append(ref)
    assert set(listers) == set(accounts)
    assert all(listers[ref] == [account["entity"]] for ref, account in accounts.items())
    for ref, entity in entities.items():
        if not ref.startswith("person:"):
            continue
        profile = payload(entity["profile"])
        if not entity.get("github"):
            assert profile.get("open_source", []) == []
        else:
            account = accounts[entity["github"]]
            related = {*account.get("pinned", []), *account.get("top_repositories", []),
                       *account.get("contributed_to", [])}
            assert all(work["repository"] in related or work["relation"] == "owner"
                       for work in profile.get("open_source", []))
