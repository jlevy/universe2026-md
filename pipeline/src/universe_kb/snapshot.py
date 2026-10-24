"""
Polite HTTP fetching and the raw snapshot store.

Every response the crawler keeps passes through the data policy's raw sanitizer, is
written under `raw/` and is recorded in `raw/manifest.json` with its URL, retrieval time
and SHA-256, so each knowledge base record can cite the exact bytes it came from.
"""

from __future__ import annotations

import copy
import fcntl
import hashlib
import http.client
import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from strif import atomic_write_text

from universe_kb.fetch_safety import UnsafeDestination, open_public_url

log = logging.getLogger(__name__)

USER_AGENT = "universe2026-md/0.1 (+https://github.com/jlevy/universe2026-md)"
REQUEST_DELAY_SECONDS = 1.0
MAX_ATTEMPTS = 4
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class FetchError(RuntimeError):
    pass


@dataclass(frozen=True)
class FetchResponse:
    """
    The outcome of `Fetcher.fetch`. `status` is None when no HTTP response arrived, and
    `error` explains any non-2xx status or failure.
    """

    status: int | None
    final_url: str | None
    content_type: str | None
    body: bytes
    error: str | None


@dataclass
class Fetcher:
    """Sequential HTTP client with a fixed delay between requests and retry on 429/5xx."""

    delay: float = REQUEST_DELAY_SECONDS
    user_agent: str = USER_AGENT
    _last_request: float = 0.0

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        form: dict[str, str] | None = None,
        json_body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        body: bytes | None = None
        all_headers = {"User-Agent": self.user_agent, **(headers or {})}
        if form is not None:
            body = urllib.parse.urlencode(form).encode()
            all_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        elif json_body is not None:
            body = json.dumps(json_body).encode()
            all_headers["Content-Type"] = "application/json"

        for attempt in range(1, MAX_ATTEMPTS + 1):
            wait = self._last_request + self.delay - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last_request = time.monotonic()
            request = urllib.request.Request(url, data=body, headers=all_headers, method=method)
            try:
                with open_public_url(request, timeout=60) as response:
                    return response.read()
            except UnsafeDestination as error:
                raise FetchError(f"{method} request blocked: {error}") from error
            except urllib.error.HTTPError as error:
                if error.code not in RETRYABLE_STATUS or attempt == MAX_ATTEMPTS:
                    detail = error.read()[:300].decode("utf-8", errors="replace")
                    raise FetchError(f"{method} {url} failed: HTTP {error.code}: {detail}"
                                     ) from error
                log.warning("%s %s returned %s; retrying", method, url, error.code)
            except urllib.error.URLError as error:
                if attempt == MAX_ATTEMPTS:
                    raise FetchError(f"{method} {url} failed: {error.reason}") from error
                log.warning("%s %s failed (%s); retrying", method, url, error.reason)
            except (http.client.IncompleteRead, ConnectionError, TimeoutError) as error:
                # A dropped or stalled connection mid-response is as transient as a 502.
                if attempt == MAX_ATTEMPTS:
                    raise FetchError(f"{method} {url} failed: {error!r}") from error
                log.warning("%s %s failed (%r); retrying", method, url, error)
            time.sleep(2**attempt)
        raise AssertionError("unreachable")

    def fetch(self, url: str, *, max_bytes: int = 2_000_000, timeout: float = 20) -> FetchResponse:
        """
        GET `url` once and report the outcome instead of raising. This is for third-party
        pages such as personal homepages, where a 404, a dead domain or a TLS failure is
        a fact to record rather than a reason to stop or retry. Reads at most `max_bytes`.
        """
        if not url.lower().startswith(("http://", "https://")):
            return FetchResponse(None, None, None, b"", f"not an http(s) URL: {url!r}")
        wait = self._last_request + self.delay - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with open_public_url(request, timeout=timeout) as response:
                return FetchResponse(
                    status=response.status,
                    final_url=response.geturl(),
                    content_type=response.headers.get("Content-Type"),
                    body=response.read(max_bytes),
                    error=None,
                )
        except urllib.error.HTTPError as error:
            try:
                body = error.read(max_bytes)
            except (OSError, http.client.HTTPException):
                body = b""
            return FetchResponse(
                status=error.code,
                final_url=error.geturl(),
                content_type=error.headers.get("Content-Type") if error.headers else None,
                body=body,
                error=f"HTTP {error.code}",
            )
        # URLError and timeouts are OSErrors; malformed URLs raise ValueError or InvalidURL.
        except (OSError, http.client.HTTPException, ValueError) as error:
            reason = error.reason if isinstance(error, urllib.error.URLError) else error
            return FetchResponse(None, None, None, b"", f"{type(error).__name__}: {reason}")

    def json(self, method: str, url: str, **kwargs: Any) -> Any:
        return json.loads(self.request(method, url, **kwargs))

    def text(self, url: str, **kwargs: Any) -> str:
        return self.request("GET", url, **kwargs).decode("utf-8")


