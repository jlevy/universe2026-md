from __future__ import annotations

import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from universe_kb.artifacts import path_for, to_yaml
from universe_kb.build import (
    EVENT_ID,
    Gazetteer,
    OrgIndex,
    RawData,
    apply_repo_stats,
    assign_ids,
    build,
    clean_url,
    curation_source,
    is_company_site,
    link_github_profiles,
    local_iso,
    program_recognitions,
    registration_link,
    repository_model,
    session_hosts,
    split_room_label,
)
from universe_kb.ids import slugify
from universe_kb.models import CONTRACTS, Affiliation, Claim, Evidence, Participation, Person
from universe_kb.people import AccountRegistry
from universe_kb.policy import (
    EXCLUDED_PLATFORMS,
    excluded_platform,
    exclusion_fingerprint,
    says_attending,
)
from universe_kb.privacy import findings as privacy_findings
from universe_kb.schemas import validate_kb
from universe_kb.sensitive import categories as sensitive_categories
from universe_kb.sensitive import city_level

CONFERENCE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = CONFERENCE_DIR / "raw"
CURATION_DIR = CONFERENCE_DIR / "curation"
SCHEMA_DIR = CONFERENCE_DIR / "schemas"


def org_index() -> OrgIndex:
    """The organization index `build()` starts from, before any source adds records."""
    software = yaml.safe_load((CURATION_DIR / "software.yaml").read_text())
    return OrgIndex(yaml.safe_load((CURATION_DIR / "organizations.yaml").read_text()),
                    software.get("mentioned_organizations", {}))


def kb_payload(kb_dir: Path, ref: str) -> dict[str, Any]:
    """The payload of the artifact that defines `ref`, from YAML or Markdown front matter."""
    text = (kb_dir / path_for(ref)).read_text()
    if text.startswith("---\n"):
        text = text.removeprefix("---\n").split("\n---\n", 1)[0]
    data = yaml.load(text, Loader=yaml.CSafeLoader)
    return data[data["softschema"]["envelope"]]


def test_gazetteer_is_longest_first_case_sensitive_and_whole_word() -> None:
    gazetteer = Gazetteer({
        "GitHub Copilot CLI": "software:copilot-cli",
        "Copilot CLI": "software:copilot-cli",
        "GitHub Copilot": "software:copilot",
        "Copilot": "software:copilot",
        ".NET": "software:dotnet",
        "C#": "software:csharp",
        "Go": "software:go",
    })

    assert gazetteer.find("Try GitHub Copilot CLI today") == [
        ("GitHub Copilot CLI", "software:copilot-cli")]
    assert gazetteer.find("Copilot CLI and GitHub Copilot") == [
        ("Copilot CLI", "software:copilot-cli"), ("GitHub Copilot", "software:copilot")]
    assert gazetteer.find("Ask Copilot. Not copilot.") == [("Copilot", "software:copilot")]
    assert gazetteer.find("Port .NET apps to C# and F#") == [
        (".NET", "software:dotnet"), ("C#", "software:csharp")]
    assert gazetteer.find("Google and Golang ship Go.") == [("Go", "software:go")]
    assert gazetteer.find("Follow @Copilot or github.com/Copilot") == []


def test_gazetteer_skips_ignored_phrases_and_hyphen_coinages() -> None:
    gazetteer = Gazetteer({"Salesforce": "org:salesforce", "Git": "software:git"},
                          ignore=["Salesforce Park"])

    assert gazetteer.find("Join the Git-Together at Salesforce Park, then meet Salesforce. "
                          "Bring your Git questions.") == [
        ("Salesforce", "org:salesforce"), ("Git", "software:git")]


def test_split_room_label_on_catalog_labels() -> None:
    venues = yaml.safe_load((CURATION_DIR / "venues.yaml").read_text())

    assert split_room_label("Main Stage @ Festival Pavilion", venues) == (
        "Main Stage", "festival-pavilion", None, None)
    assert split_room_label("Workshops @ Gateway Pavilion, Level 1", venues) == (
        "Workshops", "gateway-pavilion", "Level 1", None)
    assert split_room_label("Sandbox @ Fort Mason Building C, Founders Inc., 3rd Floor",
                            venues) == ("Sandbox", "building-c", "Founders Inc., 3rd Floor", None)
    # The building can come after an area inside it.
    assert split_room_label("The Speakeasy @ GitHub Central, Festival Pavilion", venues) == (
        "The Speakeasy", "festival-pavilion", "GitHub Central", None)
    # A place that is not on campus is an outside venue at that address.
    assert split_room_label("Hotel Zephyr @ 250 Beach St", venues) == (
        "Hotel Zephyr", None, None, "250 Beach St")
    assert split_room_label("Redwood Empire Whiskey", venues) == (
        "Redwood Empire Whiskey", None, None, None)


