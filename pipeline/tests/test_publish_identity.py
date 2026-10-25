from __future__ import annotations

import json
import re
import tarfile
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from universe_kb.artifacts import write_artifact
from universe_kb.graph import write_graph
from universe_kb.models import Event, EventDay, Facet, Organization, Source, Term
from universe_kb.publish import REPOSITORY_DIR, build_site
from universe_kb.schemas import compile_schemas

REVISION = "a" * 40


@pytest.fixture
def source_bundle(tmp_path: Path) -> tuple[Path, Path]:
    kb, skill = tmp_path / "kb", tmp_path / "skill"
    schemas = kb / "_schemas"
    compile_schemas(schemas)
    source = Source(system="curation", snapshot="curation/example.yaml")
    organization = Organization(id="org:example", name="Example", roles=["organizer"],
                                sources=[source])
    event = Event(
        id="event:example", name="Example Event", series="Example", edition="2026",
        organizer=organization.id, start="2026-10-28T09:00:00Z", end="2026-10-28T17:00:00Z",
        timezone="UTC", attendance_modes=["in_person"], url="https://event.example",
        days=[EventDay(id="day:2026-10-28", date="2026-10-28", label="Wednesday")],
        sources=[source])
    facet = Facet(id="topic", label="Topic", multi_valued=True,
                  terms=[Term(id="term:topic/example", label="Example", session_count=0)],
                  sources=[source])
    models: dict[str, tuple[str, BaseModel, str | None]] = {
        "organizations/example.md": ("organization", organization, organization.name),
        "events/example.md": ("event", event, event.name),
        "taxonomy/topic.yaml": ("facet", facet, None)}
    for path, (envelope, model, title) in models.items():
        write_artifact(kb, schemas, model, envelope=envelope, rel_path=path, title=title)
    write_graph(kb, models)
    (kb / "README.md").write_text(
        "# Example KB\n\n[Pipeline](../pipeline/README.md)\n"
        "[Policy](../docs/data-policy.md)\n[License](../LICENSE)\n")
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: universe2026-data\ndescription: Read the public dataset.\n---\n")
    return kb, skill


def read_nodes(kb: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (kb / "_graph/nodes.jsonl").read_text().splitlines()]


@pytest.mark.parametrize("defect", ["id", "kind", "path", "missing-artifact", "missing-day",
                                    "missing-term", "extra-day", "extra-term", "duplicate"])
def test_publication_rejects_graph_claims_not_supported_by_artifacts(
        source_bundle: tuple[Path, Path], tmp_path: Path, defect: str) -> None:
    kb, skill = source_bundle
    nodes = read_nodes(kb)
    event = next(node for node in nodes if node["kind"] == "event")
    if defect in {"id", "kind", "path"}:
        event[defect] = {"id": "event:wrong", "kind": "person",
                         "path": "organizations/example.md"}[defect]
    elif defect.startswith("missing-"):
        kind = {"missing-artifact": "organization", "missing-day": "day",
                "missing-term": "term"}[defect]
        nodes = [node for node in nodes if node["kind"] != kind]
    elif defect == "duplicate":
        nodes.append(dict(event))
    else:
        kind = defect.removeprefix("extra-")
        nodes.append({"id": f"{kind}:extra", "kind": kind, "name": "Extra",
                      "path": "events/example.md" if kind == "day" else "taxonomy/topic.yaml"})
    (kb / "_graph/nodes.jsonl").write_text("".join(json.dumps(node) + "\n" for node in nodes))
    output = tmp_path / "site"
    with pytest.raises(ValueError, match=r"[Gg]raph"):
        build_site(kb, skill, output, REVISION)
    assert not output.exists()


@pytest.mark.parametrize("field", ["node_total", "nodes"])
def test_publication_rejects_stale_graph_counts(
        source_bundle: tuple[Path, Path], tmp_path: Path, field: str) -> None:
    kb, skill = source_bundle
    stats_path = kb / "_graph/stats.json"
    stats = json.loads(stats_path.read_text())
    stats[field] = 999 if field == "node_total" else {"person": 5}
    stats_path.write_text(json.dumps(stats))
    with pytest.raises(ValueError, match="Graph"):
        build_site(kb, skill, tmp_path / "site", REVISION)
    assert not (tmp_path / "site").exists()


