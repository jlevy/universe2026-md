#!/usr/bin/env python3
"""Download a public Universe KB release, verify it and publish a safe local copy."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import shutil
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_MANIFEST = "https://jlevy.github.io/universe2026-md/dataset.json"
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_EXPANDED_BYTES = 1024 * 1024 * 1024
MAX_MEMBERS = 50_000
CHUNK_BYTES = 1024 * 1024
TIMEOUT_SECONDS = 60


def _https(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use a public HTTPS URL without embedded credentials")
    return url


class HttpsRedirects(HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str,
                         headers: Any, newurl: str) -> Any:
        return super().redirect_request(req, fp, code, msg, headers, _https(newurl))


def _open_https(url: str) -> Any:
    return build_opener(HttpsRedirects()).open(
        Request(_https(url), headers={"User-Agent": "universe2026-data/1"}),
        timeout=TIMEOUT_SECONDS)


def extract_archive(archive_path: Path, destination: Path) -> int:
    """Bound decompression before parsing tar metadata, then preflight every member."""
    with tempfile.TemporaryDirectory(prefix=".universe-tar-", dir=archive_path.parent) as work:
        expanded_path = Path(work) / "dataset.tar"
        expanded = 0
        with gzip.open(archive_path, "rb") as compressed, expanded_path.open("xb") as stream:
            while chunk := compressed.read(min(CHUNK_BYTES, MAX_EXPANDED_BYTES - expanded + 1)):
                expanded += len(chunk)
                if expanded > MAX_EXPANDED_BYTES:
                    raise ValueError("Archive exceeds the decompressed tar size limit")
                stream.write(chunk)
        with tarfile.open(expanded_path, "r:") as archive:
            members = []
            names: dict[str, bool] = {}
            total = 0
            for member in archive:
                path = PurePosixPath(member.name)
                if (path.is_absolute() or not path.parts or path.parts[0] != "kb"
                        or any(p in {".", ".."} or "\\" in p or ":" in p for p in path.parts)
                        or member.name.rstrip("/") != path.as_posix()
                        or not (member.isfile() or member.isdir())
                        or (path.as_posix() == "kb" and not member.isdir())
                        or path.as_posix() in names or member.size < 0):
                    raise ValueError(f"Unsafe archive member: {member.name}")
                names[path.as_posix()] = member.isdir()
                members.append(member)
                total += member.size
                if len(members) > MAX_MEMBERS or total > MAX_EXPANDED_BYTES:
                    raise ValueError("Archive exceeds the extraction limits")
            if not members or not any(member.isfile() for member in members):
                raise ValueError("Archive contains no KB files")
            for member in members:
                for parent in PurePosixPath(member.name).parents:
                    if parent.as_posix() in names and not names[parent.as_posix()]:
                        raise ValueError(f"Archive file is also a parent: {parent}")
            for member in members:
                target = destination / member.name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    content = archive.extractfile(member)
                    if content is None:
                        raise ValueError(f"Missing archive content: {member.name}")
                    with content, target.open("xb") as stream:
                        shutil.copyfileobj(content, stream)
            return sum(member.isfile() for member in members)


def download_dataset(manifest_url: str, destination: Path, *, revision: str | None = None,
                     sha256: str | None = None) -> dict[str, Any]:
    """Stage a checksum-verified release beside the caller's chosen destination."""
    _https(manifest_url)
    if revision is not None and not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("revision must be a full lowercase Git commit SHA")
    if sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise ValueError("sha256 must be a lowercase SHA-256 digest")
    destination = destination.absolute()
    empty_destination = destination.exists()
    if destination.is_symlink() or (empty_destination and (
            not destination.is_dir() or any(destination.iterdir()))):
        raise ValueError("Destination must be a new or empty directory; choose a separate revision")
    base_url = urljoin(manifest_url, "./")
    # A pinned manifest still describes paths from the public site's root.
    selected_url = (urljoin(base_url, f"releases/{revision}/dataset.json")
                    if revision else manifest_url)
    with _open_https(selected_url) as response:
        final_manifest_url = _https(response.geturl())
        content = response.read(MAX_MANIFEST_BYTES + 1)
    if len(content) > MAX_MANIFEST_BYTES:
        raise ValueError("Dataset manifest exceeds the size limit")
    manifest = json.loads(content)
    if not isinstance(manifest, dict) or manifest.get("format_version") != 1:
        raise ValueError("Unsupported dataset manifest format")
    actual_revision = manifest.get("revision")
    if (not isinstance(actual_revision, str)
            or not re.fullmatch(r"[0-9a-f]{40}", actual_revision)
            or (revision is not None and actual_revision != revision)):
        raise ValueError("Dataset revision does not match the requested commit")
    # Release manifests keep root-relative paths even after changing deployment hosts.
    release_suffix = f"/releases/{actual_revision}/dataset.json"
    base_url = urljoin(final_manifest_url, "../../" if urlparse(
        final_manifest_url).path.endswith(release_suffix) else "./")
    totals = manifest.get("totals")
    if (not isinstance(totals, dict) or type(totals.get("files")) is not int
            or not 0 < totals["files"] < MAX_MEMBERS):
        raise ValueError("Invalid dataset file count")
    archive = manifest.get("archive")
    if not isinstance(archive, dict):
        raise ValueError("Dataset manifest is missing the archive")
    path, digest, size = archive.get("path"), archive.get("sha256"), archive.get("size")
    if (not isinstance(path, str) or not re.fullmatch(r"archives/[A-Za-z0-9._/-]+", path)
            or any(p in {".", ".."} for p in PurePosixPath(path).parts)
            or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or type(size) is not int or not 0 < size <= MAX_ARCHIVE_BYTES):
        raise ValueError("Invalid archive path, checksum or size in dataset manifest")
    if sha256 is not None and sha256 != digest:
        raise ValueError("Manifest archive checksum does not match the pinned checksum")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
            prefix=f".{destination.name}-", dir=destination.parent) as work:
        archive_path = Path(work) / "dataset.tar.gz"
        computed = hashlib.sha256()
        received = 0
        with _open_https(urljoin(base_url, path)) as response, archive_path.open("wb") as stream:
            _https(response.geturl())
            while chunk := response.read(CHUNK_BYTES):
                received += len(chunk)
                if received > size:
                    raise ValueError("Downloaded archive is larger than its declared size")
                stream.write(chunk)
                computed.update(chunk)
        if received != size or computed.hexdigest() != digest:
            raise ValueError("Downloaded archive failed size or SHA-256 verification")
        staged = Path(work) / "dataset"
        staged.mkdir()
        if extract_archive(archive_path, staged) != totals["files"]:
            raise ValueError("Extracted file count does not match the dataset manifest")
        (staged / "dataset.json").write_bytes(content)
        if empty_destination:
            # Windows cannot replace a directory; rmdir refuses any newly added content.
            destination.rmdir()
        staged.rename(destination)
    return {"revision": actual_revision, "sha256": digest, "totals": totals}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST,
                        help="Public site-root dataset.json URL")
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--revision", help="Require a specific full Git commit SHA")
    parser.add_argument("--sha256", help="Require an independently recorded archive checksum")
    args = parser.parse_args(argv)
    try:
        result = download_dataset(args.manifest, args.destination,
                                  revision=args.revision, sha256=args.sha256)
    except (OSError, ValueError, tarfile.TarError) as error:
        parser.exit(1, f"download: {error}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
