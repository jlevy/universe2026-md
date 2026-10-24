"""
Enrich the official snapshot with GitHub and package-registry facts.

All lookups are read-only public data:

- every speaker's GitHub handle, via GraphQL `repositoryOwner` (profile, public
  organizations, pinned repositories, most-starred repositories);
- the repositories the software gazetteer claims, via GraphQL `repository`;
- a GitHub organization for each sponsor, accepted only when the organization's own
  website shares a domain with the sponsor's link;
- the npm and PyPI packages the gazetteer claims.

Responses are stored under `raw/github/` and `raw/registries/` like any other source.
GraphQL needs a token: set `GITHUB_TOKEN` (for example `GITHUB_TOKEN=$(gh auth token)`).
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.parse
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from universe_kb.bluesky import fetch_profiles, normalize_handle
from universe_kb.feeds import fetch_feed
from universe_kb.fetch_safety import public_http_url
from universe_kb.ids import COMPANY_LOGIN, org_key, parse_github_handle, registrable_domain
from universe_kb.manifests import MANIFESTS, RAW_URL, manifest_names, verify_package
from universe_kb.mastodon import hashtag_posts, lookup_profiles
from universe_kb.people import (
    NOT_PERSONAL_DOMAINS,
    github_social_links,
    social_account_id,
    website_id,
)
from universe_kb.policy import Exclusions, keep_link
from universe_kb.snapshot import Fetcher, FetchError, Snapshot, utc_now
from universe_kb.web import classify_social_url, fetch_homepage

log = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.github.com/graphql"
BATCH_SIZE = 5
RATE_LIMIT_ATTEMPTS = 4
RATE_LIMIT_WAIT = 90
CONTRIBUTED_REPOSITORIES = 5
FEED_ITEMS = 10
README_FIELDS = 'object(expression: "HEAD:{path}") {{ ... on Blob {{ text }} }}'
TOP_REPOSITORIES = 5
PINNED_REPOSITORIES = 6
# Recent stars and public star lists: what people follow, a signal of their interests.
RECENT_STARS = 20
STAR_LISTS = 10
STAR_LIST_ITEMS = 10
# Owners are saved after each group, so an interrupted run keeps what it fetched.
SAVE_EVERY = 20

REPO_FIELDS = """
  nameWithOwner url description homepageUrl stargazerCount forkCount isArchived isFork
  createdAt pushedAt primaryLanguage { name } licenseInfo { spdxId }
  repositoryTopics(first: 10) { nodes { topic { name } } } owner { login }
"""
STAR_FIELDS = f"""
    starredRepositories(first: {RECENT_STARS},
                        orderBy: {{ field: STARRED_AT, direction: DESC }}) {{
      totalCount nodes {{ nameWithOwner primaryLanguage {{ name }}
                          repositoryTopics(first: 6) {{ nodes {{ topic {{ name }} }} }} }} }}
    lists(first: {STAR_LISTS}) {{ nodes {{ name description
      items(first: {STAR_LIST_ITEMS}) {{ nodes {{ ... on Repository {{ nameWithOwner }} }} }} }} }}
"""
OWNER_FIELDS = f"""
  __typename login url avatarUrl
  ... on User {{
    name company bio location websiteUrl createdAt twitterUsername
    isGitHubStar isCampusExpert isEmployee hasSponsorsListing
    socialAccounts(first: 10) {{ nodes {{ provider url displayName }} }}
    followers {{ totalCount }}
    {STAR_FIELDS}
    gists {{ totalCount }}
    contributionsCollection {{
      contributionYears
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      totalPullRequestReviewContributions contributionCalendar {{ totalContributions }} }}
    repositoriesContributedTo(first: {CONTRIBUTED_REPOSITORIES}, includeUserRepositories: false,
                              contributionTypes: [COMMIT, PULL_REQUEST],
                              orderBy: {{ field: STARGAZERS, direction: DESC }}) {{
      totalCount nodes {{ {REPO_FIELDS} }} }}
    organizations(first: 20) {{ nodes {{ login }} }}
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC,
                 first: {TOP_REPOSITORIES},
                 orderBy: {{ field: STARGAZERS, direction: DESC }}) {{
      totalCount nodes {{ {REPO_FIELDS} }} }}
    pinnedItems(first: {PINNED_REPOSITORIES}, types: REPOSITORY) {{
      nodes {{ ... on Repository {{ {REPO_FIELDS} }} }} }}
  }}
  ... on Organization {{
    name description location websiteUrl createdAt twitterUsername
    repositories(isFork: false, privacy: PUBLIC, first: {TOP_REPOSITORIES},
                 orderBy: {{ field: STARGAZERS, direction: DESC }}) {{
      totalCount nodes {{ {REPO_FIELDS} }} }}
    pinnedItems(first: {PINNED_REPOSITORIES}, types: REPOSITORY) {{
      nodes {{ ... on Repository {{ {REPO_FIELDS} }} }} }}
  }}
