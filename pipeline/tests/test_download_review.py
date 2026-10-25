"""Downloader deployment redirects and destination publication preserve their contracts."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tarfile
from pathlib import Path
from typing import Any

import pytest

REVISION = "a" * 40
README = b"# Public fixture knowledge base\n"
ARCHIVE_PATH = f"archives/universe2026-kb-{REVISION}.tar.gz"


def downloader() -> Any:
    path = (Path(__file__).resolve().parents[2]
            / ".agents/skills/universe2026-data/scripts/download.py")
    spec = importlib.util.spec_from_file_location("review_download", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def payload() -> tuple[bytes, bytes]:
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as archive:
        entry = tarfile.TarInfo("kb/README.md")
        entry.size = len(README)
        archive.addfile(entry, io.BytesIO(README))
    content = stream.getvalue()
    manifest = {"format_version": 1, "revision": REVISION, "totals": {"files": 1},
                "archive": {"path": ARCHIVE_PATH, "size": len(content),
                            "sha256": hashlib.sha256(content).hexdigest()}}
    return json.dumps(manifest).encode(), content


class Response(io.BytesIO):
    def __init__(self, data: bytes, url: str) -> None:
        super().__init__(data)
        self.url = url

    def geturl(self) -> str:
        return self.url


def test_archives_follow_the_final_deployment_for_root_and_pinned_manifests(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = downloader()
    manifest, archive = payload()
    original = "https://alias.example/old/dataset.json"
    final_root = "https://cdn.example/deploy/v2/"
    for revision in (None, REVISION):
        requested: list[str] = []
        suffix = f"releases/{revision}/dataset.json" if revision else "dataset.json"
        selected_url = f"https://alias.example/old/{suffix}"
        final_url = final_root + suffix

        def open_https(url: str, selected: str = selected_url, final: str = final_url,
                       requests: list[str] = requested) -> Response:
            requests.append(url)
            if url == selected:
                return Response(manifest, final)
            assert url == final_root + ARCHIVE_PATH
            return Response(archive, url)

        monkeypatch.setattr(script, "_open_https", open_https)
        destination = tmp_path / (revision or "current")
        result = script.download_dataset(original, destination, revision=revision)
        assert result["revision"] == REVISION
        assert requested == [selected_url, final_root + ARCHIVE_PATH]
        assert (destination / "kb/README.md").read_bytes() == README
        assert (destination / "dataset.json").read_bytes() == manifest


def test_existing_empty_destination_works_when_rename_cannot_replace_it(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = downloader()
    manifest, archive = payload()
    base = "https://dataset.example/"
    destination = tmp_path / "download"
    destination.mkdir()
    original_rename = Path.rename
    publications: list[Path] = []

    def windows_rename(source: Path, target: Path) -> Path:
        if target.exists():
            raise FileExistsError("Windows cannot rename over an existing directory")
        publications.append(target)
        return original_rename(source, target)

    def open_https(url: str) -> Response:
        return Response(manifest if url.endswith("dataset.json") else archive, url)

    monkeypatch.setattr(script, "_open_https", open_https)
    monkeypatch.setattr(Path, "rename", windows_rename)
    script.download_dataset(base + "dataset.json", destination)
    assert publications == [destination]
    assert (destination / "kb/README.md").read_bytes() == README
    assert (destination / "dataset.json").read_bytes() == manifest


def test_publication_refuses_contents_added_to_an_accepted_empty_destination(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = downloader()
    manifest, archive = payload()
    base = "https://dataset.example/"
    destination = tmp_path / "download"
    destination.mkdir()
    user_file = destination / "keep.txt"
    requested: list[str] = []

    def open_https(url: str) -> Response:
        requested.append(url)
        if url.endswith("dataset.json"):
            return Response(manifest, url)
        user_file.write_bytes(b"User data added during download")
        return Response(archive, url)

    monkeypatch.setattr(script, "_open_https", open_https)
    with pytest.raises(OSError):
        script.download_dataset(base + "dataset.json", destination)
    assert user_file.read_bytes() == b"User data added during download"
    assert list(destination.iterdir()) == [user_file]
    assert not list(tmp_path.glob(".download-*"))
    requested.clear()
    with pytest.raises(ValueError, match="new or empty"):
        script.download_dataset(base + "dataset.json", destination)
    assert requested == []
