"""
Bright Data Web Scraper API datasets: the public LinkedIn and X profile details that free
sources do not expose, such as LinkedIn experience and education, X profile fields, and
each person's own recent posts.

Collection is asynchronous: trigger a snapshot with a list of inputs, poll its progress,
then download the records. Each record is sanitized (`sanitize`) and saved under
`raw/brightdata/`, so the build stays offline and the snapshot holds only the profile
owner's own public information.
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from universe_kb import policy, privacy, sensitive
from universe_kb.snapshot import Fetcher, FetchError

log = logging.getLogger(__name__)

API = "https://api.brightdata.com"
KEY_NAME = "BRIGHT_DATA_API_KEY"
POLL_SECONDS = 10
MAX_WAIT_SECONDS = 45 * 60


@dataclass(frozen=True)
class Dataset:
    id: str
    # Extra trigger parameters; "discover" datasets find many records per input.
    params: tuple[tuple[str, str], ...] = ()


# Only datasets with a sanitizer below; each new one needs its own allowlist first.
DATASETS = {
    "linkedin_profiles": Dataset("gd_l1viktl72bvl7bjuj0"),
    "linkedin_companies": Dataset("gd_l1vikfnt1wgvvqz95w"),
    "x_profiles": Dataset("gd_lwxmeb2u1cniijd7t4"),
}


def load_api_key(project_dir: Path) -> str:
    """The key from the environment, else from the project's `.env.local` or `.env`."""
    if os.environ.get(KEY_NAME):
        return os.environ[KEY_NAME]
    for name in (".env.local", ".env"):
        path = project_dir / name
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == KEY_NAME:
                return value.strip().strip("\"'")
    raise SystemExit(f"{KEY_NAME} is not set in the environment, .env.local or .env")


class BrightData:
    def __init__(self, fetcher: Fetcher, key: str) -> None:
        self.fetcher = fetcher
        self.headers = {"Authorization": f"Bearer {key}"}

    def trigger(self, dataset: str, inputs: list[dict[str, Any]],
                **params: str | int) -> str:
        spec = DATASETS[dataset]
        query = {"dataset_id": spec.id, "include_errors": "true", **dict(spec.params),
                 **{k: str(v) for k, v in params.items()}}
        result = self.fetcher.json("POST", f"{API}/datasets/v3/trigger?{urlencode(query)}",
                                   json_body=inputs, headers=self.headers)
        return result["snapshot_id"]

    def wait(self, snapshot_id: str) -> dict[str, Any]:
        deadline = time.monotonic() + MAX_WAIT_SECONDS
        while time.monotonic() < deadline:
            status = self.fetcher.json("GET", f"{API}/datasets/v3/progress/{snapshot_id}",
                                       headers=self.headers)
            state = status.get("status")
            if state == "ready":
                return status
            if state == "failed":
                raise FetchError(f"Bright Data snapshot {snapshot_id} failed: {status}")
            log.info("snapshot %s: %s", snapshot_id, state)
            time.sleep(POLL_SECONDS)
        raise TimeoutError(f"snapshot {snapshot_id} not ready after {MAX_WAIT_SECONDS}s")

    def download(self, snapshot_id: str) -> list[dict[str, Any]]:
        records = self.fetcher.json(
            "GET", f"{API}/datasets/v3/snapshot/{snapshot_id}?format=json", headers=self.headers)
        if not isinstance(records, list):
            raise FetchError(f"unexpected snapshot format for {snapshot_id}")
        return records

    def collect(self, dataset: str, inputs: list[dict[str, Any]],
                **params: str | int) -> tuple[str, list[dict[str, Any]]]:
        snapshot_id = self.trigger(dataset, inputs, **params)
        log.info("%s: snapshot %s for %s inputs", dataset, snapshot_id, len(inputs))
        self.wait(snapshot_id)
        return snapshot_id, self.download(snapshot_id)