"""


# For an account whose recent stars time out even alone (thousands of stars): the same
# fields without per-star detail or star lists.
OWNER_FIELDS_LIGHT = OWNER_FIELDS.replace(STAR_FIELDS, "starredRepositories { totalCount }")

# The repository refresh reads two counts that owner records leave out.
REPO_STATS_FIELDS = f"{REPO_FIELDS} watchers {{ totalCount }} issues(states: OPEN) {{ totalCount }}"
REPO_STATS_PATH = "github/repo-stats.json"
REPO_STATS_BATCH = 50
# Saved after each group, so an interrupted refresh keeps what it read.
REPO_STATS_SAVE_EVERY = 100
REPO_STATS_MAX_AGE_HOURS = 12.0
# Failures worth splitting a batch over: too heavy a request, a GitHub server error, or an
# error about one repository in it. Rate limits are not; smaller requests would not help.
SPLITTABLE_ERRORS = ("RESOURCE_LIMITS_EXCEEDED", "HTTP 500", "HTTP 502", "HTTP 503", "HTTP 504",
                     "GitHub GraphQL errors")


def _splittable(error: FetchError) -> bool:
    text = str(error)
    if "RATE_LIMITED" in text or "rate limit" in text.lower():
        return False
    return any(sign in text for sign in SPLITTABLE_ERRORS)


def _chunks(values: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


class GitHubClient:
    def __init__(self, fetcher: Fetcher, token: str) -> None:
        self.fetcher = fetcher
        self.headers = {"Authorization": f"bearer {token}", "Accept": "application/json"}

    def query(self, query: str) -> dict[str, Any]:
        for attempt in range(1, RATE_LIMIT_ATTEMPTS + 1):
            try:
                result = self.fetcher.json("POST", GRAPHQL_URL, json_body={"query": query},
                                           headers=self.headers)
                break
            except FetchError as error:
                # GitHub's secondary rate limit asks clients to back off for minutes.
                if "secondary rate limit" not in str(error) or attempt == RATE_LIMIT_ATTEMPTS:
                    raise
                log.warning("GitHub secondary rate limit; waiting %ss", RATE_LIMIT_WAIT)
                time.sleep(RATE_LIMIT_WAIT * attempt)
        else:
            raise AssertionError("unreachable")
        errors = [e for e in result.get("errors") or [] if e.get("type") != "NOT_FOUND"]
        if errors:
            raise FetchError(f"GitHub GraphQL errors: {json.dumps(errors)[:500]}")
        return result.get("data") or {}

    def owners(self, logins: list[str]) -> dict[str, Any]:
        found: dict[str, Any] = {}
        for batch in _chunks(logins, BATCH_SIZE):
            found.update(self._owner_batch(batch))
            log.info("github owners: %s of %s", len(found), len(logins))
        return found

    def _owner_batch(self, batch: list[str], light: bool = False) -> dict[str, Any]:
        """
        One GraphQL request for a batch of owners. Contribution history is expensive, so
        when GitHub reports exceeded resource limits the batch is split in half and retried.
        """
        # Profile READMEs live in a repository named for the account (users) or in
        # `.github/profile/README.md` (organizations).
        fields = "\n".join(
            f"o{i}: repositoryOwner(login: {json.dumps(login)}) "
            f"{{ {OWNER_FIELDS_LIGHT if light else OWNER_FIELDS}"
            f" userReadme: repository(name: {json.dumps(login)}) "
            f"{{ {README_FIELDS.format(path='README.md')} }}"
            f" orgReadme: repository(name: \".github\") "
            f"{{ {README_FIELDS.format(path='profile/README.md')} }} }}"
            for i, login in enumerate(batch)
        )
        try:
            data = self.query(f"query {{ {fields} }}")
        except FetchError as error:
            # Heavy batches fail as exceeded resource limits or as gateway timeouts.
            heavy = any(sign in str(error) for sign in
                        ("RESOURCE_LIMITS_EXCEEDED", "HTTP 502", "HTTP 504"))
            if heavy and len(batch) == 1 and not light:
                log.warning("github owner %s: retrying without star detail", batch[0])
                return self._owner_batch(batch, light=True)
            if heavy and len(batch) == 1:
                # Its earlier record is kept, and the next run tries it again.
                log.warning("github owner %s: skipped after repeated timeouts", batch[0])
                return {}
            if not heavy:
                raise
            half = len(batch) // 2
            return {**self._owner_batch(batch[:half]), **self._owner_batch(batch[half:])}
        return {login.lower(): data.get(f"o{i}") for i, login in enumerate(batch)}

    def repositories(self, full_names: list[str]) -> dict[str, Any]:
        """Repositories by lowercased full name; a deleted one maps to None."""
        found: dict[str, Any] = {}
        for batch in _chunks(full_names, BATCH_SIZE):
            found.update(self._repository_batch(batch, REPO_FIELDS))
        return found

    def repository_stats(self, full_names: list[str]) -> dict[str, Any]:
        """
        Repositories with watcher and open-issue counts, by lowercased full name. A deleted
        one maps to None; one GitHub fails to serve even on its own is left out.
        """
        found: dict[str, Any] = {}
        for batch in _chunks(full_names, REPO_STATS_BATCH):
            found.update(self._repository_batch(batch, REPO_STATS_FIELDS, skip_failures=True))
        return found

    def _repository_batch(self, batch: list[str], fields: str,
                          skip_failures: bool = False) -> dict[str, Any]:
        """
        One GraphQL request for a batch of repositories. A batch that fails as too heavy,
        with a server error or over one bad repository is split in half and retried. A
        repository that still fails alone raises, or with `skip_failures` is left out.
        """
        aliases = []
        for i, full_name in enumerate(batch):
            owner, name = full_name.split("/", 1)
            aliases.append(f"r{i}: repository(owner: {json.dumps(owner)}, "
                           f"name: {json.dumps(name)}) {{ {fields} }}")
        try:
            data = self.query(f"query {{ {' '.join(aliases)} }}")
        except FetchError as error:
            if not _splittable(error) or (len(batch) == 1 and not skip_failures):
                raise
            if len(batch) == 1:
                log.warning("github repository %s: skipped: %s", batch[0], str(error)[:300])
                return {}
            half = len(batch) // 2
            return {**self._repository_batch(batch[:half], fields, skip_failures),
                    **self._repository_batch(batch[half:], fields, skip_failures)}
        return {full_name.lower(): data.get(f"r{i}") for i, full_name in enumerate(batch)}

    def search_organizations(self, name: str) -> list[dict[str, Any]]:
        query = json.dumps(f"{name} type:org")
        data = self.query(
            f"query {{ search(query: {query}, type: USER, first: 5) {{ nodes {{ "
            f"... on Organization {{ login name websiteUrl }} }} }} }}"
        )
        return [node for node in data["search"]["nodes"] if node]


def speaker_handles(snapshot: Snapshot) -> list[str]:
    """GitHub handles of speakers in this edition's catalog and every saved past one."""
    logins: set[str] = set()
    catalogs = ["rainfocus/sessions.json", *sorted(
        p.relative_to(snapshot.root).as_posix()
        for p in (snapshot.root / "editions").glob("*/sessions.json"))]
    items = [i for c in catalogs for i in snapshot.load_json(c)["items"]]
    for item in items:
        for person in item.get("participants") or []:
            for value in person.get("attributevalues") or []:
                if value.get("attribute") == "GitHub Handle":
                    login, status = parse_github_handle(value.get("value"))
                    if login and status == "candidate":
                        logins.add(login)
    return sorted(logins, key=str.lower)


