"""
Brief bios: one or two neutral sentences per person, written from cited evidence.

The build assembles an evidence bundle per person from what the knowledge base already
holds (event bio, LinkedIn headline and about, GitHub and other profile bios, website,
affiliations, sessions, expertise, writing). Each fact has a key. Claude subagents read
bundles and write bios that cite the keys they used; the bios live in
`synthesis/brief-bios.yaml` with the hash of the bundle they were written from, so a bio
whose evidence has since changed is marked stale rather than silently trusted.

`check_bio` holds the writing rules every bio must pass.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from universe_kb.privacy import STREET_ADDRESS, contact_findings, redact
from universe_kb.sensitive import categories

MAX_BIO_CHARS = 320
MAX_FIELD_CHARS = 900
MAX_LIST_ITEMS = 6
STATED_INTERESTS = {"curated"}
# Bios never assume pronouns; they use the person's name or none.
PRONOUNS = re.compile(r"\b(he|she|him|her|his|hers|himself|herself)\b", re.IGNORECASE)
# A sentence end, not an initial ("Kent C. Dodds") or abbreviation ("Sr.", "Corp.").
SENTENCE_END = re.compile(r"(?<!\b[A-Z])(?<!\bSr)(?<!\bJr)(?<!\bDr)(?<!\bSt)(?<!\bCorp)"
                          r"(?<!\bInc)(?<!\bvs)(?<!\be\.g)(?<!\bi\.e)(?<!\.[A-Z])[.!?](\s|$)")


def _clip(text: Any, limit: int = MAX_FIELD_CHARS) -> str | None:
    if not isinstance(text, str) or not text.strip():
        return None
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"


def person_bundle(person: dict[str, Any], profile: dict[str, Any] | None,
                  entities: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """
    The facts a bio may use, keyed so the bio can cite them. `entities` maps IDs to
    payloads for the accounts, websites, organizations, sessions and events referenced.
    """
    def name_of(ref: str) -> str:
        entity = entities.get(ref) or {}
        return entity.get("name") or entity.get("title") or ref.split(":", 1)[-1]

    facts: dict[str, Any] = {"name": person["name"]}
    if person.get("job_title") and person.get("listed_for"):
        facts["listed_role"] = {
            "title": person["job_title"], "organization": person.get("affiliation_label"),
            "event": name_of(person["listed_for"])}
    current = [a for a in person.get("affiliations") or [] if a.get("current")]
    past = [a for a in person.get("affiliations") or [] if not a.get("current")]
    if current:
        facts["current_affiliations"] = sorted({
            f"{a['title']} at {name_of(a['organization'])}" if a.get("title")
            else name_of(a["organization"]) for a in current})[:MAX_LIST_ITEMS]
    if past:
        facts["past_affiliations"] = sorted({name_of(a["organization"])
                                             for a in past})[:MAX_LIST_ITEMS]
    if _clip(person.get("bio")):
        facts["event_bio"] = _clip(person.get("bio"))
    facts["participation"] = sorted({
        f"{p['role']} ({p['status'].replace('_', ' ')}) at {name_of(p['event'])}"
        for p in person.get("participations") or []})
    talks = [entities.get(s["session"]) for s in person.get("sessions") or []]
    if any(talks):
        facts["sessions"] = [f"{t['title']} ({name_of(t['event'])})"
                             for t in talks if t][:MAX_LIST_ITEMS]
    for ref in person.get("accounts") or []:
        account = entities.get(ref) or {}
        platform = "github" if ref.startswith("gh:") else account.get("platform", "other")
        for key in ("headline", "bio"):
            value = _clip(account.get(key) if platform != "github" or key == "bio"
                          else None)
            if value:
                facts[f"{platform}_{key}"] = value
        if platform == "github" and _clip(account.get("profile_readme")):
            facts["github_readme"] = _clip(account.get("profile_readme"), 600)
        if account.get("location") and "location" not in facts:
            facts["location"] = account["location"]
    for ref in person.get("websites") or []:
        site = entities.get(ref) or {}
        # An employer's site says nothing about the person.
        if site.get("kind") == "company":
            continue
        text = " — ".join(t for t in (site.get("title"), site.get("description")) if t)
        if text:
            facts.setdefault("websites", []).append(_clip(text, 300))
    if profile:
        for key, label in (("expertise", "expertise"), ("technologies", "technologies"),
                           ("recognitions", "recognitions"), ("interests", "interests"),
                           ("programming_languages", "languages")):
            # Inferred interests restate facts the bundle already holds (sessions,
            # repositories, posts); only interests a person or researcher stated count.
            values = [c["label"] for c in profile.get(key) or []
                      if key != "interests" or c.get("basis") in STATED_INTERESTS]
            if values[:MAX_LIST_ITEMS]:
                facts[label] = values[:MAX_LIST_ITEMS]
        if profile.get("location") and "location" not in facts:
            facts["location"] = profile["location"]
        for key in ("publications", "patents"):
            titles = [_clip(p["title"], 160) for p in profile.get(key) or []][:3]
            if titles:
                facts[key] = titles
        education = [e["school"] for e in profile.get("education") or []][:3]
        if education:
            facts["education"] = education
        writing = [w["title"][:120] for w in profile.get("recent_writing") or []
                   if w.get("channel") in {"blog", "linkedin"}][:4]
        if writing:
            facts["recent_writing"] = writing
        repos = [w["repository"].removeprefix("repo:") for w in profile.get("open_source") or []
                 if w.get("relation") == "owner"][:4]
        if repos:
            facts["open_source"] = repos
    return {"person": person["id"], "facts": facts}


def load_kb_payloads(kb_dir: Path) -> dict[str, dict[str, Any]]:
    """Every entity payload in a built kb, keyed by ID, as `bio-bundles` reads them."""
    payloads: dict[str, dict[str, Any]] = {}
    for path in sorted(kb_dir.rglob("*")):
        # Skip the derived `_graph/` and `_schemas/` folders, not files such as an
        # account whose handle starts with "_".
        if path.suffix not in {".md", ".yaml"} or path.name == "README.md" or any(
                part.startswith("_") for part in path.relative_to(kb_dir).parts[:-1]):
            continue
        text = path.read_text()
        document = yaml.safe_load(text.split("---\n")[1] if path.suffix == ".md" else text)
        envelope = next(k for k in document if k not in {"softschema", "title"})
        entity = document[envelope]
        if isinstance(entity, dict) and isinstance(entity.get("id"), str):
            payloads[entity["id"]] = entity
    return payloads


def bundle_hash(bundle: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(bundle, sort_keys=True).encode()).hexdigest()


def check_bio(text: str, bundle: dict[str, Any], cites: list[str]) -> list[str]:
    """The writing rules a bio must pass; returns the problems found."""
    problems = []
    if not isinstance(text, str):
        problems.append("bio text must be a string")
    if (
        not isinstance(bundle, dict)
        or not isinstance(bundle.get("facts"), dict)
        or not isinstance(bundle["facts"].get("name"), str)
        or not bundle["facts"]["name"].strip()
    ):
        problems.append("bundle must contain a facts mapping with a name")
    if not isinstance(cites, list) or not all(isinstance(c, str) for c in cites):
        problems.append("cites must be a list of strings")
    if problems:
        return problems
    if contact_findings(text) or redact(text) != text or STREET_ADDRESS.search(text):
        problems.append("contains contact details")
    role = bundle["facts"].get("listed_role")
    if isinstance(role, dict) and role.get("title"):
        title = str(role["title"])
        org = str(role.get("organization") or "")
        # A title at another current employer needs that exact pairing in a current
        # source; independently sourced titles and employers cannot be combined.
        allowed = [str(a) for a in bundle["facts"].get("current_affiliations", [])
                   if re.match(rf"{re.escape(title)}\s+(?:at|of)\s+", str(a), re.I)]
        if org:
            allowed.append(f"{title} at {org}")
            allowed.append(f"{title} of {org}")
        for role_match in re.finditer(rf"\b{re.escape(title)}\s+(?:at|of)\s+", text, re.I):
            if not any(re.match(re.escape(a) + r"(?![\w-])", text[role_match.start():], re.I)
                       for a in allowed):
                problems.append("combines a listing title with an unsupported employer")
                break
        current_pair = any(str(a).casefold() in text.casefold()
                           for a in bundle["facts"].get("current_affiliations", [])
                           if re.match(rf"{re.escape(title)}\s+(?:at|of)\s+", str(a), re.I))
        year = re.search(r"\b20\d{2}\b", str(role.get("event") or ""))
        if (title.casefold() in text.casefold() and not current_pair and year
                and year.group() not in text):
            problems.append("uses an event-listing title without its edition")
    if len(text) > MAX_BIO_CHARS:
        problems.append(f"longer than {MAX_BIO_CHARS} characters")
    if len(SENTENCE_END.findall(text)) > 2:
        problems.append("more than two sentences")
    family = bundle["facts"]["name"].split()[-1]
    # Remove the person's own name first, so "Kaiming He" is not read as a pronoun.
    unnamed = re.sub(rf"\b{re.escape(bundle['facts']['name'])}\b", "", text)
    if PRONOUNS.search(unnamed):
        problems.append("uses a gendered pronoun")
    if categories(unnamed) - {"symbol"}:
        problems.append(f"states a sensitive attribute ({', '.join(sorted(categories(unnamed)))})")
    if family.lower() not in text.lower():
        problems.append("does not name the person")
    unknown = [c for c in cites if c not in bundle["facts"]]
    if unknown:
        problems.append(f"cites unknown facts: {unknown}")
    if not cites:
        problems.append("cites nothing")
    return problems


def _submission_entries(path: Path) -> list[Any]:
    try:
        document = yaml.safe_load(path.read_text())
    except yaml.YAMLError:
        return [None]
    if document is None:
        return []
    if not isinstance(document, dict) or not isinstance(document.get("bios"), list):
        return [None]
    return document["bios"]


def _entry_problem(entry: Any) -> str | None:
    if not isinstance(entry, dict):
        return "entry must be a mapping with typed bio fields"
    for key in ("person", "text", "input_sha256"):
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            return f"{key} must be a nonempty string"
    if not isinstance(entry.get("cites"), list) or not all(
        isinstance(c, str) for c in entry["cites"]
    ):
        return "cites must be a list of strings"
    for key in ("written_by", "written_at"):
        if key in entry and not isinstance(entry[key], str):
            return f"{key} must be a string"
    return None


def _load_bundles(synthesis_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    bundles: dict[str, dict[str, Any]] = {}
    errors: dict[str, list[str]] = {}
    for path in sorted((synthesis_dir / "bundles").glob("batch-*.jsonl")):
        for index, line in enumerate(path.read_text().splitlines(), 1):
            try:
                bundle = json.loads(line)
            except json.JSONDecodeError:
                bundle = None
            if (
                not isinstance(bundle, dict)
                or not isinstance(bundle.get("person"), str)
                or not isinstance(bundle.get("facts"), dict)
                or not isinstance(bundle["facts"].get("name"), str)
                or not bundle["facts"]["name"].strip()
                or not isinstance(bundle.get("input_sha256"), str)
            ):
                errors[f"bundle:{path.name}:{index}"] = [
                    "bundle must contain typed person, facts and hash fields"
                ]
            else:
                bundles[bundle["person"]] = bundle
    return bundles, errors


def load_bios(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    return {
        entry["person"]: entry
        for entry in _submission_entries(path)
        if isinstance(entry, dict)
        and isinstance(entry.get("person"), str)
        and isinstance(entry.get("text"), str)
    }


def _write_bios(path: Path, bios: dict[str, dict[str, Any]]) -> None:
    document = {"bios": [bios[k] for k in sorted(bios)]}
    header = ("# Brief bios written by Claude subagents from each person's evidence bundle.\n"
              "# Generated by `universe-kb bios-merge`; regenerate stale ones rather than "
              "editing.\n")
    path.write_text(
        header + yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=100))


def drop_bios(synthesis_dir: Path, person_ids: set[str]) -> list[str]:
    """Delete the bios of `person_ids`, such as people removed at their request."""
    path = synthesis_dir / "brief-bios.yaml"
    bios = load_bios(path)
    gone = sorted(set(bios) & person_ids)
    if gone:
        _write_bios(path, {k: v for k, v in bios.items() if k not in person_ids})
    return gone


def prune_bios(synthesis_dir: Path, person_ids: set[str]) -> list[str]:
    """Drop bios of people no longer in the kb (renamed or merged); returns their IDs."""
    path = synthesis_dir / "brief-bios.yaml"
    bios = load_bios(path)
    gone = sorted(set(bios) - person_ids)
    if gone:
        _write_bios(path, {k: v for k, v in bios.items() if k in person_ids})
    return gone


def merge_bios(synthesis_dir: Path) -> dict[str, Any]:
    """
    Merge subagent output (`synthesis/bios/*.yaml`) into `synthesis/brief-bios.yaml`.
    Each bio is checked against the bundle it was written from; failures are reported,
    not merged, so they can be rewritten.
    """
    bundles, bundle_errors = _load_bundles(synthesis_dir)
    merged = load_bios(synthesis_dir / "brief-bios.yaml")
    rejected: dict[str, list[str]] = dict(bundle_errors)
    for path in sorted((synthesis_dir / "bios").glob("*.yaml")):
        for index, entry in enumerate(_submission_entries(path), 1):
            if problem := _entry_problem(entry):
                rejected[f"entry:{path.name}:{index}"] = [problem]
                continue
            bundle = bundles.get(entry["person"])
            if bundle is None:
                rejected[entry.get("person", "?")] = ["no bundle for this person"]
                continue
            problems = check_bio(entry.get("text", ""), bundle, entry.get("cites") or [])
            if entry.get("input_sha256") != bundle["input_sha256"]:
                problems.append("written from a different bundle")
            missing = [k for k in ("written_by", "written_at") if not entry.get(k)]
            if missing:
                problems.append(f"missing {missing}")
            if problems:
                rejected[entry["person"]] = problems
                continue
            merged[entry["person"]] = {
                "person": entry["person"], "text": " ".join(entry["text"].split()),
                "cites": entry["cites"], "written_by": entry["written_by"],
                "written_at": entry["written_at"], "input_sha256": entry["input_sha256"]}
    _write_bios(synthesis_dir / "brief-bios.yaml", merged)
    return {"merged": len(merged), "rejected": len(rejected),
            "rejections": dict(list(rejected.items())[:20])}


def check_file(synthesis_dir: Path, path: Path) -> dict[str, Any]:
    """Check one subagent output file against its bundles, without merging anything."""
    bundles, bundle_errors = _load_bundles(synthesis_dir)
    entries = _submission_entries(path)
    problems: dict[str, list[str]] = dict(bundle_errors)
    for index, entry in enumerate(entries, 1):
        if problem := _entry_problem(entry):
            problems[f"entry:{path.name}:{index}"] = [problem]
            continue
        bundle = bundles.get(entry.get("person", ""))
        if bundle is None:
            problems[entry.get("person", "?")] = ["no bundle for this person"]
            continue
        found = check_bio(entry.get("text", ""), bundle, entry.get("cites") or [])
        if entry.get("input_sha256") != bundle["input_sha256"]:
            found.append("input_sha256 does not match the bundle")
        missing = [k for k in ("written_by", "written_at") if not entry.get(k)]
        if missing:
            found.append(f"missing {missing}")
        if found:
            problems[entry["person"]] = found
    return {
        "entries": len(entries),
        "ok": max(0, len(entries) - len(problems)),
        "problems": problems,
    }