# What each dataset keeps: the profile owner's own public information, by field. An
# allowlist rather than a denylist, so a field the vendor adds later is dropped until
# someone decides it may stay. Lists of other people (employees, "people also viewed",
# similar pages, tagged users, reposts) and scraper bookkeeping are never on it.
LINKEDIN_PROFILE_FIELDS = {
    "id", "url", "name", "first_name", "last_name", "position", "about", "city", "location",
    "country_code", "followers", "connections", "avatar", "banner_image", "current_company",
    "current_company_name", "bio_links", "experience", "education", "certifications",
    "honors_and_awards", "publications", "patents", "languages", "projects", "courses",
    "volunteer_experience", "organizations", "posts", "timestamp",
}
X_PROFILE_FIELDS = {
    "x_id", "url", "id", "profile_name", "biography", "is_verified", "profile_image_link",
    "external_link", "date_joined", "following", "followers", "location", "posts_count",
    "posts", "banner_image", "timestamp",
}
X_POST_FIELDS = {"post_id", "post_url", "date_posted", "description"}
LINKEDIN_COMPANY_FIELDS = {
    "id", "url", "name", "about", "slogan", "industries", "company_size", "headquarters",
    "founded", "specialties", "logo", "image", "website", "followers", "organization_type",
    "formatted_locations", "updates", "timestamp",
}
COMPANY_UPDATE_FIELDS = {"text", "date", "post_url", "likes_count"}
# Recent LinkedIn posts kept per organization; the build shows five.
COMPANY_UPDATES = 5
# Volunteering is kept only for these causes; the others (politics, civil rights,
# health, religion, children) can state a person's views, faith or health.
PROFESSIONAL_CAUSES = {"Education", "Science and Technology"}
# A credential link that opens a private transcript or a shared file, not a public page.
PRIVATE_CREDENTIAL_LINK = re.compile(r"transcript|drive\.google|docs\.google|/share|sharing",
                                     re.IGNORECASE)
BATCH_SIZE = 100


def _own_text(record: dict[str, Any], keys: tuple[str, ...]) -> None:
    policy.apply(record, dict.fromkeys(keys, policy.person_text))


