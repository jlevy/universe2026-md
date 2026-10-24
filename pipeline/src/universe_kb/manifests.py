"""
Packages a repository publishes, verified against their registries.

A repository's root manifests (`package.json`, `pyproject.toml`, `setup.cfg`,
`Cargo.toml`, `go.mod`) declare package names, but a name alone proves nothing: forks
keep the upstream's manifest, and unrelated projects reuse popular names. So a package
is linked to a repository only when a saved manifest declaration and its registry agree
on the same `owner/repo` (for Go, a module path under that repository). This establishes
source provenance, not registry publisher identity.

Only public, unauthenticated endpoints are used: raw.githubusercontent.com for files and
the npm, PyPI, crates.io and Go module proxy registries. api.github.com is not.
"""

from __future__ import annotations

import configparser
import json
import logging
import re
import tomllib
import urllib.parse
from dataclasses import dataclass
from typing import Any

from universe_kb.snapshot import Fetcher

log = logging.getLogger(__name__)

MANIFESTS: dict[str, list[str]] = {
    "npm": ["package.json"],
    "pypi": ["pyproject.toml", "setup.cfg"],
    "crates": ["Cargo.toml"],
    "go": ["go.mod"],
}
RAW_URL = "https://raw.githubusercontent.com/{full_name}/{ref}/{file}"
# Registry documents list every release; large projects' PyPI and crates.io documents run
# to megabytes, and a truncated document would fail to parse.
REGISTRY_MAX_BYTES = 20_000_000
NOT_FOUND_STATUS = {404, 410}

# PyPI `project_urls` labels that name a source repository, after PEP 753 normalization
# (lowercase, punctuation and whitespace removed).
SOURCE_LABELS = {"source", "sourcecode", "repository", "repo", "code", "github", "git"}
HOMEPAGE_LABELS = {"homepage", "home"}

GITHUB_URL = re.compile(
    r"^(?:git\+)?(?:(?:https?|git|ssh)://)?(?:[^@/]+@)?(?:www\.)?github\.com[:/]"
    r"(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)",
    re.IGNORECASE,
)
# npm's shorthand for a GitHub repository: `github:owner/repo` or bare `owner/repo`.
GITHUB_SHORTHAND = re.compile(r"^(?:github:)?(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)$")
GO_MODULE = re.compile(r"^\s*module\s+(?:\(\s*)?(\"?)(?P<path>[^\s\"()]+)\1", re.MULTILINE)


def github_repo(url: str | None) -> str | None:
    """
    The lowercase `owner/repo` a GitHub URL names, or None for any other URL. Accepts the
    forms registries hold: `git+https://…/repo.git`, `git@github.com:owner/repo`,
    `github:owner/repo`, and links into the repository such as `/tree/main/pkg`.
    """
    if not url:
        return None
    url = url.strip()
    match = GITHUB_URL.match(url) or GITHUB_SHORTHAND.match(url)
    if not match:
        return None
    repo = match["repo"].removesuffix(".git")
    if not repo or repo in {".", ".."}:
        return None
    return f"{match['owner']}/{repo}".lower()


def _string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _table(data: Any, *keys: str) -> dict[str, Any]:
    for key in keys:
        data = data.get(key) if isinstance(data, dict) else None
    return data if isinstance(data, dict) else {}


def _package_json_name(text: str) -> str | None:
    data = json.loads(text)
    if not isinstance(data, dict) or data.get("private") is True:
        return None
    return _string(data.get("name"))


def _pyproject_name(text: str) -> str | None:
    data = tomllib.loads(text)
    return (_string(_table(data, "project").get("name"))
            or _string(_table(data, "tool", "poetry").get("name")))


def _setup_cfg_name(text: str) -> str | None:
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(text)
    return _string(parser.get("metadata", "name", fallback=None))


def _cargo_name(text: str) -> str | None:
    return _string(_table(tomllib.loads(text), "package").get("name"))


def _go_mod_name(text: str) -> str | None:
    text = re.sub(r"//.*", "", text)
    match = GO_MODULE.search(text)
    return match["path"] if match else None


PARSERS = {
    "package.json": ("npm", _package_json_name),
    "pyproject.toml": ("pypi", _pyproject_name),
    "setup.cfg": ("pypi", _setup_cfg_name),
    "Cargo.toml": ("crates", _cargo_name),
    "go.mod": ("go", _go_mod_name),
}


def manifest_names(text: str, filename: str) -> list[tuple[str, str]]:
    """
    `(ecosystem, package_name)` pairs one manifest declares. Private npm packages and
    Cargo workspace roots declare none; malformed or unknown files give an empty list.
    """
    if filename not in PARSERS:
        return []
    ecosystem, parse = PARSERS[filename]
    try:
        name = parse(text.removeprefix("\ufeff"))
    except (ValueError, RecursionError, configparser.Error) as error:
        log.info("unreadable %s: %s", filename, error)
        return []
    return [(ecosystem, name)] if name else []