def profile_github_logins(snapshot: Snapshot) -> list[str]:
    """
    GitHub logins people link from their own LinkedIn, X, Mastodon or homepage, so the
    build can give a GitHub account to speakers whose listing named none.
    """
    urls: list[Any] = []
    for rel_path, keys in (("brightdata/linkedin_profiles.json", ("bio_links",)),
                           ("brightdata/x_profiles.json", ("external_link",))):
        if snapshot.has(rel_path):
            for entry in snapshot.load_json(rel_path).values():
                for record in entry.get("records") or []:
                    for key in keys:
                        value = record.get(key)
                        urls += ([v.get("link") for v in value if isinstance(v, dict)]
                                 if isinstance(value, list) else [value])
    if snapshot.has("mastodon/profiles.json"):
        for profile in snapshot.load_json("mastodon/profiles.json").values():
            fields = (profile or {}).get("fields") or []
            urls += [f.get("url") for f in fields if f.get("verified_at")]
    if snapshot.has("websites/homepages.json"):
        for page in snapshot.load_json("websites/homepages.json").values():
            urls += page.get("rel_me") or []
    logins = set()
    for url in urls:
        classified = classify_social_url(url) if isinstance(url, str) else None
        if classified and classified[0] == "github":
            logins.add(classified[1])
    return sorted(logins, key=str.lower)


