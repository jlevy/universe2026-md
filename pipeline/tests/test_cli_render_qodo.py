from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from universe_kb import cli
from universe_kb.bios import bundle_hash, load_bios


def test_bios_merge_reports_partial_rejection_as_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    synthesis = tmp_path / "synthesis"
    bundles = synthesis / "bundles"
    bundles.mkdir(parents=True)
    bundle = {"person": "person:example", "facts": {"name": "Example Person",
                                                    "job_title": "Engineer"}}
    digest = bundle_hash(bundle)
    (bundles / "batch-01.jsonl").write_text(json.dumps({**bundle, "input_sha256": digest}))
    submissions = synthesis / "bios"
    submissions.mkdir()
    accepted = {"person": "person:example", "text": "Example Person is an engineer.",
                "cites": ["job_title"], "input_sha256": digest,
                "written_by": "test-model", "written_at": "2026-10-24T00:00:00Z"}
    invalid = {**accepted, "person": "person:missing"}
    source = submissions / "example.yaml"
    source.write_text(yaml.safe_dump({"bios": [accepted, invalid]}))
    monkeypatch.setattr(cli, "SYNTHESIS_DIR", synthesis)

    status = cli.main(["bios-merge"])

    assert json.loads(capsys.readouterr().out) == {
        "merged": 1, "rejected": 1,
        "rejections": {"person:missing": ["no bundle for this person"]}}
    assert load_bios(synthesis / "brief-bios.yaml") == {"person:example": accepted}
    assert status == 1
    source.write_text(yaml.safe_dump({"bios": [accepted]}))
    assert cli.main(["bios-merge"]) == 0
    assert json.loads(capsys.readouterr().out)["rejected"] == 0


def test_page_body_renders_escaped_structured_content_without_duplicate_inline_links() -> None:
    from universe_kb.models import Image, Link, Page, PageSection
    from universe_kb.render import Renderer

    inline = "Read [Existing](https://example.org/existing) for **details**."
    page = Page(id="page:example.org/home", site="githubuniverse.com",
                url="https://example.org/home", title="Example page", sources=[], sections=[
                    PageSection(heading="Resources", text=inline, links=[
                        Link(kind="website", label="Existing", url="https://example.org/existing"),
                        Link(kind="website", label="Guide [draft] & details",
                             url="https://example.org/guide (draft)")],
                        images=[Image(url="https://example.org/image(1).png",
                                      alt="A [diagram] <one>")],
                        calls_to_action=[Link(kind="registration", label="Join [now]",
                                              url="https://example.org/join?label=<now>")])])

    body = Renderer({}).page_body(page)

    assert inline in body
    assert body.count("](https://example.org/existing)") == 1
    assert r"- [Guide \[draft\] &amp; details](<https://example.org/guide%20(draft)>)" in body
    assert r"![A \[diagram\] &lt;one&gt;](<https://example.org/image(1).png>)" in body
    assert r"- [Join \[now\]](<https://example.org/join?label=%3Cnow%3E>)" in body


def test_generated_index_links_the_media_export(tmp_path: Path) -> None:
    from universe_kb.render import Renderer

    Renderer({}).write_index(tmp_path, {"nodes": {}})

    assert "[media.yaml](media.yaml)" in (tmp_path / "README.md").read_text()


def bundle_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    kb = tmp_path / "kb"
    kb.mkdir()
    for slug, name in [("alpha", "Alpha Example"), ("beta", "Beta Example")]:
        (kb / f"{slug}.yaml").write_text(yaml.safe_dump({"person": {
            "id": f"person:{slug}", "name": name, "bio": "Builds example tools."}}))
    synthesis = tmp_path / "synthesis"
    bundles = synthesis / "bundles"
    bundles.mkdir(parents=True)
    (bundles / "batch-01.jsonl").write_text("previous first batch\n")
    (bundles / "batch-03.jsonl").write_text("previous third batch\n")
    monkeypatch.setattr(cli, "SYNTHESIS_DIR", synthesis)
    return kb, bundles