def test_assign_ids_suffixes_collisions_in_input_order() -> None:
    ids = assign_ids({"u1": "Jane Doe", "u2": "José Ñúñez", "u3": "Jane  Doe", "u4": "jane-doe",
                      "u5": "李雷", "u6": "王芳"}, "person")

    assert ids == {
        "u1": "person:jane-doe",
        "u2": "person:jose-nunez",
        "u3": "person:jane-doe-2",
        "u4": "person:jane-doe-3",
        # Names with no ASCII letters fall back to the same slug and still get unique IDs.
        "u5": "person:x",
        "u6": "person:x-2",
    }


def test_assign_ids_never_repeats_an_id() -> None:
    ids = assign_ids({"u1": "Jane Doe", "u2": "Jane Doe", "u3": "Jane Doe 2"}, "person")

    assert len(set(ids.values())) == 3


def test_local_iso_converts_catalog_utc_to_san_francisco_time() -> None:
    assert local_iso("2026/10/28 16:00:00") == "2026-10-28T09:00:00-07:00"
    # The first pre-event slot is on Oct 27 in UTC but Oct 26 locally.
    assert local_iso("2026/10/27 01:30:00") == "2026-10-26T18:30:00-07:00"
    # Daylight saving time ends on Nov 1, 2026.
    assert local_iso("2026/11/02 16:00:00") == "2026-11-02T08:00:00-08:00"


def test_clean_url() -> None:
    assert clean_url(" www.example.com/x?utm_source=a&id=3. ") == "https://www.example.com/x?id=3"
    assert clean_url("   ") is None
    assert clean_url(None) is None


def test_registration_link_needs_sign_up_text_or_an_event_platform() -> None:
    assert registration_link(
        "Hosted by NeuBird and FluidCloud. Advance [registration required]"
        "(https://neubird.ai/events/happy-hour?utm_source=Events&utm_medium=Github).") == (
        "https://neubird.ai/events/happy-hour")
    assert registration_link("Hosted by Syntax. [Details](https://luma.com/5ng6bniy)") == (
        "https://luma.com/5ng6bniy")
    assert registration_link("Hosted by Syntax. https://luma.com/5ng6bniy?utm_source=github") == (
        "https://luma.com/5ng6bniy")
    # A partner's homepage and a link to another catalog session are not sign-up pages.
    assert registration_link(
        "Join GitHub Gives and local nonprofit [Refuse Refuse](https://refuserefusesf.org/) "
        "for a community cleanup around Fort Mason Center.") is None
    assert registration_link(
        "Follows [the keynote](https://reg.githubuniverse.com/flow/github/universe26/"
        "attendee-portal/page/sessioncatalog/session/1) and [RSVP here]"
        "(https://githubuniverse.com/rsvp).") is None


def test_session_hosts_from_host_phrases_and_curation() -> None:
    def hosts(title: str, abstract: str, code: str = "TEST1") -> list[str]:
        item = {"title": title, "code": code, "attributevalues": []}
        return session_hosts(item, abstract, [], org_index(), curation_source("test"))

    assert hosts("Happy hour", "Hosted by\xa0NeuBird and FluidCloud. Advance registration.") == [
        "org:neubird", "org:fluidcloud"]
    assert hosts("Frontiers", "An evening of out-of-this-world perspectives, co-sponsored by "
                 "Moderne.io and Microsoft. As organizations move beyond experimentation, "
                 "connect with peers.\n\nHosted by Slalom. Advance registration.") == [
        "org:slalom", "org:moderne", "org:microsoft"]
    assert hosts("Git-Together", "Come raise a glass with us! Hosted by Cloudsmith, Chainguard, "
                 "Eficode, Octopus Deploy, and Tailscale.") == [
        "org:cloudsmith", "org:chainguard", "org:eficode", "org:octopus-deploy", "org:tailscale"]
    # A lowercase "hosted by" mid-sentence names a person, not a host organization.
    assert hosts("A Taste of the Craft - Hosted by Rewind",
                 "An evening of whiskey, hosted by Master Blender Lauren Patz.") == ["org:rewind"]
    # Curation names the sponsor of a session whose speakers work elsewhere.
    assert hosts("Agentic delivery", "A session.", code="BLD1916M") == ["org:accenture"]