def sponsors(snapshot: Snapshot) -> list[dict[str, Any]]:
    result = snapshot.load_json("rainfocus/exhibitors.json")
    return [item for section in result.get("sectionList") or [result]
            for item in section.get("items") or []]


def match_sponsor_org(sponsor: dict[str, Any], candidates: list[dict[str, Any]]) -> str | None:
    """
    Accept a GitHub organization only if its website shares the sponsor link's domain.
    When several do (a company and its regional accounts), prefer the one whose name is
    the sponsor's name, then the shortest login.
    """
    domain = registrable_domain((sponsor.get("externalLink") or "").strip())
    if not domain:
        return None
    matches = [c for c in candidates if registrable_domain(c.get("websiteUrl")) == domain]
    name = org_key(sponsor["name"])
    matches.sort(key=lambda c: (org_key(c.get("name") or "") != name, len(c["login"])))
    return matches[0]["login"] if matches else None


def company_logins(owners: dict[str, Any]) -> list[str]:
    """Organization logins that users name in their GitHub company field, like `@github`."""
    logins = set()
    for node in owners.values():
        if node and node.get("__typename") == "User":
            logins.update(COMPANY_LOGIN.findall(node.get("company") or ""))
    return sorted((login for login in logins if login.lower() not in owners), key=str.lower)


def lookup_npm(fetcher: Fetcher, name: str) -> dict[str, Any] | None:
    url = f"https://registry.npmjs.org/{urllib.parse.quote(name, safe='@')}"
    try:
        doc = fetcher.json("GET", url, headers={"Accept": "application/json"})
    except FetchError:
        return None
    latest = (doc.get("dist-tags") or {}).get("latest")
    repository = doc.get("repository") or {}
    return {
        "name": doc.get("name"),
        "description": doc.get("description"),
        "latest_version": latest,
        "license": doc.get("license") if isinstance(doc.get("license"), str) else None,
        "homepage": doc.get("homepage"),
        "repository_url": repository.get("url") if isinstance(repository, dict) else repository,
        "url": f"https://www.npmjs.com/package/{name}",
    }


def lookup_pypi(fetcher: Fetcher, name: str) -> dict[str, Any] | None:
    try:
        doc = fetcher.json("GET", f"https://pypi.org/pypi/{name}/json")
    except FetchError:
        return None
    info = doc["info"]
    urls = info.get("project_urls") or {}
    source = next((v for k, v in urls.items() if k.lower() in {"source", "repository",
                                                              "source code", "github"}), None)
    return {
        "name": info.get("name"),
        "description": info.get("summary"),
        "latest_version": info.get("version"),
        "license": info.get("license_expression") or info.get("license") or None,
        "homepage": info.get("home_page") or urls.get("Homepage"),
        "repository_url": source,
        "url": f"https://pypi.org/project/{info.get('name') or name}/",
    }


