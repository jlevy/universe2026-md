from __future__ import annotations

import multiprocessing
from pathlib import Path

import pytest

from universe_kb.publication import publish_directory


def test_failed_publish_restores_old_tree_and_does_not_remove_other_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "kb"
    destination.mkdir()
    (destination / "marker").write_text("old")
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "marker").write_text("new")
    recovery = tmp_path / ".kb-previous-kb-unrelated"
    recovery.mkdir()
    (recovery / "marker").write_text("other recovery")
    rename = Path.rename

    def fail_final(source: Path, target: Path | str) -> Path:
        if source == staging:
            raise OSError("injected final rename failure")
        return rename(source, target)

    monkeypatch.setattr(Path, "rename", fail_final)
    with pytest.raises(OSError, match="injected final rename failure"):
        publish_directory(staging, destination)
    assert (destination / "marker").read_text() == "old"
    assert (recovery / "marker").read_text() == "other recovery"


def test_overlapping_publishers_wait_for_failed_writer_rollback(tmp_path: Path) -> None:
    context = multiprocessing.get_context("fork")
    at_final = context.Event()
    release = context.Event()
    second_started = context.Event()
    second_final = context.Event()
    destination = tmp_path / "kb"
    destination.mkdir()
    (destination / "marker").write_text("old")
    first, second = tmp_path / "first", tmp_path / "second"
    for path, label in ((first, "first"), (second, "second")):
        path.mkdir()
        (path / "marker").write_text(label)

    def publish_first() -> None:
        rename = Path.rename

        def fail_final(source: Path, target: Path | str) -> Path:
            if source == first:
                at_final.set()
                if not release.wait(10):
                    raise RuntimeError("second publisher never started")
                raise OSError("injected final rename failure")
            return rename(source, target)

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(Path, "rename", fail_final)
            try:
                publish_directory(first, destination)
            except OSError:
                return
        raise AssertionError("first publisher should fail")

    def publish_second() -> None:
        rename = Path.rename

        def observe_final(source: Path, target: Path | str) -> Path:
            if source == second:
                second_final.set()
            return rename(source, target)

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(Path, "rename", observe_final)
            second_started.set()
            publish_directory(second, destination)

    first_process = context.Process(target=publish_first)
    second_process = context.Process(target=publish_second)
    first_process.start()
    try:
        assert at_final.wait(10)
        second_process.start()
        assert second_started.wait(10)
        assert not second_final.wait(0.2)
        release.set()
        first_process.join(10)
        second_process.join(10)
        assert first_process.exitcode == 0
        assert second_process.exitcode == 0
        assert (destination / "marker").read_text() == "second"
        assert not list(tmp_path.glob(".kb-previous-*"))
    finally:
        release.set()
        for process in (first_process, second_process):
            if process.pid is not None and process.is_alive():
                process.terminate()
                process.join()