def test_github_profile_links_to_professional_profiles_become_accounts() -> None:
    raw = RawData(RAW_DIR, json.loads((RAW_DIR / "manifest.json").read_text())["files"])
    person = Person(
        id="person:ada", name="Ada", inclusion_basis="curated", github="gh:ada",
        github_resolution="resolved", sources=[curation_source("people.yaml")],
        participations=[Participation(event=EVENT_ID, role="attendee", status="candidate")])
    owners: dict[str, Any] = {"ada": {
        "login": "ada", "url": "https://github.com/ada", "__typename": "User",
        "websiteUrl": "https://www.youtube.com/@ada",
        "socialAccounts": {"nodes": [
            {"provider": "GENERIC", "url": "https://threads.net/@ada"},
            {"provider": "GENERIC", "url": "https://hachyderm.io/@ada"},
            {"provider": "GENERIC", "url": "https://ada.dev"},
        ]},
    }}
    registry = AccountRegistry()

    link_github_profiles(raw, {person.id: person}, owners, registry, org_index())

    # Threads is a personal platform, left out by default.
    assert registry.owned_by(person.id) == (
        ["acct:mastodon/ada@hachyderm.io", "acct:youtube/@ada"], ["site:ada.dev"])
    assert set(registry.excluded) == {"threads"}


def excluding_one_speaker(curation_dir: Path) -> dict[str, Any]:
    """
    Copy curation into `curation_dir`, excluding the first 2026 speaker who gave a GitHub
    handle, and return what identifies them, so the build can be checked for traces.
    """
    owners = json.loads((RAW_DIR / "github/owners.json").read_text())
    catalog = json.loads((RAW_DIR / "rainfocus/sessions.json").read_text())["items"]
    for participant in (p for item in catalog for p in item.get("participants") or []):
        login = next((a["value"] for a in participant.get("attributevalues") or []
                      if a["attribute"] == "GitHub Handle"), "").lstrip("@")
        if (owners.get(login.lower()) or {}).get("__typename") == "User":
            break
    else:
        raise AssertionError("no 2026 speaker with a GitHub account")
    name = participant["fullName"].strip()
    fingerprints = [{"sha256": exclusion_fingerprint(key)}
                    for key in (f"person:{slugify(name)}", f"gh:{login.lower()}")]
    shutil.copytree(CURATION_DIR, curation_dir)
    people = yaml.safe_load((curation_dir / "people.yaml").read_text())
    people["exclude"] = [*(people.get("exclude") or []), *fingerprints]
    (curation_dir / "people.yaml").write_text(yaml.safe_dump(people, allow_unicode=True))
    return {"id": f"person:{slugify(name)}", "name": name, "github": f"gh:{login.lower()}"}


