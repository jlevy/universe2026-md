from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tarfile
from pathlib import Path
from typing import Any

import pytest

from universe_kb.artifacts import write_artifact
from universe_kb.models import Participation, Person, Source
from universe_kb.publish import build_site
from universe_kb.schemas import compile_schemas

REVISION = "a" * 40
SKILL = Path(__file__).resolve().parents[2] / ".agents/skills/universe2026-data"


def fixture_kb(root: Path) -> Path:
    kb = root / "source-kb"
    schemas = kb / "_schemas"
    compile_schemas(schemas)
    person = Person(
        id="person:example-owner", name="Example <em>Owner</em>",
        inclusion_basis="curated", github_resolution="absent",
        sources=[Source(system="curation", snapshot="curation/example.yaml")],
        participations=[Participation(event="event:github-universe-2026", role="speaker",
                                      status="confirmed")])
    write_artifact(kb, schemas, person, envelope="person", rel_path="people/example-owner.md",
                   title=person.name, body="Public professional example.\n")
    (kb / "README.md").write_text("# Example Knowledge Base\n")
    (kb / "_graph").mkdir()
    (kb / "_graph/nodes.jsonl").write_text(json.dumps({
        "id": person.id, "kind": "person", "name": person.name,
        "path": "people/example-owner.md"}) + "\n")
    (kb / "_graph/edges.jsonl").write_text("")
    (kb / "_search").mkdir()
    (kb / "_search/documents.jsonl").write_text(json.dumps({"id": person.id}) + "\n")
    return kb


def downloader() -> Any:
    spec = importlib.util.spec_from_file_location(
        "universe_data_download", SKILL / "scripts/download.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_static_package_preserves_bytes_schema_paths_and_deterministic_archives(
        tmp_path: Path) -> None:
    kb = fixture_kb(tmp_path)
    first, second = tmp_path / "site-one", tmp_path / "site-two"
    first.mkdir()
    manifest = build_site(kb, SKILL, first, REVISION)
    original = {p.relative_to(kb).as_posix(): p.read_bytes() for p in kb.rglob("*") if p.is_file()}
    assert {p.relative_to(first / "kb").as_posix(): p.read_bytes()
            for p in (first / "kb").rglob("*") if p.is_file()} == original
    archive = first / manifest["archive"]["path"]
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["archive"]["sha256"]
    assert archive.stat().st_size == manifest["archive"]["size"]
    with tarfile.open(archive) as packed:
        unpacked = {m.name.removeprefix("kb/"): content.read()
                    for m in packed.getmembers() if m.isfile()
                    if (content := packed.extractfile(m)) is not None}
    assert unpacked == original
    assert "../_schemas/" in original["people/example-owner.md"].decode()
    assert build_site(kb, SKILL, second, REVISION) == manifest
    assert (second / manifest["archive"]["path"]).read_bytes() == archive.read_bytes()
    assert (first / ".nojekyll").is_file()
    index = json.loads((first / "files.json").read_text())
    assert index["entities"][0]["path"] == "kb/people/example-owner.md"
    assert json.loads((first / "releases" / REVISION / "dataset.json").read_text()) == manifest
    html = (first / "index.html").read_text()
    assert "&lt;em&gt;Owner&lt;/em&gt;" in html and "<em>Owner</em>" not in html
    with tarfile.open(first / manifest["skill"]["path"]) as skill:
        assert {m.name for m in skill.getmembers() if m.isfile()} == {
            "universe2026-data/SKILL.md", "universe2026-data/scripts/download.py"}


def test_publication_rejects_nonpublic_inputs_links_invalid_records_and_existing_output(
        tmp_path: Path) -> None:
    kb = fixture_kb(tmp_path)
    output = tmp_path / "site"
    private = kb / ".env"
    private.write_text("example fixture, no credentials")
    with pytest.raises(ValueError, match="Non-public path"):
        build_site(kb, SKILL, output, REVISION)
    assert not output.exists()
    private.unlink()
    link = kb / "people/link.md"
    link.symlink_to(kb / "people/example-owner.md")
    with pytest.raises(ValueError, match="Symlinks"):
        build_site(kb, SKILL, output, REVISION)
    link.unlink()
    record = kb / "people/example-owner.md"
    record.write_text(record.read_text().replace(
        "inclusion_basis: curated", "inclusion_basis: invalid"))
    with pytest.raises(ValueError, match="KB validation failed"):
        build_site(kb, SKILL, output, REVISION)
    assert not output.exists()
    output.mkdir()
    (output / "keep.txt").write_text("user owned")
    with pytest.raises(ValueError, match="new or empty"):
        build_site(kb, SKILL, output, REVISION)
    assert (output / "keep.txt").read_text() == "user owned"


