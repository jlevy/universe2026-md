from __future__ import annotations

import hashlib
import json
import multiprocessing
from pathlib import Path
from typing import Any

import pytest

from universe_kb.privacy import findings
from universe_kb.snapshot import Snapshot


def test_text_snapshot_is_sanitized_and_rewrite_preserves_provenance(tmp_path: Path) -> None:
    snapshot = Snapshot(tmp_path)
    address = "@".join(["ada", "mail.co"])
    text = f"<p>Contact:{address}; +49 30 " + "1234 5678; 123 Example Street</p>"
    snapshot.save_text("site/home.html", text, url="https://example.org/")
    assert not findings(tmp_path / "site")
    assert "Example Street" not in (tmp_path / "site/home.html").read_text()
    entry = dict(snapshot.entries["site/home.html"])
    (tmp_path / "site/home.html").write_text(text)
    assert snapshot.rewrite_text("site/home.html", text)
    saved = (tmp_path / "site/home.html").read_bytes()
    assert snapshot.entries["site/home.html"]["sha256"] == hashlib.sha256(saved).hexdigest()
    assert snapshot.entries["site/home.html"]["retrieved_at"] == entry["retrieved_at"]
    assert snapshot.entries["site/home.html"]["url"] == entry["url"]
    assert not snapshot.rewrite_text("site/home.html", saved.decode())


def _snapshot_writer(root: str, first: bool, saved: Any, finished: Any, identical: bool) -> None:
    snapshot = Snapshot(Path(root))
    if first:
        snapshot.save_json("first.json", {"value": 1}, url="https://example.org/first")
        snapshot.save_json("shared.json", {"value": 1}, url="https://example.org/first")
        saved.set()
        assert finished.wait(10)
        snapshot.write_manifest()
    else:
        assert saved.wait(10)
        snapshot.save_json("second.json", {"value": 2}, url="https://example.org/second")
        snapshot.save_json("shared.json", {"value": 1 if identical else 2},
                           url="https://example.org/second")
        snapshot.write_manifest()
        finished.set()


@pytest.mark.parametrize("identical", [False, True])
def test_concurrent_snapshot_writers_keep_distinct_paths_and_current_hash(
    tmp_path: Path, identical: bool
) -> None:
    context = multiprocessing.get_context("fork")
    saved, finished = context.Event(), context.Event()
    processes = [
        context.Process(target=_snapshot_writer,
                        args=(str(tmp_path), first, saved, finished, identical))
        for first in (True, False)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(15)
        if process.is_alive():
            process.terminate()
            process.join()
        assert process.exitcode == 0
    entries = json.loads((tmp_path / "manifest.json").read_text())["files"]
    assert set(entries) == {"first.json", "second.json", "shared.json"}
    for rel_path, entry in entries.items():
        data = (tmp_path / rel_path).read_bytes()
        assert entry["sha256"] == hashlib.sha256(data).hexdigest()
        assert entry["bytes"] == len(data)
    assert entries["shared.json"]["url"] == "https://example.org/second"