@dataclass(frozen=True)
class RegistryRecord:
    """
    What a registry says about one package. `sources` are declared repository or source
    URLs, most authoritative first; `homepages` count only when no source is declared.
    """

    name: str
    url: str
    latest_version: str | None
    description: str | None
    license: str | None
    sources: tuple[str, ...]
    homepages: tuple[str, ...] = ()


def _text(value: Any) -> str | None:
    return (" ".join(value.split()) or None) if isinstance(value, str) else None


def _registry_json(fetcher: Fetcher, url: str) -> tuple[Any, str | None]:
    """The parsed document, or None and the failure reason."""
    response = fetcher.fetch(url, max_bytes=REGISTRY_MAX_BYTES)
    if response.status in NOT_FOUND_STATUS:
        return None, "not_published"
    if response.status != 200:
        log.warning("registry lookup %s failed: %s", url, response.error)
        return None, "registry_error"
    try:
        return json.loads(response.body), None
    except (ValueError, RecursionError) as error:
        log.warning("registry lookup %s returned unreadable JSON: %s", url, error)
        return None, "registry_error"


def _npm(fetcher: Fetcher, name: str) -> tuple[RegistryRecord | None, str | None]:
    # `/latest` is the latest version's manifest, a few kilobytes; the full document
    # lists every version and can exceed any sensible size limit.
    quoted = urllib.parse.quote(name, safe="@")
    doc, reason = _registry_json(fetcher, f"https://registry.npmjs.org/{quoted}/latest")
    if not isinstance(doc, dict):
        return None, reason or "registry_error"
    repository = doc.get("repository")
    source = repository.get("url") if isinstance(repository, dict) else repository
    license_ = doc.get("license")
    if isinstance(license_, dict):
        license_ = license_.get("type")
    canonical = _string(doc.get("name")) or name
    return RegistryRecord(
        name=canonical,
        url=f"https://www.npmjs.com/package/{canonical}",
        latest_version=_string(doc.get("version")),
        description=_text(doc.get("description")),
        license=_string(license_),
        sources=tuple(s for s in [_string(source)] if s),
        homepages=tuple(h for h in [_string(doc.get("homepage"))] if h),
    ), None


def _pypi_license(info: dict[str, Any]) -> str | None:
    # `license` sometimes holds the whole license text rather than its name.
    license_ = _string(info.get("license"))
    if license_ and ("\n" in license_ or len(license_) > 80):
        license_ = None
    classifiers = [c.rsplit(" :: ", 1)[-1] for c in info.get("classifiers") or []
                   if isinstance(c, str) and c.startswith("License :: ")]
    return (_string(info.get("license_expression")) or license_
            or (classifiers[0] if classifiers else None))


def _pypi(fetcher: Fetcher, name: str) -> tuple[RegistryRecord | None, str | None]:
    quoted = urllib.parse.quote(name, safe="")
    doc, reason = _registry_json(fetcher, f"https://pypi.org/pypi/{quoted}/json")
    info = doc.get("info") if isinstance(doc, dict) else None
    if not isinstance(info, dict):
        return None, reason or "registry_error"
    sources: list[str] = []
    homepages: list[str] = []
    for label, value in _table(info, "project_urls").items():
        key = re.sub(r"[\W_]", "", str(label).lower())
        if key in SOURCE_LABELS and _string(value):
            sources.append(value.strip())
        elif key in HOMEPAGE_LABELS and _string(value):
            homepages.append(value.strip())
    if _string(info.get("home_page")):
        homepages.append(info["home_page"].strip())
    canonical = _string(info.get("name")) or name
    return RegistryRecord(
        name=canonical,
        url=f"https://pypi.org/project/{canonical}/",
        latest_version=_string(info.get("version")),
        description=_text(info.get("summary")),
        license=_pypi_license(info),
        sources=tuple(sources),
        homepages=tuple(homepages),
    ), None


def _crates(fetcher: Fetcher, name: str) -> tuple[RegistryRecord | None, str | None]:
    quoted = urllib.parse.quote(name, safe="")
    doc, reason = _registry_json(fetcher, f"https://crates.io/api/v1/crates/{quoted}")
    crate = doc.get("crate") if isinstance(doc, dict) else None
    if not isinstance(crate, dict):
        return None, reason or "registry_error"
    latest = (_string(crate.get("default_version")) or _string(crate.get("max_stable_version"))
              or _string(crate.get("max_version")))
    license_ = next((v.get("license") for v in doc.get("versions") or []
                     if isinstance(v, dict) and v.get("num") == latest), None)
    canonical = _string(crate.get("name")) or name
    return RegistryRecord(
        name=canonical,
        url=f"https://crates.io/crates/{canonical}",
        latest_version=latest,
        description=_text(crate.get("description")),
        license=_string(license_),
        sources=tuple(s for s in [_string(crate.get("repository"))] if s),
        homepages=tuple(h for h in [_string(crate.get("homepage"))] if h),
    ), None