def test_downloader_verifies_remote_bytes_and_pins_before_publication(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    site = tmp_path / "site"
    manifest = build_site(fixture_kb(tmp_path), SKILL, site, REVISION)
    script = downloader()
    base = "https://dataset.example/"
    requested = []

    class Response(io.BytesIO):
        def geturl(self) -> str:
            return base

    responses = {
        base + f"releases/{REVISION}/dataset.json": json.dumps(manifest).encode(),
        base + manifest["archive"]["path"]: (site / manifest["archive"]["path"]).read_bytes()}

    def open_https(url: str) -> Response:
        requested.append(url)
        return Response(responses[url])

    monkeypatch.setattr(script, "_open_https", open_https)
    destination = tmp_path / "download"
    result = script.download_dataset(base + "dataset.json", destination, revision=REVISION,
                                     sha256=manifest["archive"]["sha256"])
    assert result["revision"] == REVISION
    assert (destination / "kb/people/example-owner.md").read_bytes() == (
        site / "kb/people/example-owner.md").read_bytes()
    assert (destination / "kb/_schemas").is_dir()
    requested.clear()
    with pytest.raises(ValueError, match="new or empty"):
        script.download_dataset(base + "dataset.json", destination, revision=REVISION)
    assert requested == []
    with pytest.raises(ValueError, match="pinned checksum"):
        script.download_dataset(base + "dataset.json", tmp_path / "wrong-pin", revision=REVISION,
                                sha256="0" * 64)
    assert not (tmp_path / "wrong-pin").exists()
    responses[base + manifest["archive"]["path"]] = b"corrupted archive"
    with pytest.raises(ValueError, match="verification"):
        script.download_dataset(base + "dataset.json", tmp_path / "corrupt", revision=REVISION)
    assert not (tmp_path / "corrupt").exists()
    with pytest.raises(ValueError, match="HTTPS"):
        script.download_dataset("http://dataset.example/dataset.json", tmp_path / "http")


def test_tar_preflight_rejects_unsafe_members_before_writing(tmp_path: Path) -> None:
    script = downloader()
    for number, (name, kind, link) in enumerate([
        ("../outside", tarfile.REGTYPE, ""), ("/kb/outside", tarfile.REGTYPE, ""),
        ("kb/../outside", tarfile.REGTYPE, ""), ("kb\\outside", tarfile.REGTYPE, ""),
        ("kb/link", tarfile.SYMTYPE, "/outside"),
        ("kb/link", tarfile.LNKTYPE, "kb/first"), ("kb/device", tarfile.CHRTYPE, ""),
        ("kb/first", tarfile.REGTYPE, "")]):
        archive = tmp_path / f"unsafe-{number}.tar.gz"
        with tarfile.open(archive, "w:gz") as packed:
            first = tarfile.TarInfo("kb/first")
            first.size = 2
            packed.addfile(first, io.BytesIO(b"ok"))
            entry = tarfile.TarInfo(name)
            entry.type, entry.linkname = kind, link
            packed.addfile(entry, io.BytesIO())
        destination = tmp_path / f"extract-{number}"
        with pytest.raises(ValueError, match="Unsafe archive member"):
            script.extract_archive(archive, destination)
        assert not destination.exists()
    assert not (tmp_path / "outside").exists()


def test_publication_rejects_a_skill_with_a_missing_linked_resource(tmp_path: Path) -> None:
    kb = fixture_kb(tmp_path)
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: universe2026-data\ndescription: Query the public dataset.\n---\n"
        "Read [download](scripts/download.py).\n")
    with pytest.raises(ValueError, match="resource is missing"):
        build_site(kb, skill, tmp_path / "site", REVISION)
    assert not (tmp_path / "site").exists()


def test_downloader_rejects_invalid_manifest_fields_before_archive_fetch(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = downloader()
    manifest = {"format_version": 1, "revision": REVISION, "totals": {"files": 1},
                "archive": {"path": f"archives/universe2026-kb-{REVISION}.tar.gz",
                            "size": 100, "sha256": "a" * 64}}
    bad = [dict(manifest, format_version=2), dict(manifest, revision="b" * 40),
           dict(manifest, totals={"files": -1}),
           dict(manifest, archive={**manifest["archive"], "path": "archives/../private.tar.gz"}),
           dict(manifest, archive={**manifest["archive"], "size": True}),
           dict(manifest, archive={**manifest["archive"], "sha256": "invalid"})]
    for number, invalid in enumerate(bad):
        requested = []

        class Response(io.BytesIO):
            def geturl(self) -> str:
                return "https://dataset.example/dataset.json"

        def open_https(url: str, requests: list[str] = requested,
                       payload: bytes = json.dumps(invalid).encode()) -> Response:
            requests.append(url)
            return Response(payload)

        monkeypatch.setattr(script, "_open_https", open_https)
        destination = tmp_path / f"invalid-{number}"
        with pytest.raises(ValueError):
            script.download_dataset("https://dataset.example/dataset.json", destination,
                                    revision=REVISION)
        assert len(requested) == 1
        assert not destination.exists()


def test_tar_metadata_is_bounded_before_parsing_or_writing(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = downloader()
    archive = tmp_path / "oversized-metadata.tar.gz"
    with tarfile.open(archive, "w:gz", format=tarfile.PAX_FORMAT,
                      pax_headers={"comment": "x" * (2 * 1024 * 1024)}) as packed:
        entry = tarfile.TarInfo("kb/README.md")
        entry.size = 2
        packed.addfile(entry, io.BytesIO(b"ok"))
    monkeypatch.setattr(script, "MAX_EXPANDED_BYTES", 1024)
    parsed = []
    original_open = script.tarfile.open

    def parse_tar(*args: Any, **kwargs: Any) -> Any:
        parsed.append(args[0])
        return original_open(*args, **kwargs)

    monkeypatch.setattr(script.tarfile, "open", parse_tar)
    destination = tmp_path / "extracted"
    with pytest.raises(ValueError, match="decompressed tar"):
        script.extract_archive(archive, destination)
    assert parsed == []
    assert not destination.exists()
    assert not list(tmp_path.glob(".universe-tar-*"))
