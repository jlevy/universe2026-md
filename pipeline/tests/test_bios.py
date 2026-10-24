"""
Brief bios: the evidence bundle a bio is written from, the writing rules every bio must
pass, and merging subagent output into `synthesis/brief-bios.yaml`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from universe_kb.bios import (
    bundle_hash,
    check_bio,
    check_file,
    load_bios,
    load_kb_payloads,
    merge_bios,
    person_bundle,
    prune_bios,
)

ADA = "person:ada-lovelace"
EVENT_2026 = "event:github-universe-2026"
EVENT_2024 = "event:github-universe-2024"
ENTITIES: dict[str, dict[str, Any]] = {
    "org:acme": {"name": "Acme"},
    "org:analytical-society": {"name": "Analytical Society"},
    EVENT_2026: {"name": "GitHub Universe 2026"},
    EVENT_2024: {"name": "GitHub Universe 2024"},
    "session:2024/brk101": {"title": "Compilers for everyone", "event": EVENT_2024},
    "gh:ada": {"bio": "Builds   engines.", "headline": "Not a GitHub field",
               "profile_readme": "Hi, I'm Ada.", "location": "London"},
    "acct:linkedin/in/ada": {"platform": "linkedin", "headline": "Principal Engineer at Acme",
                             "bio": "Writes compilers.", "location": "Paris"},
    "site:ada.dev": {"title": "Ada's notes", "description": "Essays on engines"},
}


def test_person_bundle_collects_the_facts_a_bio_may_cite() -> None:
    person = {
        "id": ADA, "name": "Ada Lovelace", "job_title": "Principal Engineer",
        "affiliations": [
            {"organization": "org:acme", "title": "Principal Engineer", "current": True},
            # The same role from a second source is one fact.
            {"organization": "org:acme", "title": "Principal Engineer", "current": True},
            {"organization": "org:analytical-society", "current": False}],
        "bio": "Ada  writes\ncompilers.",
        "participations": [
            {"event": EVENT_2024, "role": "speaker", "status": "self_reported"},
            {"event": EVENT_2026, "role": "speaker", "status": "confirmed"}],
        "sessions": [{"session": "session:2024/brk101"}, {"session": "session:not-in-kb"}],
        "accounts": ["gh:ada", "acct:linkedin/in/ada"],
        "websites": ["site:ada.dev"],
    }
    profile = {
        "location": "Somewhere else",
        "expertise": [{"label": "Compilers"}], "technologies": [],
        "education": [{"school": "University of London"}],
        "recent_writing": [{"title": "Notes on G", "channel": "blog"},
                           {"title": "A post on X", "channel": "x"}],
        "open_source": [{"repository": "repo:ada/engine", "relation": "owner"},
                        {"repository": "repo:other/lib", "relation": "contributor"}],
    }

    assert person_bundle(person, profile, ENTITIES) == {"person": ADA, "facts": {
        "name": "Ada Lovelace",
        "current_affiliations": ["Principal Engineer at Acme"],
        "past_affiliations": ["Analytical Society"],
        "event_bio": "Ada writes compilers.",
        "participation": ["speaker (confirmed) at GitHub Universe 2026",
                          "speaker (self reported) at GitHub Universe 2024"],
        "sessions": ["Compilers for everyone (GitHub Universe 2024)"],
        "github_bio": "Builds engines.",
        "github_readme": "Hi, I'm Ada.",
        # The first account with a location wins over later accounts and the profile.
        "location": "London",
        "linkedin_headline": "Principal Engineer at Acme",
        "linkedin_bio": "Writes compilers.",
        "websites": ["Ada's notes — Essays on engines"],
        "expertise": ["Compilers"],
        "education": ["University of London"],
        "recent_writing": ["Notes on G"],
        "open_source": ["ada/engine"],
    }}

    sparse = {"id": "person:jo", "name": "Jo Smith", "bio": "  ", "affiliations": [],
              "sessions": [{"session": "session:not-in-kb"}],
              "participations": [{"event": EVENT_2026, "role": "attendee", "status": "candidate"}]}
    expected = {"person": "person:jo", "facts": {
        "name": "Jo Smith", "participation": ["attendee (candidate) at GitHub Universe 2026"]}}
    assert person_bundle(sparse, None, ENTITIES) == expected
    assert person_bundle(sparse, {"expertise": [], "recent_writing": []}, ENTITIES) == expected


def test_bundle_hash_ignores_key_order_but_not_content() -> None:
    bundle = {"person": ADA, "facts": {"name": "Ada Lovelace", "expertise": ["Compilers"]}}
    reordered = {"facts": {"expertise": ["Compilers"], "name": "Ada Lovelace"}, "person": ADA}
    changed = {"person": ADA, "facts": {"name": "Ada Lovelace", "expertise": ["Engines"]}}

    assert bundle_hash(bundle) == bundle_hash(reordered)
    assert bundle_hash(bundle) != bundle_hash(changed)


def test_check_bio_rules() -> None:
    bundle = {"person": ADA, "facts": {"name": "Ada Lovelace", "job_title": "Principal Engineer",
                                       "current_affiliations": ["Principal Engineer at Acme"]}}
    cites = ["job_title", "current_affiliations"]
    # "the", "shell" and "Node.js" contain pronoun letters or a period but are not
    # pronouns or sentence ends; "They" is the neutral pronoun bios may use.
    good = "Ada Lovelace leads the shell and Node.js teams at Acme. They write about compilers."

    assert check_bio(good, bundle, cites) == []
    assert check_bio("Ada Lovelace " + "builds engines " * 25, bundle, cites) == [
        "longer than 320 characters"]
    assert check_bio("Ada Lovelace builds engines. Lovelace writes. Lovelace speaks!",
                     bundle, cites) == ["more than two sentences"]
    assert check_bio("Ada Lovelace leads Acme, where her team builds engines.",
                     bundle, cites) == ["uses a gendered pronoun"]
    assert check_bio("She leads Acme's engine team as Lovelace.", bundle, cites) == [
        "uses a gendered pronoun"]
    assert check_bio("Ada leads engineering at Acme.", bundle, cites) == [
        "does not name the person"]
    assert check_bio(good, bundle, ["job_title", "github_bio"]) == [
        "cites unknown facts: ['github_bio']"]
    assert check_bio(good, bundle, []) == ["cites nothing"]


def test_check_bio_accepts_a_family_name_that_is_also_a_pronoun() -> None:
    bundle = {"person": "person:kaiming-he",
              "facts": {"name": "Kaiming He", "job_title": "Research Scientist"}}

    assert check_bio("Kaiming He is a research scientist.", bundle, ["job_title"]) == []


def write_bundles(root: Path) -> dict[str, str]:
    """
    Bundles in a synthesis directory as `bio-bundles` writes them, and an empty `bios/`
    for subagent output. Returns each person's bundle hash.
    """
    facts = {ADA: {"name": "Ada Lovelace", "job_title": "Principal Engineer"},
             "person:grace-hopper": {"name": "Grace Hopper", "job_title": "Rear Admiral"},
             "person:alan-turing": {"name": "Alan Turing", "job_title": "Mathematician"}}
    hashes: dict[str, str] = {}
    lines = []
    for person_id, person_facts in facts.items():
        bundle = {"person": person_id, "facts": person_facts}
        hashes[person_id] = bundle_hash(bundle)
        lines.append(json.dumps({**bundle, "input_sha256": hashes[person_id]}))
    (root / "bundles").mkdir(parents=True)
    (root / "bundles" / "batch-01.jsonl").write_text("\n".join(lines) + "\n")
    (root / "bios").mkdir()
    return hashes


def bio(person_id: str, text: str, input_sha256: str) -> dict[str, Any]:
    return {"person": person_id, "text": text, "cites": ["job_title"],
            "written_by": "claude-subagent", "written_at": "2026-10-24T09:00:00Z",
            "input_sha256": input_sha256}


def test_merge_bios_merges_good_bios_and_reports_the_rest(tmp_path: Path) -> None:
    root = tmp_path / "synthesis"
    hashes = write_bundles(root)
    bios = [
        bio(ADA, "Ada Lovelace is a   principal\nengineer.", hashes[ADA]),
        bio("person:grace-hopper", "Grace Hopper is a rear admiral.", "0" * 64),
        bio("person:alan-turing", "Alan Turing is a mathematician known for his machine.",
            hashes["person:alan-turing"]),
        bio("person:nobody", "Nobody is here.", "0" * 64),
    ]
    (root / "bios" / "x.yaml").write_text(yaml.safe_dump({"bios": bios}))
    # A bio merged earlier stays when its rewrite is rejected.
    earlier = bio("person:grace-hopper", "Grace Hopper wrote compilers.", "f" * 64)
    (root / "brief-bios.yaml").write_text(yaml.safe_dump({"bios": [earlier]}))

    assert check_file(root, root / "bios" / "x.yaml") == {"entries": 4, "ok": 1, "problems": {
        "person:grace-hopper": ["input_sha256 does not match the bundle"],
        "person:alan-turing": ["uses a gendered pronoun"],
        "person:nobody": ["no bundle for this person"]}}
    assert load_bios(root / "brief-bios.yaml") == {"person:grace-hopper": earlier}

    assert merge_bios(root) == {"merged": 2, "rejected": 3, "rejections": {
        "person:grace-hopper": ["written from a different bundle"],
        "person:alan-turing": ["uses a gendered pronoun"],
        "person:nobody": ["no bundle for this person"]}}
    merged = yaml.safe_load((root / "brief-bios.yaml").read_text())["bios"]
    assert merged == [bio(ADA, "Ada Lovelace is a principal engineer.", hashes[ADA]), earlier]


def test_merge_bios_rejects_a_bio_without_authorship(tmp_path: Path) -> None:
    root = tmp_path / "synthesis"
    hashes = write_bundles(root)
    unsigned = bio(ADA, "Ada Lovelace is a principal engineer.", hashes[ADA])
    del unsigned["written_at"]
    (root / "bios" / "x.yaml").write_text(yaml.safe_dump({"bios": [unsigned]}))

    assert check_file(root, root / "bios" / "x.yaml")["problems"] == {
        ADA: ["missing ['written_at']"]}
    assert merge_bios(root)["rejected"] == 1


def test_load_kb_payloads_skips_derived_folders_but_not_underscore_handles(
        tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    (kb / "_graph").mkdir(parents=True)
    (kb / "_graph" / "stats.yaml").write_text("stats:\n  id: not-an-entity\n")
    (kb / "accounts" / "x").mkdir(parents=True)
    (kb / "accounts" / "x" / "_adalovelace.yaml").write_text(
        "softschema: {}\nsocial_account:\n  id: acct:x/_adalovelace\n  bio: dev infra\n")
    (kb / "people").mkdir()
    (kb / "people" / "eli.md").write_text(
        "---\ntitle: Eli\nperson:\n  id: person:eli\n  name: Eli Lovelace\n---\n# Eli\n")

    assert sorted(load_kb_payloads(kb)) == ["acct:x/_adalovelace", "person:eli"]


def test_prune_bios_drops_people_no_longer_in_the_kb(tmp_path: Path) -> None:
    root = tmp_path / "synthesis"
    hashes = write_bundles(root)
    kept = bio(ADA, "Ada Lovelace is a principal engineer.", hashes[ADA])
    gone = bio("person:hopper-joe", "Joe Hopper is an engineer.", "0" * 64)
    (root / "brief-bios.yaml").write_text(yaml.safe_dump({"bios": [kept, gone]}))

    assert prune_bios(root, {ADA}) == ["person:hopper-joe"]
    assert load_bios(root / "brief-bios.yaml") == {ADA: kept}
    assert prune_bios(root, {ADA}) == []


def test_historical_job_titles_remain_paired_with_their_listing() -> None:
    person = {"id": ADA, "name": "Ada Lovelace", "job_title": "Research Engineer",
              "listed_for": EVENT_2024, "affiliation_label": "Analytical Society",
              "affiliations": [{"organization": "org:acme", "current": True}],
              "participations": [{"event": EVENT_2024, "role": "speaker", "status": "confirmed"}]}
    bundle = person_bundle(person, None, ENTITIES)
    assert "job_title" not in bundle["facts"]
    assert bundle["facts"]["listed_role"] == {
        "title": "Research Engineer", "organization": "Analytical Society",
        "event": "GitHub Universe 2024"}
    bad = "Ada Lovelace is a Research Engineer at Acme."
    assert any("unsupported" in p for p in check_bio(bad, bundle, ["listed_role"]))
    good = ("The GitHub Universe 2024 listing describes Ada Lovelace as "
            "Research Engineer at Analytical Society.")
    assert check_bio(good, bundle, ["listed_role"]) == []
    assert "uses an event-listing title without its edition" in check_bio(
        "Ada Lovelace is a Research Engineer at Analytical Society.", bundle, ["listed_role"])
    person["affiliations"][0]["title"] = "Research Engineer"
    current = person_bundle(person, None, ENTITIES)
    assert check_bio(bad, current, ["current_affiliations"]) == []


def test_generated_bios_reject_contact_details() -> None:
    bundle = {"person": ADA, "facts": {"name": "Ada Lovelace", "job_title": "Engineer"}}
    for contact in [
        "@".join(["ada", "mail.co"]),
        "ada " + "@ github",
        "+49 30 " + "1234 5678",
        "123 Example Street",
    ]:
        assert "contains contact details" in check_bio(
            f"Ada Lovelace builds engines; contact: {contact}.", bundle, ["job_title"]
        )


def test_malformed_generated_entries_are_rejections(tmp_path: Path) -> None:
    root = tmp_path / "synthesis"
    hashes = write_bundles(root)
    entries = [
        None,
        {"person": ADA, "text": 7, "cites": ["job_title"]},
        bio(ADA, "Ada Lovelace builds engines.", hashes[ADA]),
    ]
    path = root / "bios" / "malformed.yaml"
    path.write_text(yaml.safe_dump({"bios": entries}))
    checked = check_file(root, path)
    assert checked["entries"] == 3 and checked["ok"] == 1
    assert len(checked["problems"]) == 2
    assert merge_bios(root)["rejected"] == 2
    assert list(load_bios(root / "brief-bios.yaml")) == [ADA]


def test_malformed_bundle_is_an_actionable_rejection(tmp_path: Path) -> None:
    root = tmp_path / "synthesis"
    hashes = write_bundles(root)
    bundle_path = root / "bundles" / "batch-01.jsonl"
    bundle_path.write_text(json.dumps({"person": ADA, "facts": [], "input_sha256": "0" * 64}))
    path = root / "bios" / "generated.yaml"
    valid = bio(ADA, "Ada Lovelace builds engines.", hashes[ADA])
    path.write_text(yaml.safe_dump({"bios": [valid]}))
    checked = check_file(root, path)
    assert checked["ok"] == 0 and len(checked["problems"]) == 2
    assert merge_bios(root)["rejected"] == 2


def test_generated_bios_do_not_assume_plain_hosted_addresses_are_account_ids() -> None:
    bundle = {"person": ADA, "facts": {"name": "Ada Lovelace", "job_title": "Engineer"}}
    for host in ("github.com", "mastodon.social"):
        text = "Ada Lovelace builds engines; " + "@".join(["synthetic-user", host])
        assert "contains contact details" in check_bio(text, bundle, ["job_title"])