def enrich(snapshot: Snapshot, fetcher: Fetcher, curation_dir: Path) -> dict[str, Any]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("enrich needs GITHUB_TOKEN; try GITHUB_TOKEN=$(gh auth token)")
    github = GitHubClient(fetcher, token)
    software = yaml.safe_load((curation_dir / "software.yaml").read_text())
    organizations = yaml.safe_load((curation_dir / "organizations.yaml").read_text())

    pinned_orgs = [o["github"] for o in organizations["organizations"].values() if o.get("github")]
    pinned_orgs += [o["github"] for o in software.get("mentioned_organizations", {}).values()
                    if o.get("github")]

    # Incremental: sponsors and owners already looked up are not fetched again.
    sponsor_matches: dict[str, Any] = (snapshot.load_json("github/sponsor-orgs.json")
                                       if snapshot.has("github/sponsor-orgs.json") else {})
    for sponsor in sponsors(snapshot):
        name = sponsor["name"].strip()
        if name in sponsor_matches:
            continue
        candidates = github.search_organizations(name)
        sponsor_matches[name] = {
            "link": sponsor.get("externalLink"),
            "candidates": candidates,
            "accepted": match_sponsor_org(sponsor, candidates),
        }
    snapshot.save_json("github/sponsor-orgs.json", sponsor_matches, url=GRAPHQL_URL,
                       method="POST")

    logins = speaker_handles(snapshot) + profile_github_logins(snapshot)
    curated_people = yaml.safe_load((curation_dir / "people.yaml").read_text()) or {}
    for entry in curated_people.get("people") or []:
        login = (entry.get("accounts") or {}).get("github")
        if login:
            logins.append(str(login))
    logins += [m["accepted"] for m in sponsor_matches.values() if m["accepted"]]
    logins += pinned_orgs
    # People removed at their request are not looked up again.
    removed = Exclusions.load(curation_dir)
    unique_logins = sorted({login.lower(): login for login in logins
                            if not removed.matches(f"gh:{login.lower()}")}.values(), key=str.lower)
    owners: dict[str, Any] = (snapshot.load_json("github/owners.json")
                              if snapshot.has("github/owners.json") else {})

    def stale(login: str) -> bool:
        # Records fetched before a field existed lack its key: the README for everyone,
        # the program flags and stars for users.
        node = owners.get(login.lower(), "missing")
        return node == "missing" or (bool(node) and (
            "userReadme" not in node
            or (node.get("__typename") == "User" and "isGitHubStar" not in node)))

    todo = [login for login in unique_logins if stale(login)]
    for start in range(0, len(todo), SAVE_EVERY):
        owners.update(github.owners(todo[start: start + SAVE_EVERY]))
        snapshot.save_json("github/owners.json", owners, url=GRAPHQL_URL, method="POST")
    # Organizations named in users' company fields become affiliation candidates.
    owners.update(github.owners([login for login in company_logins(owners) if stale(login)]))
    snapshot.save_json("github/owners.json", owners, url=GRAPHQL_URL, method="POST")

    claimed = sorted({r for entry in software["software"] for r in entry.get("repositories", [])},
                     key=str.lower)
    repos = github.repositories(claimed)
    snapshot.save_json("github/repos.json", repos, url=GRAPHQL_URL, method="POST")

    npm: dict[str, Any] = {}
    pypi: dict[str, Any] = {}
    for entry in software["software"]:
        for package in entry.get("packages", []):
            ecosystem, name = package.split(":", 1)
            if ecosystem == "npm":
                npm[name] = lookup_npm(fetcher, name)
            elif ecosystem == "pypi":
                pypi[name] = lookup_pypi(fetcher, name)
    snapshot.save_json("registries/npm.json", npm, url="https://registry.npmjs.org/")
    snapshot.save_json("registries/pypi.json", pypi, url="https://pypi.org/pypi/")
    snapshot.write_manifest()

    return {
        "github_owners": len(owners),
        "github_owners_found": sum(1 for v in owners.values() if v),
        "claimed_repositories": len(repos),
        "claimed_repositories_found": sum(1 for v in repos.values() if v),
        "sponsor_orgs_matched": sum(1 for v in sponsor_matches.values() if v["accepted"]),
        "sponsors": len(sponsor_matches),
        "npm_found": sum(1 for v in npm.values() if v),
        "pypi_found": sum(1 for v in pypi.values() if v),
    }


def social_targets(snapshot: Snapshot, curation_dir: Path) -> tuple[list[str], list[str]]:
    """
    Websites and Bluesky actors to look up: what speakers list at the event, what their
    GitHub profiles declare, and what curated people give. Profile URLs (LinkedIn, X, …)
    are accounts, not websites, so they are left out of the website list.
    """
    websites: list[str] = []
    actors: list[str] = []
    for item in snapshot.load_json("rainfocus/sessions.json")["items"]:
        for person in item.get("participants") or []:
            for value in person.get("attributevalues") or []:
                if value.get("attribute") == "Bluesky":
                    actors.append(value.get("value") or "")
    if snapshot.has("github/owners.json"):
        for node in snapshot.load_json("github/owners.json").values():
            if not node or node.get("__typename") != "User":
                continue
            for platform, url in github_social_links(node):
                if platform == "bluesky":
                    actors.append(url)
                elif platform == "website":
                    websites.append(url)
    curated = yaml.safe_load((curation_dir / "people.yaml").read_text()) or {}
    for entry in curated.get("people") or []:
        accounts = entry.get("accounts") or {}
        if accounts.get("website"):
            websites.append(accounts["website"])
        if accounts.get("bluesky"):
            actors.append(accounts["bluesky"])

    def keep_website(url: str) -> bool:
        url = url.strip()
        full = url if "://" in url else f"https://{url}"
        return (public_http_url(full) and classify_social_url(full) is None and keep_link(full)
                and registrable_domain(full) not in NOT_PERSONAL_DOMAINS)

    # One fetch per site, however the address was written (scheme, `www.`, trailing slash).
    by_site: dict[str, str] = {}
    for url in websites:
        url = url.strip()
        if url and keep_website(url):
            full = url if "://" in url else f"https://{url}"
            by_site.setdefault(website_id(full), full)
    removed = Exclusions.load(curation_dir)
    website_list = sorted(url for site, url in by_site.items() if not removed.matches(site))
    handles = {normalize_handle(a)[0] for a in actors}
    return website_list, sorted(h for h in handles
                                if h and not removed.matches(social_account_id("bluesky", h)))