@pytest.mark.parametrize("failure_type", [OSError, KeyboardInterrupt])
def test_bundle_regeneration_preserves_previous_batches_on_write_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
    failure_type: type[BaseException],
) -> None:
    import argparse

    kb, bundles = bundle_workspace(tmp_path, monkeypatch)
    previous = {p.name: p.read_bytes() for p in bundles.iterdir()}
    write_text = Path.write_text

    def fail_second(path: Path, data: str, encoding: str | None = None,
                    errors: str | None = None, newline: str | None = None) -> int:
        if path.name == "batch-02.jsonl":
            raise failure_type("injected batch write failure")
        return write_text(path, data, encoding=encoding, errors=errors, newline=newline)

    monkeypatch.setattr(Path, "write_text", fail_second)
    with pytest.raises(failure_type, match="injected batch write failure"):
        cli.cmd_bio_bundles(argparse.Namespace(kb=kb, batch=1, all=True, event=None))

    assert {p.name: p.read_bytes() for p in bundles.iterdir()} == previous
    assert capsys.readouterr().out == ""
    assert list(bundles.parent.glob(".bio-bundles-*")) == []


def test_bundle_regeneration_publishes_complete_batches_and_removes_stale_ones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    kb, bundles = bundle_workspace(tmp_path, monkeypatch)

    assert cli.main(["--kb", str(kb), "bio-bundles", "--all", "--batch", "1"]) == 0

    assert sorted(p.name for p in bundles.iterdir()) == ["batch-01.jsonl", "batch-02.jsonl"]
    for name, person in [("batch-01.jsonl", "person:alpha"), ("batch-02.jsonl", "person:beta")]:
        bundle = json.loads((bundles / name).read_text())
        digest = bundle.pop("input_sha256")
        assert bundle["person"] == person
        assert digest == bundle_hash(bundle)
    assert json.loads(capsys.readouterr().out) == {
        "people": 2, "pruned": [], "to_write": 2, "batches": 2}
    assert cli.main(["--kb", str(kb), "bio-bundles", "--event", "event:missing"]) == 0
    assert list(bundles.iterdir()) == []
    assert json.loads(capsys.readouterr().out)["batches"] == 0


def test_bundle_regeneration_restores_previous_batches_when_publication_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    kb, bundles = bundle_workspace(tmp_path, monkeypatch)
    previous = {p.name: p.read_bytes() for p in bundles.iterdir()}
    rename = Path.rename

    def fail_publish(path: Path, target: Path | str) -> Path:
        if path.name.startswith(".bio-bundles-") and Path(target) == bundles:
            raise OSError("injected bundle publication failure")
        return rename(path, target)

    monkeypatch.setattr(Path, "rename", fail_publish)
    with pytest.raises(OSError, match="injected bundle publication failure"):
        cli.main(["--kb", str(kb), "bio-bundles", "--all", "--batch", "1"])

    assert {p.name: p.read_bytes() for p in bundles.iterdir()} == previous
    assert capsys.readouterr().out == ""
    assert list(bundles.parent.glob(".bio-bundles-*")) == []
    assert list(bundles.parent.glob(".kb-previous-bundles-*")) == []


def test_sanitize_raw_backfills_json_html_and_text_without_changing_provenance(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    import hashlib

    raw = tmp_path / "raw"
    raw.mkdir()
    contact = "@".join(["example", "mail.invalid"])
    contents = {
        "profile.json": json.dumps({"bio": f"Builds tools. Contact {contact}"}),
        "page.html": f"<html><body><p>Builds tools. Contact {contact}</p></body></html>",
        "notes.txt": f"Builds tools. Contact {contact}",
    }
    entries = {}
    for rel, text in contents.items():
        (raw / rel).write_text(text)
        entries[rel] = {"url": f"https://example.org/{rel}", "method": "GET",
                        "retrieved_at": "2026-10-24T00:00:00Z", "bytes": len(text.encode()),
                        "sha256": hashlib.sha256(text.encode()).hexdigest()}
    entries["missing.html"] = {"url": "https://example.org/missing"}
    manifest = raw / "manifest.json"
    manifest.write_text(json.dumps({"files": entries}))

    assert cli.main(["--raw", str(raw), "sanitize-raw"]) == 0

    assert json.loads(capsys.readouterr().out) == {
        "files": 4, "changed": ["notes.txt", "page.html", "profile.json"]}
    updated = json.loads(manifest.read_text())["files"]
    for rel in contents:
        text = (raw / rel).read_text()
        assert contact not in text
        assert "Builds tools." in text
        assert updated[rel]["bytes"] == len(text.encode())
        assert updated[rel]["sha256"] == hashlib.sha256(text.encode()).hexdigest()
        for key in ("url", "method", "retrieved_at"):
            assert updated[rel][key] == entries[rel][key]
    assert updated["page.html"]["sanitized_at"]
    assert updated["notes.txt"]["sanitized_at"]
    assert cli.main(["--raw", str(raw), "sanitize-raw"]) == 0
    assert json.loads(capsys.readouterr().out) == {"files": 4, "changed": []}
    assert json.loads(manifest.read_text())["files"] == updated