def test_build_writes_a_valid_connected_kb(tmp_path: Path) -> None:
    kb_dir = tmp_path / "kb"
    excluded = excluding_one_speaker(tmp_path / "curation")

    stats = build(RAW_DIR, tmp_path / "curation", kb_dir, SCHEMA_DIR)
    report = validate_kb(kb_dir)

    # A person excluded in curation leaves no trace: not their ID, name or GitHub account,
    # in any record, search document or graph export.
    traces = [(path.relative_to(kb_dir), needle) for path in kb_dir.rglob("*")
              if path.is_file() for needle in excluded.values()
              if needle in path.read_text()]
    assert traces == []

    assert report["invalid"] == 0
    assert report["failures"] == []
    # 156 sessions this year plus the 2023 to 2025 catalogs (test rows removed).
    assert report["by_contract"][CONTRACTS["session"].contract_id] == 156 + 149 + 128 + 87
    assert report["by_contract"][CONTRACTS["event"].contract_id] == 4
    # The snapshot keeps growing as collection runs add attendees, so people are checked
    # against the official speakers plus at least the original research set.
    person_count = report["by_contract"][CONTRACTS["person"].contract_id]
    assert person_count >= 195
    assert report["by_contract"][CONTRACTS["profile"].contract_id] == person_count
    assert len(list((kb_dir / "sessions").glob("*.md"))) == 156
    assert len(list((kb_dir / "people").glob("*.md"))) == person_count

    nodes = [json.loads(line) for line in (kb_dir / "_graph/nodes.jsonl").read_text().splitlines()]
    edges = [json.loads(line) for line in (kb_dir / "_graph/edges.jsonl").read_text().splitlines()]
    node_ids = {node["id"] for node in nodes}
    assert len(node_ids) == len(nodes)
    assert len(edges) == stats["edge_total"]
    endpoints = {edge["source"] for edge in edges} | {edge["target"] for edge in edges}
    assert endpoints - node_ids == set()
    # Every featured speaker on the home page resolved to a catalog person.
    assert stats["edges"]["features"] == 8

    # Search documents cover every person and session, with each one's own text.
    documents = {d["id"]: d for d in map(json.loads, (
        kb_dir / "_search/documents.jsonl").read_text().splitlines())}
    for kind in ("person", "session"):
        ids = {n["id"] for n in nodes if n["kind"] == kind}
        assert ids <= set(documents)
        assert all(documents[i]["title"] and documents[i]["text"] for i in ids)
    assert any(d["kind"] == "faq_entry" for d in documents.values())
    coverage = json.loads((kb_dir / "_graph/coverage.json").read_text())
    assert coverage["session"]["fields"]["abstract"] == 100
    # No email address or phone number survives anywhere, exports included.
    assert privacy_findings(kb_dir) == []

    def of_kind(kind: str) -> dict[str, dict[str, Any]]:
        return {n["id"]: kb_payload(kb_dir, n["id"]) for n in nodes if n["kind"] == kind}

    people = of_kind("person")
    current = "event:github-universe-2026"
    roles = {pid: {(p["event"], p["role"], p["status"]) for p in person["participations"]}
             for pid, person in people.items()}
    speakers = {pid for pid, found in roles.items() if (current, "speaker", "confirmed") in found}
    past_speakers = {pid for pid, found in roles.items()
                     if any(e != current and r == "speaker" and st == "confirmed"
                            for e, r, st in found)}
    attendees = {pid for pid, found in roles.items()
                 if found and {(r, st) for _, r, st in found}
                 <= {("attendee", "self_reported"), ("attendee", "candidate")}}
    # One contradictory catalog participant is quarantined; the fixture excludes another.
    assert len(speakers) == 183 - 2
    # Attendees enter only through their own public post saying they will be there.
    assert len(attendees) >= 1
    # Returning speakers merged across editions instead of being duplicated.
    assert len({person["name"] for person in people.values()}) == len(people)
    assert len(speakers & past_speakers) >= 30
    # Everyone is here for a published talk or a public post about attending.
    assert speakers | past_speakers | attendees == set(people)
    assert {people[pid]["inclusion_basis"] for pid in attendees} == {"public_self_report"}
    assert all(says_attending(e.get("quote"))
               for pid in attendees for p in people[pid]["participations"]
               if p["role"] == "attendee" for e in p["evidence"][-1:])

    refs = {pid: [*person.get("accounts", []), *person.get("websites", []), person["profile"]]
            for pid, person in people.items()}
    assert [(pid, ref) for pid, listed in refs.items() for ref in listed
            if ref not in node_ids] == []
    assert [pid for pid, person in people.items()
            if kb_payload(kb_dir, person["profile"])["person"] != pid] == []

    # Each social account and website belongs to the one person or organization listing it.
    listers: dict[str, list[str]] = defaultdict(list)
    for entity_id, entity in {**people, **of_kind("organization")}.items():
        for ref in [*entity.get("accounts", []), *entity.get("websites", [])]:
            if not ref.startswith("gh:"):
                listers[ref].append(entity_id)
    owners = {ref: payload.get("owner")
              for ref, payload in {**of_kind("social_account"), **of_kind("website")}.items()}
    assert {ref: ids for ref, ids in listers.items() if len(ids) > 1} == {}
    assert {ref: owner for ref, owner in owners.items() if listers.get(ref) != [owner]} == {}

    # Personal platforms are left out. Nothing the build derives about a person states a
    # sensitive attribute, and no location is finer than a city.
    accounts = of_kind("social_account")
    assert {a["platform"] for a in accounts.values()} & set(EXCLUDED_PLATFORMS) == set()
    assert [ref for ref, a in accounts.items() if excluded_platform(a["url"])] == []
    described = {**people, **accounts, **of_kind("github_account"), **of_kind("website"),
                 **of_kind("profile")}
    for ref, payload in described.items():
        owner = payload.get("owner") or payload.get("entity") or payload.get("person") or ref
        if not owner.startswith("person:"):
            continue
        if ref.startswith("profile:"):
            assert not sensitive_categories(payload.get("headline")), ref
            derived = [item.get(f) for key, fields in (
                ("recent_writing", ("title",)), ("activities", ("title", "detail")),
                ("interests", ("label",)), ("credentials", ("title",)))
                for item in payload.get(key) or [] for f in fields]
            assert [text for text in derived if sensitive_categories(text)] == [], ref
        location = payload.get("location")
        assert city_level(location) == location, (ref, location)