@dataclass
class Snapshot:
    """Raw files under `root`, plus the manifest that describes them."""

    root: Path
    entries: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Each save publishes its payload and manifest under the same process lock.
    # This set also tracks explicit metadata edits made by existing collection callers.
    changed: set[str] = field(default_factory=set)
    _published: dict[str, dict[str, Any]] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        manifest = self.root / "manifest.json"
        if manifest.exists():
            self.entries = json.loads(manifest.read_text())["files"]
            self._published = copy.deepcopy(self.entries)

    def save_json(self, rel_path: str, data: Any, *, url: str, method: str = "GET") -> None:
        from universe_kb.policy import sanitize_raw

        # Sanitize a copy: callers keep using what they fetched (the crawler reads the
        # catalog widget's tokens from a page it has just saved without them).
        text = json.dumps(sanitize_raw(rel_path, copy.deepcopy(data)), ensure_ascii=False,
                          indent=1) + "\n"
        self._save(rel_path, text, url=url, method=method)

    def rewrite_json(self, rel_path: str, data: Any) -> bool:
        """Reapply the JSON policy, retaining retrieval provenance and recording sanitation."""
        from universe_kb.policy import sanitize_raw

        text = json.dumps(sanitize_raw(rel_path, copy.deepcopy(data)), ensure_ascii=False,
                          indent=1) + "\n"
        return self._rewrite(rel_path, text)

    def rewrite_text(self, rel_path: str, text: str) -> bool:
        """Reapply the text/HTML policy without changing source URL or retrieval time."""
        from universe_kb.policy import sanitize_text

        return self._rewrite(rel_path, sanitize_text(rel_path, text))

    @contextmanager
    def _locked(self) -> Iterator[None]:
        # Lock the stable snapshot directory itself, avoiding a publishable lock file.
        self.root.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.root, os.O_RDONLY)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def _read_manifest(self) -> dict[str, dict[str, Any]]:
        path = self.root / "manifest.json"
        return json.loads(path.read_text())["files"] if path.exists() else {}

    def _publish_manifest(self, updates: dict[str, dict[str, Any]]) -> None:
        """Merge under the directory lock; a delayed writer cannot restore stale hashes."""
        files = self._read_manifest()
        for rel_path, entry in updates.items():
            path = self.root / rel_path
            if not path.is_file():
                continue
            data = path.read_bytes()
            if entry.get("sha256") != hashlib.sha256(data).hexdigest():
                continue
            files[rel_path] = {**entry, "bytes": len(data)}
        atomic_write_text(
            self.root / "manifest.json",
            json.dumps({"files": dict(sorted(files.items()))}, indent=1) + "\n",
            make_parents=True,
        )
        self.entries = files
        self._published = copy.deepcopy(files)

    def _rewrite(self, rel_path: str, text: str) -> bool:
        with self._locked():
            path = self.root / rel_path
            if path.read_text() == text:
                return False
            entry = dict(self._read_manifest().get(rel_path) or self.entries[rel_path])
            entry.update(
                bytes=len(text.encode()),
                sha256=hashlib.sha256(text.encode()).hexdigest(),
                sanitized_at=utc_now(),
            )
            atomic_write_text(path, text)
            self.changed.add(rel_path)
            self._publish_manifest({rel_path: entry})
        return True

    def save_text(self, rel_path: str, text: str, *, url: str, method: str = "GET") -> None:
        from universe_kb.policy import sanitize_text

        self._save(rel_path, sanitize_text(rel_path, text), url=url, method=method)

    def _save(self, rel_path: str, text: str, *, url: str, method: str) -> None:
        entry = {
            "url": url,
            "method": method,
            "retrieved_at": utc_now(),
            "bytes": len(text.encode()),
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
        }
        with self._locked():
            atomic_write_text(self.root / rel_path, text, make_parents=True)
            self.changed.add(rel_path)
            self._publish_manifest({rel_path: entry})
        log.info("saved %s (%s bytes)", rel_path, entry["bytes"])

    def write_manifest(self) -> None:
        with self._locked():
            files = self._read_manifest()
            updates = {}
            for rel in self.changed:
                entry = self.entries.get(rel) or {}
                previous = self._published.get(rel) or {}
                delta = {key: value for key, value in entry.items() if previous.get(key) != value}
                if delta:
                    updates[rel] = {**files.get(rel, {}), **delta}
            self._publish_manifest(updates)

    def load_json(self, rel_path: str) -> Any:
        return json.loads((self.root / rel_path).read_text())

    def has(self, rel_path: str) -> bool:
        return (self.root / rel_path).exists()