def test_publication_includes_embedded_identities_and_guides_without_changing_kb(
        source_bundle: tuple[Path, Path], tmp_path: Path) -> None:
    kb, skill = source_bundle
    output = tmp_path / "site"
    original = {p.relative_to(kb).as_posix(): p.read_bytes() for p in kb.rglob("*") if p.is_file()}
    manifest = build_site(kb, skill, output, REVISION)
    assert manifest["totals"]["entities"] == 5
    assert manifest["totals"]["by_kind"] == {
        "organization": 1, "event": 1, "day": 1, "facet": 1, "term": 1}
    index = json.loads((output / "files.json").read_text())
    paths = {node["id"]: node["path"] for node in index["entities"]}
    assert paths["day:2026-10-28"] == paths["event:example"] == "kb/events/example.md"
    assert paths["term:topic/example"] == paths["facet:topic"] == "kb/taxonomy/topic.yaml"
    assert {p.relative_to(output / "kb").as_posix(): p.read_bytes()
            for p in (output / "kb").rglob("*") if p.is_file()} == original
    for target in re.findall(r"\]\(([^)]+)\)", (output / "kb/README.md").read_text()):
        assert (output / "kb" / target).is_file()
    for relative in ("LICENSE", "docs/data-policy.md"):
        assert (output / relative).read_bytes() == (REPOSITORY_DIR / relative).read_bytes()
    guide = (output / "pipeline/README.md").read_text()
    targets = re.findall(r"\]\(([^)]+)\)", guide)
    base = f"https://github.com/jlevy/universe2026-md/blob/{REVISION}/"
    assert base + "docs/data-policy.md" in targets
    assert base + "LICENSE" in targets
    assert all(target.startswith(("https://", "#")) for target in targets)
    with tarfile.open(output / manifest["archive"]["path"]) as archive:
        files = {entry.name.removeprefix("kb/") for entry in archive if entry.isfile()}
        assert files == set(original)


def test_empty_output_is_removed_only_at_publication_for_windows_rename(
        source_bundle: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    kb, skill = source_bundle
    output = tmp_path / "site"
    output.mkdir()
    rename = Path.rename

    def windows_rename(source: Path, destination: Path) -> Path:
        if destination.exists():
            raise FileExistsError(destination)
        assert (source / "dataset.json").is_file()
        return rename(source, destination)

    monkeypatch.setattr(Path, "rename", windows_rename)
    build_site(kb, skill, output, REVISION)
    assert (output / "dataset.json").is_file()


def test_publication_preserves_output_that_gains_user_content_during_staging(
        source_bundle: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from universe_kb import publish

    kb, skill = source_bundle
    output = tmp_path / "site"
    output.mkdir()
    archive = publish._archive

    def concurrent_file(root: Path, target: Path, prefix: str) -> dict[str, Any]:
        result = archive(root, target, prefix)
        (output / "keep.txt").write_text("user owned")
        return result

    monkeypatch.setattr(publish, "_archive", concurrent_file)
    with pytest.raises(OSError):
        build_site(kb, skill, output, REVISION)
    assert [path.name for path in output.iterdir()] == ["keep.txt"]
    assert (output / "keep.txt").read_text() == "user owned"


def test_publication_rejects_symlinked_allowlisted_guides(
        source_bundle: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from universe_kb import publish

    kb, skill = source_bundle
    repository = tmp_path / "repository"
    (repository / "pipeline").mkdir(parents=True)
    (repository / "docs").mkdir()
    (repository / "pipeline/README.md").write_text("# Public guide\n")
    (repository / "docs/data-policy.md").symlink_to(kb / "README.md")
    monkeypatch.setattr(publish, "REPOSITORY_DIR", repository)
    with pytest.raises(ValueError, match="Symlinked public guide"):
        build_site(kb, skill, tmp_path / "site", REVISION)
    assert not (tmp_path / "site").exists()
