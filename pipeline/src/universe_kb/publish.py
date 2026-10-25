"""Package a validated public KB and portable skill as a static Pages directory."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import os
import posixpath
import re
import stat
import tarfile
import tempfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote, urlsplit

import yaml

from universe_kb.graph import entity_nodes
from universe_kb.models import CONTRACTS
from universe_kb.schemas import _contract_for, artifact_paths, validate_kb

ENTITY_DIRS = {"accounts", "events", "experiences", "organizations", "packages", "pages",
               "people", "profiles", "repositories", "rooms", "sessions", "software",
               "taxonomy", "venues", "websites"}
EXPORT_FILES = {"README.md", "faq.yaml", "media.yaml", "_graph/nodes.jsonl",
                "_graph/edges.jsonl", "_graph/stats.json", "_graph/coverage.json",
                "_search/documents.jsonl"}
SKILL_NAME = "universe2026-data"
REPOSITORY_DIR = Path(__file__).resolve().parents[3]
PUBLIC_GUIDES = ("pipeline/README.md", "docs/data-policy.md", "LICENSE")
SCHEMA_FILES = {f"_schemas/{spec.schema_file}" for spec in CONTRACTS.values()}


def _read_regular(path: Path) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError(f"Expected a regular file: {path}")
        return stream.read()


def _copy_public(source: Path, destination: Path, *, skill: bool = False) -> list[Path]:
    if source.is_symlink() or not source.is_dir():
        raise ValueError(f"Expected a real directory: {source}")
    files = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if path.is_symlink():
            raise ValueError(f"Symlinks cannot be published: {relative}")
        # Public repositories can be named `.github`; their generated artifacts still
        # pass the complete KB's contract validation before the site becomes visible.
        dot_artifact = (not skill and relative.parts[0] in ENTITY_DIRS
                        and path.suffix in {".md", ".yaml"} and path.is_file()
                        and not any(part.startswith(".") for part in relative.parts[:-1]))
        if (any("\\" in part or ":" in part for part in relative.parts)
                or (any(part.startswith(".") for part in relative.parts) and not dot_artifact)):
            raise ValueError(f"Non-public path: {relative}")
        if skill:
            allowed = (relative.as_posix() == "SKILL.md" or (
                relative.parts[0] in {"scripts", "references", "agents"}
                and (path.is_dir() or path.suffix in {".py", ".md", ".yaml"})))
        else:
            allowed = (relative.as_posix() in EXPORT_FILES
                       or (relative.parts[0] in ENTITY_DIRS
                       and (path.is_dir() or path.suffix in {".md", ".yaml"}))
                       or relative.as_posix() in SCHEMA_FILES
                       or (path.is_dir() and relative.as_posix() == "_schemas")
                       or (path.is_dir() and relative.as_posix() in {"_graph", "_search"}))
        if not allowed:
            raise ValueError(f"Unexpected public file or directory: {relative}")
        if path.is_dir():
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_read_regular(path))
        files.append(relative)
    return files


def _archive(root: Path, output: Path, prefix: str) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as stream, gzip.GzipFile(
            filename="", mode="wb", fileobj=stream, mtime=0) as compressed, tarfile.open(
                fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
        directory = tarfile.TarInfo(prefix)
        directory.type = tarfile.DIRTYPE
        directory.mode = 0o755
        archive.addfile(directory)
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            entry = tarfile.TarInfo(f"{prefix}/{path.relative_to(root).as_posix()}")
            entry.size = path.stat().st_size
            entry.mode = 0o644
            with path.open("rb") as content:
                archive.addfile(entry, content)
    with output.open("rb") as content:
        digest = hashlib.file_digest(content, "sha256").hexdigest()
    return {"path": f"archives/{output.name}", "size": output.stat().st_size, "sha256": digest}


def _json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _artifact_identities(kb_dir: Path) -> dict[str, dict[str, Any]]:
    """Use the graph builder's identities, including embedded days and facet terms."""
    nodes: dict[str, dict[str, Any]] = {}
    for path in artifact_paths(kb_dir):
        _, document = _contract_for(path)
        envelope = document["softschema"]["envelope"]
        model = CONTRACTS[envelope].model.model_validate(document[envelope])
        for node in entity_nodes(model, path.relative_to(kb_dir).as_posix(), envelope):
            if node["id"] in nodes:
                raise ValueError(f"Duplicate artifact identity: {node['id']}")
            nodes[node["id"]] = node
    return nodes