# Public hashtag timelines for attendee discovery; Bluesky search needs a login.
HASHTAG_HOSTS = ["mastodon.social", "hachyderm.io", "fosstodon.org", "infosec.exchange"]
HASHTAGS = ["GitHubUniverse", "GitHubUniverse2026", "GitHubUniverse26", "GHUniverse"]
HASHTAG_SINCE = "2026-09-01"
SOCIAL_STEPS = ("websites", "bluesky", "mastodon", "feeds", "hashtags", "org_websites")


def kb_person_handles(kb_dir: Path, platform: str) -> list[str]:
    """Handles of people's accounts on `platform` in the built kb, however they were found."""
    handles = []
    for path in sorted((kb_dir / "accounts" / platform).glob("*.yaml")):
        account = yaml.safe_load(path.read_text())["social_account"]
        if account.get("owner", "").startswith("person:"):
            handles.append(account["handle"])
    return sorted(set(handles), key=str.lower)


def kb_person_websites(kb_dir: Path) -> list[str]:
    """
    Every person's website in the built knowledge base, wherever it was linked from
    (LinkedIn, X, Mastodon, a homepage), so its title and feeds can be read.
    """
    urls = []
    for path in sorted((kb_dir / "websites").rglob("*.yaml")):
        site = yaml.safe_load(path.read_text())["website"]
        if site.get("owner", "").startswith("person:"):
            urls.append(site["url"])
    return sorted(set(urls))


def kb_org_websites(kb_dir: Path) -> list[str]:
    """Websites of every organization in the built knowledge base."""
    urls = []
    for path in sorted((kb_dir / "organizations").glob("*.md")):
        front = path.read_text().split("---\n")[1]
        org = yaml.safe_load(front)["organization"]
        if org.get("website"):
            urls.append(org["website"])
    return sorted(set(urls))


def mastodon_handles(snapshot: Snapshot) -> list[str]:
    """
    Mastodon accounts that GitHub profiles or personal websites point to. Authors found on
    hashtag timelines are never looked up: their posts are all the build needs.
    """
    urls: list[str] = []
    if snapshot.has("github/owners.json"):
        for node in snapshot.load_json("github/owners.json").values():
            if node and node.get("__typename") == "User":
                urls += [url for _platform, url in github_social_links(node)]
    if snapshot.has("websites/homepages.json"):
        for page in snapshot.load_json("websites/homepages.json").values():
            urls += (page.get("rel_me") or []) + (page.get("social_links") or [])
    handles = []
    for url in urls:
        classified = classify_social_url(url)
        if classified and classified[0] == "mastodon":
            handles.append(classified[1])
    return sorted(set(handles), key=str.lower)