def go_proxy_path(module: str) -> str:
    """The module proxy's case encoding: each uppercase letter becomes `!` and lowercase."""
    return re.sub(r"[A-Z]", lambda m: "!" + m[0].lower(), module)


def _go(fetcher: Fetcher, module: str) -> tuple[RegistryRecord | None, str | None]:
    # The go command only fetches modules whose first path element looks like a host.
    if "." not in module.split("/", 1)[0]:
        return None, "not_published"
    quoted = urllib.parse.quote(go_proxy_path(module), safe="/!")
    doc, reason = _registry_json(fetcher, f"https://proxy.golang.org/{quoted}/@latest")
    if not isinstance(doc, dict):
        return None, reason or "registry_error"
    # The proxy's recorded origin, then the repository a github.com module path names.
    sources = [_string(_table(doc, "Origin").get("URL"))]
    if module.lower().startswith("github.com/"):
        sources.append("https://" + "/".join(module.split("/")[:3]))
    return RegistryRecord(
        name=module,
        url=f"https://pkg.go.dev/{module}",
        latest_version=_string(doc.get("Version")),
        description=None,
        license=None,
        sources=tuple(s for s in sources if s),
    ), None


LOOKUPS = {"npm": _npm, "pypi": _pypi, "crates": _crates, "go": _go}


def verify_package(fetcher: Fetcher, full_name: str, ecosystem: str, name: str,
                   declared_in: str | None = None
                   ) -> dict[str, Any]:
    """
    Match registry source provenance to a repository that declares the package in
    `declared_in`. Without the declaration a registry backlink is insufficient; even
    with it, this check makes no claim about the registry publisher's identity.
    """
    record, reason = LOOKUPS[ecosystem](fetcher, name)
    package: dict[str, Any] = {
        "ecosystem": ecosystem, "name": name, "url": None, "latest_version": None,
        "description": None, "license": None, "repository_url": None,
        "verified": False, "reason": reason,
    }
    if record is None:
        return package
    candidates = record.sources or record.homepages
    expected = full_name.lower()
    matched = next((url for url in candidates if github_repo(url) == expected), None)
    if matched and declared_in is None:
        reason = "no_manifest_declaration"
    elif matched:
        reason = None
    elif candidates:
        reason = "repository_mismatch"
    else:
        reason = "no_repository"
    package.update(
        name=record.name, url=record.url, latest_version=record.latest_version,
        description=record.description, license=record.license,
        repository_url=matched or (candidates[0] if candidates else None),
        verified=matched is not None and reason is None, reason=reason,
    )
    return package


def _dedupe_key(ecosystem: str, name: str) -> tuple[str, str]:
    # PyPI treats runs of `-`, `_` and `.` as equal and ignores case (PEP 503).
    if ecosystem == "pypi":
        return ecosystem, re.sub(r"[-_.]+", "-", name).lower()
    return ecosystem, name


def repo_packages(fetcher: Fetcher, full_name: str, default_branch: str | None = None
                  ) -> dict[str, Any]:
    """
    Fetch `full_name`'s root manifests, then verify each declared package with its
    registry. Within an ecosystem, later manifests are skipped once one declares a name
    (a `setup.cfg` beside a named `pyproject.toml` adds nothing). `HEAD` resolves to the
    default branch, so `default_branch` is needed only to read another branch.

    Returns `{"repository", "checked": [{"file", "status", "error"}], "packages": [...]}`,
    each package as `verify_package` describes it.
    """
    ref = urllib.parse.quote(default_branch or "HEAD", safe="/")
    checked: list[dict[str, Any]] = []
    declared: dict[tuple[str, str], tuple[str, str, str]] = {}
    for files in MANIFESTS.values():
        for filename in files:
            url = RAW_URL.format(full_name=full_name, ref=ref, file=filename)
            response = fetcher.fetch(url)
            checked.append({"file": filename, "status": response.status,
                            "error": response.error})
            if response.status != 200:
                continue
            names = manifest_names(response.body.decode("utf-8", errors="replace"), filename)
            for ecosystem, name in names:
                declared.setdefault(_dedupe_key(ecosystem, name), (ecosystem, name, filename))
            if names:
                break
    packages = [{**verify_package(fetcher, full_name, ecosystem, name, filename),
                 "declared_in": filename}
                for ecosystem, name, filename in declared.values()]
    return {"repository": full_name, "checked": checked, "packages": packages}
