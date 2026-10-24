"""
Guards for the contracts of the committed knowledge base: every model is closed, every
artifact names the `v2` contract for its envelope with `status: enforced`, and the stock
softschema CLI rejects a field the contract does not declare.
"""

from __future__ import annotations

import json
import os
import shutil
from functools import cache
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import BaseModel, ValidationError
from softschema.cli import main as softschema_cli

from universe_kb import models
from universe_kb.artifacts import STATUS
from universe_kb.models import CONTRACTS, NAMESPACE, VERSION
from universe_kb.schemas import artifact_paths, validate_kb

PIPELINE_DIR = Path(__file__).resolve().parents[1]
# The built knowledge base sits beside the pipeline, at the repository root.
REPO_DIR = PIPELINE_DIR.parent
KB_DIR = REPO_DIR / "kb"
SCHEMA_DIR = PIPELINE_DIR / "schemas"
ARTIFACTS = artifact_paths(KB_DIR)

# The C loader reads all of `kb/` in about two seconds; the pure-Python one takes ten.
_Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def read_document(path: Path) -> dict[str, Any]:
    """An artifact's YAML: the frontmatter of a Markdown file, or the whole YAML file."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        assert text.startswith("---\n"), path
        text = text[4:].split("\n---\n", 1)[0]
    return yaml.load(text, Loader=_Loader)


@cache
def kb_documents() -> list[tuple[Path, dict[str, Any]]]:
    """Every artifact in the committed `kb/` with its parsed YAML, read once per run."""
    return [(path, read_document(path)) for path in ARTIFACTS]


def stock_cli(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, dict[str, Any]]:
    """Run the stock `softschema` CLI in process and return its exit code and JSON report."""
    capsys.readouterr()
    code = softschema_cli(list(argv))
    return code, json.loads(capsys.readouterr().out)


def test_contracts_are_v2_and_artifacts_enforced() -> None:
    assert VERSION == "v2"
    assert STATUS == "enforced"
    for spec in CONTRACTS.values():
        assert spec.contract_id == f"{NAMESPACE}:{spec.model.__name__}/v2"


def test_every_model_forbids_undeclared_fields() -> None:
    # A model that derives from BaseModel directly, or reopens `extra`, would quietly
    # reopen its schema; every model in the module must be closed.
    open_models = [
        name for name, value in vars(models).items()
        if isinstance(value, type) and issubclass(value, BaseModel)
        and value.__module__ == models.__name__ and value.model_config.get("extra") != "forbid"
    ]
    assert open_models == []


def test_compiled_schemas_are_closed_and_kb_copies_match() -> None:
    assert sorted(p.name for p in (KB_DIR / "_schemas").iterdir()) == sorted(
        spec.schema_file for spec in CONTRACTS.values())
    for spec in CONTRACTS.values():
        compiled = SCHEMA_DIR / spec.schema_file
        schema = yaml.load(compiled.read_text(encoding="utf-8"), Loader=_Loader)
        assert schema["additionalProperties"] is False, spec.schema_file
        assert schema["x-softschema"]["contract"] == spec.contract_id
        # The build copies schemas/ into kb/_schemas/; a stale copy means a missed rebuild.
        assert (KB_DIR / "_schemas" / spec.schema_file).read_bytes() == compiled.read_bytes()


def test_every_kb_artifact_names_its_envelopes_v2_contract_and_is_enforced() -> None:
    assert ARTIFACTS
    problems: list[str] = []
    envelopes: set[str] = set()
    for path, document in kb_documents():
        rel = path.relative_to(KB_DIR).as_posix()
        meta = document.get("softschema") or {}
        spec = CONTRACTS.get(str(meta.get("envelope")))
        if spec is None:
            problems.append(f"{rel}: unknown envelope {meta.get('envelope')!r}")
            continue
        envelopes.add(spec.envelope)
        schema = os.path.relpath(KB_DIR / "_schemas" / spec.schema_file, path.parent)
        expected = {"contract": spec.contract_id, "schema": Path(schema).as_posix(),
                    "envelope": spec.envelope, "status": "enforced"}
        if meta != expected:
            problems.append(f"{rel}: softschema block {meta} != {expected}")
        if not str(meta.get("contract")).endswith("/v2"):
            problems.append(f"{rel}: contract {meta.get('contract')!r} is not v2")
        if not isinstance(document.get(spec.envelope), dict):
            problems.append(f"{rel}: no `{spec.envelope}` payload")
    assert not problems, "\n".join(problems[:20])
    assert envelopes == set(CONTRACTS)


def repair_sample() -> list[Path]:
    """The first and last artifact of each envelope, and every 500th artifact overall."""
    by_envelope: dict[str, list[Path]] = {}
    for path, document in kb_documents():
        by_envelope.setdefault(document["softschema"]["envelope"], []).append(path)
    sample = {p for paths in by_envelope.values() for p in (paths[0], paths[-1])}
    return sorted(sample | set(ARTIFACTS[::500]))


def test_softschema_repair_dry_run_changes_nothing_on_a_kb_sample(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The whole kb takes minutes; a sample across every envelope catches a writer that
    # emits YAML softschema would retype or repair. Run from the kb's parent directory,
    # the repository root, since softschema refuses schema pointers that escape the
    # working directory.
    monkeypatch.chdir(REPO_DIR)
    changed = {}
    for path in repair_sample():
        rel = path.relative_to(REPO_DIR).as_posix()
        code, report = stock_cli(capsys, "repair", "--dry-run", rel)
        if code != 0 or report["repairs"] or report["outcome"] != "valid":
            changed[rel] = report["repairs"] or report["outcome"]
    assert changed == {}


def copy_artifact(rel: str, root: Path) -> Path:
    """Copy one kb artifact, and the schema its pointer names, into `root/kb/`."""
    source = KB_DIR / rel
    target = root / "kb" / rel
    target.parent.mkdir(parents=True)
    shutil.copyfile(source, target)
    schema_rel = (Path(rel).parent / read_document(source)["softschema"]["schema"]).as_posix()
    schema_target = root / "kb" / os.path.normpath(schema_rel)
    schema_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(KB_DIR / os.path.normpath(schema_rel), schema_target)
    return target


def first_artifact(envelope: str) -> str:
    """The first artifact of an envelope, relative to `kb/`, so no test names a person."""
    return next(path.relative_to(KB_DIR).as_posix() for path, document in kb_documents()
                if document["softschema"]["envelope"] == envelope)


@pytest.mark.parametrize("envelope", ["session", "profile"])
def test_stock_cli_rejects_an_undeclared_top_level_field(
    envelope: str, tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rel = first_artifact(envelope)
    target = copy_artifact(rel, tmp_path)
    spec = CONTRACTS[envelope]
    monkeypatch.chdir(tmp_path)
    cli_path = f"kb/{rel}"

    code, report = stock_cli(capsys, "validate", cli_path)
    assert code == 0, report
    assert report["outcome"] == "valid"
    assert report["contract_id"] == spec.contract_id
    assert report["status"] == "enforced"

    text = target.read_text(encoding="utf-8")
    header = f"\n{envelope}:\n"
    assert text.count(header) == 1
    target.write_text(text.replace(header, f"{header}  undeclared_note: added by a test\n"),
                      encoding="utf-8")
    payload = read_document(target)[envelope]
    assert payload["undeclared_note"] == "added by a test"

    # Structural layer: the stock CLI binds only the compiled schema, which is closed.
    code, report = stock_cli(capsys, "validate", cli_path)
    assert code == 1
    assert report["outcome"] != "valid"
    assert report["structural"]["ok"] is False
    assert "undeclared_note" in json.dumps(report["structural"]["errors"])

    # Semantic layer: the Pydantic model is closed too, so `universe-kb validate` fails
    # the artifact on both layers.
    with pytest.raises(ValidationError, match="undeclared_note"):
        spec.model.model_validate(payload)
    result = validate_kb(tmp_path / "kb")
    assert (result["artifacts"], result["invalid"]) == (1, 1)