def enrich_social(snapshot: Snapshot, fetcher: Fetcher, curation_dir: Path, kb_dir: Path,
                  steps: tuple[str, ...] = SOCIAL_STEPS) -> dict[str, Any]:
    """
    Public, unauthenticated sources, in order: personal websites (their rel=me links can
    name more Bluesky and Mastodon accounts), Bluesky profiles, Mastodon profiles, recent
    writing from the websites' feeds, and Mastodon hashtag timelines for attendees.
    """
    report: dict[str, Any] = {}
    websites, actors = social_targets(snapshot, curation_dir)
    removed = Exclusions.load(curation_dir)
    if "websites" in steps:
        # Incremental: a site fetched before is kept; delete the file to refetch all.
        homepages: dict[str, Any] = (snapshot.load_json("websites/homepages.json")
                                     if snapshot.has("websites/homepages.json") else {})
        known = {website_id(u if "://" in u else f"https://{u}") for u in homepages}
        for url in [*websites, *kb_person_websites(kb_dir)]:
            full = url if "://" in url else f"https://{url}"
            if website_id(full) in known or removed.matches(website_id(full)):
                continue
            known.add(website_id(full))
            homepages[url] = fetch_homepage(fetcher, full)
            log.info("website %s: %s", url, homepages[url].get("status"))
        snapshot.save_json("websites/homepages.json", homepages, url="https://", method="GET")
        report["websites"] = len(homepages)
        report["websites_ok"] = sum(1 for p in homepages.values() if p.get("status") == 200)
    homepages = (snapshot.load_json("websites/homepages.json")
                 if snapshot.has("websites/homepages.json") else {})

    if "bluesky" in steps:
        for page in homepages.values():
            for link in page.get("rel_me") or []:
                classified = classify_social_url(link)
                if classified and classified[0] == "bluesky":
                    actors.append(classified[1])
        actors += kb_person_handles(kb_dir, "bluesky")
        unique_actors = sorted({h for h in (normalize_handle(a)[0] for a in actors)
                                if h and not removed.matches(social_account_id("bluesky", h))})
        profiles = fetch_profiles(fetcher, unique_actors)
        snapshot.save_json("bluesky/profiles.json", profiles,
                           url="https://public.api.bsky.app/xrpc/app.bsky.actor.getProfiles")
        report["bluesky_found"] = sum(1 for p in profiles.values() if p)

    if "mastodon" in steps:
        removed = Exclusions.load(curation_dir)
        handles = [h for h in mastodon_handles(snapshot) + kb_person_handles(kb_dir, "mastodon")
                   if not removed.matches(social_account_id("mastodon", h))]
        mastodon = lookup_profiles(fetcher, sorted(set(handles), key=str.lower))
        snapshot.save_json("mastodon/profiles.json", mastodon,
                           url="https://mastodon.social/api/v1/accounts/lookup")
        report["mastodon_found"] = sum(1 for p in mastodon.values() if p)

    if "feeds" in steps:
        # Comment feeds hold other people's comments, not the site owner's writing.
        # Cached homepages can predate removal requests; screen their site identities
        # before discovering feeds, including feeds hosted on another domain.
        feed_urls = sorted({f for url, page in homepages.items()
                            if not removed.matches(website_id(
                                url if "://" in url else f"https://{url}"))
                            and page.get("status") == 200
                            for f in page.get("feeds") or [] if "comments" not in f.lower()})
        feeds = {url: fetch_feed(fetcher, url, max_items=FEED_ITEMS) for url in feed_urls}
        snapshot.save_json("feeds/feeds.json", feeds, url="https://", method="GET")
        report["feeds_ok"] = sum(1 for f in feeds.values() if not f.get("error"))

    if "org_websites" in steps:
        existing = (snapshot.load_json("websites/org-homepages.json")
                    if snapshot.has("websites/org-homepages.json") else {})
        for url in kb_org_websites(kb_dir):
            if url not in existing:
                existing[url] = fetch_homepage(fetcher, url)
        snapshot.save_json("websites/org-homepages.json", existing, url="https://")
        report["org_websites_ok"] = sum(1 for p in existing.values() if p.get("status") == 200)

    if "hashtags" in steps:
        timelines = {f"{host}#{tag}": hashtag_posts(fetcher, host, tag, since=HASHTAG_SINCE)
                     for host in HASHTAG_HOSTS for tag in HASHTAGS}
        # Posts by people removed at their request are never stored again.
        removed = Exclusions.load(curation_dir)
        for timeline in timelines.values():
            timeline["posts"] = [p for p in timeline["posts"]
                                 if not removed.matches(social_account_id(
                                     "mastodon", (p.get("account") or {}).get("acct") or ""))]
        snapshot.save_json("mastodon/hashtags.json", timelines,
                           url="https://mastodon.social/api/v1/timelines/tag/GitHubUniverse")
        report["hashtag_posts"] = sum(len(t["posts"]) for t in timelines.values())

    snapshot.write_manifest()
    return report


# Which manifests to read for a repository, by its primary language.
LANGUAGE_ECOSYSTEMS = {"TypeScript": ["npm"], "JavaScript": ["npm"], "Python": ["pypi"],
                       "Go": ["go"], "Rust": ["crates"]}