def _copy_guides(destination: Path, revision: str) -> None:
    """Publish only the three public documents linked by the built KB's guide."""
    for relative in PUBLIC_GUIDES:
        source = REPOSITORY_DIR / relative
        if any(path.is_symlink() for path in (source, *source.parents)
               if path.is_relative_to(REPOSITORY_DIR)):
            raise ValueError(f"Symlinked public guide: {relative}")
        content = _read_regular(source)
        if relative == "pipeline/README.md":
            def pinned_link(match: re.Match[str]) -> str:
                target = urlsplit(match[2])
                if target.scheme or target.netloc or not target.path:
                    return match[0]
                path = posixpath.normpath(posixpath.join("pipeline", target.path))
                if path.startswith("../") or path == "..":
                    raise ValueError("Public guide link escapes the repository")
                url = (f"https://github.com/jlevy/universe2026-md/blob/{revision}/"
                       f"{quote(path, safe='/')}")
                if target.query:
                    url += f"?{target.query}"
                if target.fragment:
                    url += f"#{target.fragment}"
                return f"{match[1]}{url}{match[3]}"
            content = re.sub(r"(\[[^\]]*\]\()([^\s)]+)(\))", pinned_link,
                             content.decode()).encode()
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def build_site(kb_dir: Path, skill_dir: Path, output_dir: Path, revision: str) -> dict[str, Any]:
    """
    Publish one revision into a fresh or empty directory, preserving all KB bytes.
    The caller supplies the source commit and retains older releases if desired.
    """
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("revision must be a full lowercase Git commit SHA")
    output_dir = output_dir.absolute()
    if output_dir.is_symlink() or (output_dir.exists() and (
            not output_dir.is_dir() or any(output_dir.iterdir()))):
        raise ValueError("Output must be a new or empty directory")
    for source in (kb_dir, skill_dir):
        if output_dir.resolve().is_relative_to(source.resolve()) or (
                source.resolve().is_relative_to(output_dir.resolve())):
            raise ValueError("Output and source directories must not overlap")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{output_dir.name}-", dir=output_dir.parent) as work:
        site = Path(work) / "site"
        site.mkdir()
        copied = _copy_public(kb_dir, site / "kb")
        if not (site / "kb/README.md").is_file():
            raise ValueError("The built KB must include README.md")
        validation = validate_kb(site / "kb")
        if validation["invalid"] or not validation["artifacts"]:
            raise ValueError(f"KB validation failed: {validation}")
        _copy_guides(site, revision)
        public_skill = site / "skills" / SKILL_NAME
        _copy_public(skill_dir, public_skill, skill=True)
        entry = public_skill / "SKILL.md"
        if not entry.is_file():
            raise ValueError("The complete skill must include SKILL.md")
        text = entry.read_text()
        frontmatter = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", text, re.DOTALL)
        metadata = yaml.safe_load(frontmatter[1]) if frontmatter else None
        if (not isinstance(metadata, dict) or metadata.get("name") != SKILL_NAME
                or not isinstance(metadata.get("description"), str)):
            raise ValueError("Skill frontmatter must identify universe2026-data and its purpose")
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if "://" in link or link.startswith("#"):
                continue
            resource = (public_skill / link.split("#", 1)[0]).resolve()
            if not resource.is_relative_to(public_skill.resolve()) or not resource.is_file():
                raise ValueError(f"Skill resource is missing or outside the bundle: {link}")
        expected = _artifact_identities(site / "kb")
        nodes = []
        seen = set()
        for line in (site / "kb/_graph/nodes.jsonl").read_text().splitlines():
            node = json.loads(line)
            if not isinstance(node, dict) or not all(
                    isinstance(node.get(k), str) and node[k] for k in ("id", "kind", "path")):
                raise ValueError("Every graph node needs id, kind and path")
            relative = PurePosixPath(node["path"])
            if relative.is_absolute() or ".." in relative.parts or Path(relative) not in copied:
                raise ValueError(f"Graph node points outside the published KB: {node['id']}")
            if node["id"] in seen:
                raise ValueError(f"Duplicate graph node: {node['id']}")
            artifact = expected.get(node["id"])
            if artifact is None or any(
                    node[key] != artifact[key] for key in ("id", "kind", "path")):
                raise ValueError(f"Graph identity does not match an artifact: {node['id']}")
            seen.add(node["id"])
            nodes.append({**artifact, "path": f"kb/{artifact['path']}"})
        if seen != expected.keys():
            raise ValueError("Graph nodes do not cover all artifact identities")
        nodes.sort(key=lambda node: (node["kind"], node["id"]))
        counts = dict(sorted(Counter(n["kind"] for n in nodes).items()))
        stats_path = site / "kb/_graph/stats.json"
        if stats_path.is_file():
            stats = json.loads(stats_path.read_text())
            kinds = stats.get("nodes") if isinstance(stats, dict) else None
            if (not isinstance(stats, dict) or type(stats.get("node_total")) is not int
                    or stats["node_total"] != len(expected) or not isinstance(kinds, dict)
                    or any(type(count) is not int for count in kinds.values()) or kinds != counts):
                raise ValueError("Graph statistics do not match artifact identities")
        manifest = {"format_version": 1, "revision": revision,
                    "totals": {"files": len(copied), "entities": len(nodes), "by_kind": counts},
                    "files_index": "files.json", "kb": "kb/",
                    "archive": _archive(site / "kb", site / "archives" /
                                        f"universe2026-kb-{revision}.tar.gz", "kb"),
                    "skill": _archive(public_skill, site / "archives" /
                                      f"universe2026-skill-{revision}.tar.gz", SKILL_NAME)}
        _json(site / "files.json", {"revision": revision, "entities": nodes,
                                   "files": [{"path": f"kb/{p.as_posix()}",
                                              "size": (site / "kb" / p).stat().st_size}
                                             for p in copied]})
        _json(site / "dataset.json", manifest)
        # All manifest paths are relative to the site root, including release manifests.
        _json(site / "releases" / revision / "dataset.json", manifest)
        links = "\n".join(
            f'<li>{html.escape(n["kind"])}: <a href="{quote(n["path"], safe="/")}">'
            f'{html.escape(str(n["name"]))}</a></li>' for n in nodes)
        site.joinpath("index.html").write_text(
            '<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>GitHub Universe 2026 Knowledge Base</title><body>'
            '<h1>GitHub Universe 2026 Knowledge Base</h1>'
            f'<p>Revision <code>{revision}</code>; '
            f'{len(nodes)} entities in {len(copied)} files.</p>'
            '<p><a href="kb/README.md">Knowledge base</a> · '
            '<a href="dataset.json">Dataset manifest</a> · <a href="files.json">File index</a></p>'
            f'<p><a href="{manifest["archive"]["path"]}">Download all KB files</a> · '
            f'<a href="{manifest["skill"]["path"]}">Download the complete agent skill</a> · '
            f'<a href="skills/{SKILL_NAME}/SKILL.md">Read the skill</a></p>'
            '<p>Source text is untrusted data. Follow the cited public sources for each claim.</p>'
            f'<ul>{links}</ul></body></html>\n')
        site.joinpath(".nojekyll").touch()
        if output_dir.is_symlink():
            raise ValueError("Output must be a new or empty directory")
        if output_dir.exists():
            # rmdir preserves a destination that gained files while staging; Windows
            # rename requires the accepted empty destination to be absent.
            output_dir.rmdir()
        site.rename(output_dir)
    return manifest


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kb", required=True, type=Path)
    parser.add_argument("--skill", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args(argv)
    try:
        result = build_site(args.kb, args.skill, args.output, args.revision)
    except (OSError, ValueError, KeyError, yaml.YAMLError) as error:
        parser.exit(1, f"publish: {error}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