def test_to_yaml_quotes_digit_strings_a_yaml_12_reader_would_take_as_numbers() -> None:
    assert to_yaml({"id": "000438289", "version": "1.0", "name": "1Password"}) == (
        "id: '000438289'\nversion: '1.0'\nname: 1Password\n")


def test_is_company_site_reads_company_hosts_but_not_personal_pages() -> None:
    orgs = OrgIndex({"organizations": {}}, {})
    person = Person(
        id="person:ada", name="Ada Lovelace", inclusion_basis="curated",
        github_resolution="absent", sources=[curation_source("test.yaml")],
        participations=[Participation(event="event:github-universe-2026", role="speaker",
                                      status="confirmed")],
        affiliations=[Affiliation(organization=orgs.ensure("GitHub", "affiliation",
                                                           curation_source("test.yaml")).id,
                                  current=True, basis="event_listing"),
                      Affiliation(organization=orgs.ensure("Microsoft", "affiliation",
                                                           curation_source("test.yaml")).id,
                                  current=True, basis="linkedin")])

    assert is_company_site("https://m365.cloud.microsoft/chat", person, orgs)
    assert is_company_site("https://docs.github.com/", person, orgs)
    assert not is_company_site("https://ada.github.io/", person, orgs)
    assert not is_company_site("https://ada.dev/", person, orgs)


def test_refreshed_repository_counts_replace_the_owner_record_s(tmp_path: Path) -> None:
    def node(full_name: str, stars: int, **extra: Any) -> dict[str, Any]:
        return {"nameWithOwner": full_name, "url": f"https://github.com/{full_name}",
                "stargazerCount": stars, "forkCount": 2, "isArchived": False,
                "isFork": False, "pushedAt": "2025-01-01T00:00:00Z",
                "repositoryTopics": {"nodes": []}, "owner": {"login": "octo"}, **extra}

    retrieved = "2026-01-01T00:00:00Z"
    manifest = {rel: {"url": "https://api.github.com/graphql", "retrieved_at": retrieved}
                for rel in ("github/owners.json", "github/repo-stats.json")}
    stats = {
        "octo/hello": node("octo/hello", 500, isArchived=True, pushedAt="2026-10-20T08:00:00Z",
                           watchers={"totalCount": 31}, issues={"totalCount": 12},
                           fetched_at="2026-10-24T19:00:00Z"),
        "octo/gone": {"missing": True, "fetched_at": "2026-10-24T19:00:00Z"},
    }
    (tmp_path / "github").mkdir()
    (tmp_path / "github/repo-stats.json").write_text(json.dumps(stats))
    raw = RawData(tmp_path, manifest)
    owner_source = raw.source("github/owners.json", "octo")
    repos = {r.id: r for r in (repository_model(node("octo/Hello", 120), owner_source, set()),
                               repository_model(node("octo/gone", 40), owner_source, set()),
                               repository_model(node("octo/never", 7), owner_source, set()))}

    assert apply_repo_stats(raw, repos) == 1

    hello, gone, never = repos.values()
    assert (hello.stars, hello.forks, hello.archived) == (500, 2, True)
    assert (hello.watchers, hello.open_issues) == (31, 12)
    assert hello.pushed_at == "2026-10-20T08:00:00Z"
    assert hello.stats_observed_at == "2026-10-24T19:00:00Z"
    assert [(s.snapshot, s.record_id) for s in hello.sources] == [
        ("raw/github/owners.json", "octo"), ("raw/github/repo-stats.json", "octo/Hello")]
    # A repository the refresh found missing, or never read, keeps the owner's counts.
    for repo, stars in ((gone, 40), (never, 7)):
        assert (repo.stars, repo.stats_observed_at, len(repo.sources)) == (stars, None, 1)
    type(hello).model_validate(hello.model_dump())


def test_program_recognitions_come_from_github_flags_once() -> None:
    node = {"login": "ada", "url": "https://github.com/ada", "isGitHubStar": True,
            "isCampusExpert": False}
    stated = Claim(label="GitHub Star", basis="bio", confidence="medium",
                   evidence=[Evidence(quote="GitHub Star")])

    assert [(c.label, c.basis) for c in program_recognitions(node, [])] == [
        ("GitHub Star", "github_profile")]
    assert program_recognitions(node, [stated]) == []
    assert program_recognitions(None, []) == []