def enrich_packages(snapshot: Snapshot, fetcher: Fetcher, kb_dir: Path) -> dict[str, Any]:
    """
    Packages that repositories owned by people and organizations in the knowledge base
    publish, verified against their registries. Only the manifests for each repository's
    language are read, and repositories already checked are skipped.
    """
    rel_path = "packages/repo-packages.json"
    results: dict[str, Any] = snapshot.load_json(rel_path) if snapshot.has(rel_path) else {}
    for path in sorted((kb_dir / "repositories").rglob("*.yaml")):
        repo = yaml.safe_load(path.read_text())["repository"]
        ecosystems = LANGUAGE_ECOSYSTEMS.get(repo.get("primary_language") or "")
        if not repo.get("owner") or not ecosystems or repo["full_name"] in results:
            continue
        checked, packages = [], []
        for ecosystem in ecosystems:
            for filename in MANIFESTS[ecosystem]:
                url = RAW_URL.format(full_name=repo["full_name"], ref="HEAD", file=filename)
                response = fetcher.fetch(url)
                checked.append({"file": filename, "status": response.status})
                if response.status != 200:
                    continue
                text = response.body.decode("utf-8", errors="replace")
                names = manifest_names(text, filename)
                packages += [{**verify_package(fetcher, repo["full_name"], eco, name, filename),
                              "declared_in": filename}
                             for eco, name in names]
                if names:
                    break
        results[repo["full_name"]] = {"checked": checked, "packages": packages}
    snapshot.save_json(rel_path, results, url="https://raw.githubusercontent.com/")
    snapshot.write_manifest()
    found = [p for r in results.values() for p in r["packages"]]
    return {"repositories": len(results), "declared": len(found),
            "verified": sum(1 for p in found if p.get("verified"))}


def kb_repository_names(kb_dir: Path) -> list[str]:
    """Full names of every repository in the built knowledge base."""
    names: dict[str, str] = {}
    for path in sorted((kb_dir / "repositories").rglob("*.yaml")):
        repo = yaml.load(path.read_text(), Loader=yaml.CSafeLoader)["repository"]
        names.setdefault(repo["full_name"].lower(), repo["full_name"])
    return sorted(names.values(), key=str.lower)


def _parse_utc(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def refresh_repositories(snapshot: Snapshot, github: GitHubClient, kb_dir: Path,
                         max_age_hours: float = REPO_STATS_MAX_AGE_HOURS) -> dict[str, Any]:
    """
    Read stars, forks, watchers and open issues for every repository in the built
    knowledge base straight from GitHub, with the time each was read. Owner records carry
    counts too, but they are only as fresh as the owner's last fetch, and nothing records
    when that was.

    Records go to `github/repo-stats.json` by lowercased full name, each with its
    `fetched_at`, and are saved after each group so an interrupted run keeps its progress.
    Records younger than `max_age_hours` are not read again. A repository GitHub no longer
    has (deleted, or renamed without a redirect) is recorded as missing. One that GitHub
    fails to serve even on its own keeps its earlier record and is reported as unfetched.
    """
    names = kb_repository_names(kb_dir)
    stats: dict[str, Any] = (snapshot.load_json(REPO_STATS_PATH)
                             if snapshot.has(REPO_STATS_PATH) else {})
    cutoff = datetime.now(UTC) - timedelta(hours=max_age_hours)

    def fresh(name: str) -> bool:
        record = stats.get(name.lower())
        return bool(record) and _parse_utc(record["fetched_at"]) > cutoff

    todo = [name for name in names if not fresh(name)]
    counts = {"refreshed": 0, "missing": 0}
    unfetched: list[str] = []
    renamed: list[str] = []
    stopped_early = False
    for start in range(0, len(todo), REPO_STATS_SAVE_EVERY):
        group = todo[start: start + REPO_STATS_SAVE_EVERY]
        read = 0
        for batch in _chunks(group, REPO_STATS_BATCH):
            found = github.repository_stats(batch)
            fetched_at = utc_now()
            for name in batch:
                key, node = name.lower(), found.get(name.lower())
                if key not in found:
                    unfetched.append(name)
                elif node is None:
                    stats[key] = {"missing": True, "fetched_at": fetched_at}
                    counts["missing"] += 1
                else:
                    # GitHub follows a rename to the repository's new name.
                    if node["nameWithOwner"].lower() != key:
                        renamed.append(f"{name} -> {node['nameWithOwner']}")
                    stats[key] = {**node, "fetched_at": fetched_at}
                    counts["refreshed"] += 1
            read += len(found)
        snapshot.save_json(REPO_STATS_PATH, stats, url=GRAPHQL_URL, method="POST")
        snapshot.write_manifest()
        log.info("repository stats: %s of %s", start + len(group), len(todo))
        if read == 0:
            # Every request failed even one repository at a time: GitHub is down for us.
            log.error("github served none of %s repositories; stopping", len(group))
            stopped_early = True
            break

    return {"repositories": len(names), "skipped_fresh": len(names) - len(todo),
            "requested": len(todo), **counts, "unfetched": len(unfetched),
            "unfetched_names": unfetched, "renamed": renamed, "stopped_early": stopped_early}