def _items(record: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = record.get(key)
    return [i for i in value if isinstance(i, dict)] if isinstance(value, list) else []


def _linkedin_profile(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("default_avatar"):
        # LinkedIn's placeholder silhouette is not the person's photo.
        record.pop("avatar", None)
    record = {k: v for k, v in record.items() if k in LINKEDIN_PROFILE_FIELDS}
    _own_text(record, ("about", "position"))
    policy.apply(record, dict.fromkeys(("name", "first_name", "last_name"), policy.person_name))
    policy.apply(record, {"location": policy.location, "city": policy.location})
    if isinstance(record.get("current_company"), dict):
        record["current_company"] = {k: v for k, v in record["current_company"].items()
                                     if k in {"name", "company_id", "link"}}
    record["bio_links"] = [{"title": b.get("title"), "link": b.get("link")}
                           for b in _items(record, "bio_links") if policy.keep_link(b.get("link"))]
    for job in _items(record, "experience"):
        for key in ("description_html", "company_logo_url"):
            job.pop(key, None)
        _own_text(job, ("description",))
        policy.apply(job, {"location": policy.location})
        for position in _items(job, "positions"):
            position.pop("description_html", None)
            _own_text(position, ("description",))
            policy.apply(position, {"location": policy.location})
    # School years let a reader work out someone's age.
    record["education"] = [
        {k: v for k, v in e.items() if k in {"title", "url", "degree", "field"}}
        for e in _items(record, "education")]
    record["volunteer_experience"] = [
        item for item in _items(record, "volunteer_experience")
        if item.get("cause") in PROFESSIONAL_CAUSES and not sensitive.is_sensitive(
            " ".join(str(item.get(k) or "") for k in ("title", "subtitle", "info")))]
    for key in ("organizations", "projects", "honors_and_awards", "certifications", "courses",
                "posts", "publications", "patents"):
        # Structured entries the knowledge base would list as facts: one whose words state
        # a sensitive attribute (a church choir, an identity-based award) is dropped.
        # Publications and patents are professional work and stay as listed.
        record[key] = [i for i in _items(record, key)
                       if key in {"publications", "patents"} or not sensitive.is_sensitive(
                           " ".join(str(i.get(k) or "") for k in (
                               "title", "subtitle", "publication", "description")))]
        for item in record[key]:
            if key not in {"publications", "patents"}:
                _own_text(item, ("description", "attribution"))
    for item in record["certifications"]:
        # Credential numbers identify a record in someone else's system.
        item.pop("credential_id", None)
        if isinstance(item.get("meta"), str):
            item["meta"] = re.sub(r"\s*Credential ID \S+", "", item["meta"])
        if PRIVATE_CREDENTIAL_LINK.search(str(item.get("credential_url") or "")):
            item.pop("credential_url", None)
    return record


def _post_author(post: dict[str, Any]) -> str | None:
    """The numeric author ID in a post URL (`twitter.com/<id>/status/…`), if it has one."""
    match = re.search(r"(?:twitter|x)\.com/(\d+)/status/", post.get("post_url") or "")
    return match[1] if match else None


def _x_profile(record: dict[str, Any]) -> dict[str, Any]:
    record = {k: v for k, v in record.items() if k in X_PROFILE_FIELDS}
    _own_text(record, ("biography",))
    policy.apply(record, {"profile_name": policy.person_name, "location": policy.location})
    if not policy.keep_link(record.get("external_link")):
        record["external_link"] = None
    # Only the owner's own posts and replies, without media or engagement counts: a post
    # whose URL names another author, or a retweet, carries someone else's words.
    owner = str(record.get("x_id") or "")
    record["posts"] = [
        {**{k: v for k, v in post.items() if k in X_POST_FIELDS},
         "description": privacy.redact(post.get("description") or "")}
        for post in record.get("posts") or []
        if isinstance(post, dict) and _post_author(post) in {owner, None}
        and not (post.get("description") or "").startswith("RT @")
        and not sensitive.is_sensitive(post.get("description"))]
    return record


def _linkedin_company(record: dict[str, Any]) -> dict[str, Any]:
    # Updates that tag a person (a `linkedin.com/in/` link in their HTML) name someone
    # other than the organization; the rest keep only their plain text.
    updates = [u for u in _items(record, "updates") if (u.get("text") or "").strip()
               and "linkedin.com/in/" not in str(u.get("text_html") or "")]
    updates.sort(key=lambda u: u.get("date") or "", reverse=True)
    if not record.get("id") and record.get("company_id"):
        record["id"] = record["company_id"]
    if not record.get("about") and record.get("description"):
        record["about"] = record["description"]
    record = {k: v for k, v in record.items() if k in LINKEDIN_COMPANY_FIELDS}
    record["updates"] = [{k: v for k, v in u.items() if k in COMPANY_UPDATE_FIELDS}
                         for u in updates[:COMPANY_UPDATES]]
    policy.apply(record, {"about": policy.org_text, "slogan": policy.org_text})
    for update in record["updates"]:
        policy.apply(update, {"text": policy.org_text})
    if isinstance(record.get("formatted_locations"), list):
        record["formatted_locations"] = list(dict.fromkeys(
            loc for loc in map(sensitive.city_level, record["formatted_locations"]) if loc))
    return record


def sanitize(dataset: str, record: dict[str, Any]) -> dict[str, Any]:
    """
    One collected record as it may be committed: the profile owner's own public
    information, with other people's data, scraper bookkeeping, contact details and
    sensitive attributes removed and locations kept at city level. An error record (a
    hidden or deleted profile) keeps only its error code, so collection does not retry it.
    """
    if record.get("error") or record.get("error_code"):
        return {"error_code": record.get("error_code") or "error"}
    shape = {"linkedin_profiles": _linkedin_profile, "x_profiles": _x_profile,
             "linkedin_companies": _linkedin_company}.get(dataset)
    if shape is None:
        raise ValueError(f"no sanitizer for Bright Data dataset {dataset!r}")
    return privacy.redact_payload(shape(dict(record)))


def kb_profile_urls(kb_dir: Path, platform: str, owner_kind: str = "person") -> list[str]:
    """Profile URLs of every account on `platform` that a person (or org) owns in the kb."""
    import yaml

    urls = []
    for path in sorted((kb_dir / "accounts" / platform).rglob("*.yaml")):
        account = yaml.safe_load(path.read_text())["social_account"]
        if account.get("owner", "").startswith(f"{owner_kind}:"):
            urls.append(account["url"])
    return urls


def collect_to_snapshot(client: BrightData, snapshot: Any, dataset: str, urls: list[str],
                        **params: str | int) -> dict[str, int]:
    """
    Collect `urls` in batches and merge them into `raw/brightdata/<dataset>.json`, keyed by
    input URL, so a rerun only fetches what is missing.
    """
    rel_path = f"brightdata/{dataset}.json"
    existing: dict[str, Any] = snapshot.load_json(rel_path) if snapshot.has(rel_path) else {}
    todo = [u for u in dict.fromkeys(urls) if u not in existing]
    for start in range(0, len(todo), BATCH_SIZE):
        batch = todo[start: start + BATCH_SIZE]
        snapshot_id, records = client.collect(dataset, [{"url": u} for u in batch], **params)
        by_input: dict[str, list[dict[str, Any]]] = {u: [] for u in batch}
        for record in records:
            source = (record.get("input") or {}).get("url") or record.get("input_url")
            if source in by_input:
                by_input[source].append(record)
        for url, found in by_input.items():
            existing[url] = {"snapshot_id": snapshot_id, "records": found}
        snapshot.save_json(rel_path, existing, url=f"{API}/datasets/v3/snapshot/{snapshot_id}")
        snapshot.write_manifest()
    return {"inputs": len(urls), "fetched": len(todo),
            "with_records": sum(1 for v in existing.values() if v["records"])}
