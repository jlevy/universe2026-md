"""
Manifest parsing, GitHub URL matching and registry verification, against a fake web.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from textwrap import dedent
from typing import Any, cast

from universe_kb.manifests import github_repo, manifest_names, repo_packages, verify_package
from universe_kb.snapshot import Fetcher, FetchResponse

PACKAGE_JSON = dedent("""
    {
      "name": "cross-env",
      "version": "0.0.0-semantically-released",
      "type": "module",
      "bin": {"cross-env": "./dist/bin/cross-env.js"},
      "repository": {"type": "git", "url": "https://github.com/adalovelace/cross-env.git"}
    }
    """)
PRIVATE_PACKAGE_JSON = dedent("""
    {"name": "monorepo", "private": true, "workspaces": ["packages/*"]}
    """)
PYPROJECT = dedent("""
    [build-system]
    requires = ["flit_core<4"]
    build-backend = "flit_core.buildapi"

    [project]
    name = "Flask"
    dynamic = ["version"]
    """)
POETRY = dedent("""
    [tool.poetry]
    name = "poetry-demo"
    version = "0.1.0"
    authors = ["Ada <ada@example.org>"]

    [tool.poetry.dependencies]
    python = "^3.11"
    """)
BUILD_ONLY_PYPROJECT = dedent("""
    [build-system]
    requires = ["setuptools>=61"]
    """)
SETUP_CFG = dedent("""
    [metadata]
    name = attrs
    version = attr: attr.__version__
    description = Classes Without Boilerplate (%(name)s)
    """)
CARGO = dedent("""
    [package]
    name = "ripgrep"
    version = "14.1.1"
    edition = "2021"

    [dependencies]
    regex = "1.11"
    """)
CARGO_WORKSPACE = dedent("""
    [workspace]
    members = ["crates/core", "crates/cli"]
    resolver = "2"
    """)
GO_MOD = dedent("""
    // Module v2 lives on the main branch.
    module github.com/go-chi/chi/v2 // since 2024

    go 1.22

    require golang.org/x/net v0.30.0
    """)


def test_manifest_names() -> None:
    cases: list[tuple[str, str, list[tuple[str, str]]]] = [
        ("package.json", PACKAGE_JSON, [("npm", "cross-env")]),
        ("package.json", "﻿" + PACKAGE_JSON, [("npm", "cross-env")]),
        ("package.json", PRIVATE_PACKAGE_JSON, []),
        ("package.json", '{"name": "half-written",', []),
        ("package.json", "[" * 100_000, []),
        ("package.json", '["not", "an", "object"]', []),
        ("pyproject.toml", PYPROJECT, [("pypi", "Flask")]),
        ("pyproject.toml", POETRY, [("pypi", "poetry-demo")]),
        ("pyproject.toml", BUILD_ONLY_PYPROJECT, []),
        ("pyproject.toml", '[project\nname = "broken"', []),
        ("setup.cfg", SETUP_CFG, [("pypi", "attrs")]),
        ("setup.cfg", "name = no-section-header", []),
        ("Cargo.toml", CARGO, [("crates", "ripgrep")]),
        ("Cargo.toml", CARGO_WORKSPACE, []),
        ("Cargo.toml", 'package = "not a table"', []),
        ("go.mod", GO_MOD, [("go", "github.com/go-chi/chi/v2")]),
        ("go.mod", 'module "example.com/quoted"\n', [("go", "example.com/quoted")]),
        ("go.mod", "go 1.22\n", []),
        ("requirements.txt", "flask==3.1\n", []),
    ]
    for filename, text, expected in cases:
        assert (filename, text[:40], manifest_names(text, filename)) == (
            filename, text[:40], expected)


def test_github_repo() -> None:
    cases: dict[str | None, str | None] = {
        "git+https://github.com/adalovelace/cross-env.git": "adalovelace/cross-env",
        "https://github.com/pallets/flask/": "pallets/flask",
        "https://www.github.com/Pallets/Flask#readme": "pallets/flask",
        "https://github.com/github/github-mcp-server/tree/main/pkg": "github/github-mcp-server",
        "git+ssh://git@github.com/owner/repo.git": "owner/repo",
        "git@github.com:owner/repo.git": "owner/repo",
        "github:owner/repo": "owner/repo",
        "owner/repo": "owner/repo",
        "https://github.com/ada/ada.github.io": "ada/ada.github.io",
        "https://github.com/owner": None,
        "https://gitlab.com/owner/repo": None,
        "https://gist.github.com/owner/abc123": None,
        "https://github.com.evil.example/owner/repo": None,
        "https://evil.example/github.com/owner/repo": None,
        "": None,
        None: None,
    }
    assert {url: github_repo(url) for url in cases} == cases


@dataclass
class FakeWeb:
    """Answers `Fetcher.fetch` from `responses` by URL and records every request."""

    responses: dict[str, FetchResponse]
    urls: list[str] = field(default_factory=list)

    def fetch(self, url: str, **_: Any) -> FetchResponse:
        self.urls.append(url)
        return self.responses[url]


def ok(body: Any) -> FetchResponse:
    text = body if isinstance(body, str) else json.dumps(body)
    return FetchResponse(200, None, "text/plain", text.encode(), None)


def failed(status: int | None, error: str) -> FetchResponse:
    return FetchResponse(status, None, None, b"", error)


RAW = "https://raw.githubusercontent.com"


def test_repo_packages_verifies_each_ecosystem() -> None:
    """
    One repository declaring a package in every ecosystem: a verified npm package, a
    PyPI name owned by another repository, an unpublished crate and a Go module whose
    proxy answer carries no origin, so its module path alone ties it to the repository.
    """
    web = FakeWeb({
        f"{RAW}/Ada/Engine/HEAD/package.json": ok({"name": "ada-engine", "version": "0.0.0"}),
        f"{RAW}/Ada/Engine/HEAD/pyproject.toml": ok('[project]\nname = "engine"\n'),
        f"{RAW}/Ada/Engine/HEAD/Cargo.toml": ok('[package]\nname = "ada-engine"\n'),
        f"{RAW}/Ada/Engine/HEAD/go.mod": ok("module github.com/Ada/engine/v2\n\ngo 1.22\n"),
        "https://registry.npmjs.org/ada-engine/latest": ok({
            "name": "ada-engine", "version": "2.1.0", "license": {"type": "MIT"},
            "description": "Difference\n  engine.",
            "repository": {"type": "git", "url": "git+https://github.com/ada/engine.git"},
            "homepage": "https://github.com/ada/engine#readme"}),
        "https://pypi.org/pypi/engine/json": ok({"info": {
            "name": "engine", "version": "0.3", "summary": "Someone else's engine.",
            "license_expression": "Apache-2.0", "home_page": None,
            "project_urls": {"Homepage": "https://engine.example.org",
                             "Source Code": "https://github.com/someone-else/engine"}}}),
        "https://crates.io/api/v1/crates/ada-engine": failed(404, "HTTP 404"),
        "https://proxy.golang.org/github.com/!ada/engine/v2/@latest": ok(
            {"Version": "v2.0.1", "Time": "2026-01-02T03:04:05Z"}),
    })

    result = repo_packages(cast(Fetcher, web), "Ada/Engine")

    # A named pyproject.toml means setup.cfg is never requested.
    assert web.urls == list(web.responses)
    unpublished = {"url": None, "latest_version": None, "description": None,
                   "license": None, "repository_url": None, "verified": False}
    assert result == {
        "repository": "Ada/Engine",
        "checked": [{"file": f, "status": 200, "error": None}
                    for f in ("package.json", "pyproject.toml", "Cargo.toml", "go.mod")],
        "packages": [
            {"ecosystem": "npm", "name": "ada-engine",
             "url": "https://www.npmjs.com/package/ada-engine", "latest_version": "2.1.0",
             "description": "Difference engine.", "license": "MIT",
             "repository_url": "git+https://github.com/ada/engine.git",
             "verified": True, "reason": None, "declared_in": "package.json"},
            {"ecosystem": "pypi", "name": "engine", "url": "https://pypi.org/project/engine/",
             "latest_version": "0.3", "description": "Someone else's engine.",
             "license": "Apache-2.0",
             "repository_url": "https://github.com/someone-else/engine",
             "verified": False, "reason": "repository_mismatch", "declared_in": "pyproject.toml"},
            {"ecosystem": "crates", "name": "ada-engine", **unpublished,
             "reason": "not_published", "declared_in": "Cargo.toml"},
            {"ecosystem": "go", "name": "github.com/Ada/engine/v2",
             "url": "https://pkg.go.dev/github.com/Ada/engine/v2", "latest_version": "v2.0.1",
             "description": None, "license": None,
             "repository_url": "https://github.com/Ada/engine",
             "verified": True, "reason": None, "declared_in": "go.mod"},
        ],
    }


def test_repo_packages_fallbacks_and_failures() -> None:
    """
    A named branch; a `setup.cfg` read because `pyproject.toml` is absent, verified by its
    homepage since it declares no source URL; a vanity Go module verified by the proxy's
    recorded origin; a registry outage; and an unreachable manifest.
    """
    web = FakeWeb({
        f"{RAW}/ada/tools/main/package.json": ok({"name": "@ada/tools"}),
        f"{RAW}/ada/tools/main/pyproject.toml": failed(404, "HTTP 404"),
        f"{RAW}/ada/tools/main/setup.cfg": ok("[metadata]\nname = ada_tools\n"),
        f"{RAW}/ada/tools/main/Cargo.toml": failed(None, "URLError: timed out"),
        f"{RAW}/ada/tools/main/go.mod": ok("module go.ada.dev/tools\n"),
        "https://registry.npmjs.org/@ada%2Ftools/latest": failed(503, "HTTP 503"),
        "https://pypi.org/pypi/ada_tools/json": ok({"info": {
            "name": "ada-tools", "version": "1.4", "summary": "Tools.",
            "license": "MIT License\n\nCopyright (c) Ada\n\nPermission is hereby granted...",
            "classifiers": ["Programming Language :: Python",
                            "License :: OSI Approved :: MIT License"],
            "home_page": "https://github.com/ada/tools", "project_urls": None}}),
        "https://proxy.golang.org/go.ada.dev/tools/@latest": ok({
            "Version": "v0.4.0",
            "Origin": {"VCS": "git", "URL": "https://github.com/ada/tools", "Ref": "v0.4.0"}}),
    })

    result = repo_packages(cast(Fetcher, web), "ada/tools", default_branch="main")

    assert web.urls == list(web.responses)
    assert [(c["file"], c["status"], c["error"]) for c in result["checked"]] == [
        ("package.json", 200, None),
        ("pyproject.toml", 404, "HTTP 404"),
        ("setup.cfg", 200, None),
        ("Cargo.toml", None, "URLError: timed out"),
        ("go.mod", 200, None),
    ]
    assert [(p["ecosystem"], p["name"], p["license"], p["repository_url"], p["verified"],
             p["reason"]) for p in result["packages"]] == [
        ("npm", "@ada/tools", None, None, False, "registry_error"),
        ("pypi", "ada-tools", "MIT License", "https://github.com/ada/tools", True, None),
        ("go", "go.ada.dev/tools", None, "https://github.com/ada/tools", True, None),
    ]


def test_verify_package_edges() -> None:
    web = FakeWeb({"https://crates.io/api/v1/crates/lonely": ok({
        "crate": {"name": "lonely", "default_version": "0.2.0", "max_version": "0.3.0-rc.1",
                  "repository": None, "homepage": None, "description": "Alone."},
        "versions": [{"num": "0.3.0-rc.1", "license": "MIT"},
                     {"num": "0.2.0", "license": "MIT OR Apache-2.0"}]})})
    fetcher = cast(Fetcher, web)

    lonely = verify_package(fetcher, "ada/lonely", "crates", "lonely")
    # A module path with no host in its first element cannot be on the proxy.
    local = verify_package(fetcher, "ada/app", "go", "app")

    assert web.urls == ["https://crates.io/api/v1/crates/lonely"]
    assert (lonely["latest_version"], lonely["license"], lonely["verified"],
            lonely["reason"]) == ("0.2.0", "MIT OR Apache-2.0", False, "no_repository")
    assert (local["verified"], local["reason"]) == (False, "not_published")
