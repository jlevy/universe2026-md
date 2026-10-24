from __future__ import annotations

from pathlib import Path

import pytest

from universe_kb.build import Built, write_kb


def test_failed_final_rename_restores_previous_kb_and_preserves_a_new_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_rename = Path.rename
    for concurrent in (False, True):
        root = tmp_path / str(concurrent)
        kb = root / "kb"
        kb.mkdir(parents=True)
        (kb / "marker").write_text("old")
        schemas = root / "schemas"
        schemas.mkdir()

        def fail_final(source: Path, target: Path | str, *,
                       destination: Path = kb, publish_new: bool = concurrent) -> Path:
            if (source.name.startswith(".kb-") and not source.name.startswith(".kb-previous-")
                    and Path(target) == destination):
                if publish_new:
                    destination.mkdir()
                    (destination / "marker").write_text("new")
                raise OSError("injected publication failure")
            return original_rename(source, target)

        with monkeypatch.context() as patch:
            patch.setattr(Path, "rename", fail_final)
            with pytest.raises(OSError, match="injected publication failure"):
                write_kb(Built(), kb, schemas)
        assert (kb / "marker").read_text() == ("new" if concurrent else "old")
        if concurrent:
            (recovery,) = root.glob(".kb-previous-kb-*")
            assert (recovery / "marker").read_text() == "old"
