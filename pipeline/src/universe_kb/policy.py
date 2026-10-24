"""
The data policy (`docs/data-policy.md` at the repository root) as code: what may be
committed to `raw/` and `kb/`.

- **Personal accounts:** Instagram, Threads, Facebook and TikTok accounts are left out by
  default, wherever a source links them.
- **Removal requests:** people listed under `exclude` in `curation/people.yaml` are left
  out of every build, collection skips their accounts, and `universe-kb scrub` deletes
  their raw data and bios.
- **Minimal caches:** `prune_raw` keeps only the parts of the caches about people that the
  built knowledge base uses.
- **Raw caches:** `sanitize_raw` runs on every raw file before it is written. It strips
  data about people other than a profile's owner and scraper bookkeeping, redacts contact
  details, preserves self-written public bio text, filters added sensitive attributes,
  and keeps locations at city level. `universe-kb sanitize-raw` reapplies it
  to the whole snapshot.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import yaml

from universe_kb import privacy, sensitive
from universe_kb.web import classify_social_url

if TYPE_CHECKING:
    from universe_kb.snapshot import Snapshot

# Whether to remove sensitive attributes people state about themselves in text they wrote
# and published: speaker bios, profile bios and about text, profile READMEs, their own
# websites' descriptions, and display names. The policy keeps such self-written text
# verbatim, apart from contact details. The pipeline never adds or derives a sensitive
# attribute anywhere else: structured fields, interests, selected posts, evidence quotes
# and generated bios are always filtered.
REDACT_SELF_STATED = False

# Platforms whose accounts are personal by default; the user decides on each later.
EXCLUDED_PLATFORMS = ("instagram", "threads", "facebook", "tiktok")
# Sites whose profile pages are personal or only collect someone's other links.
EXCLUDED_SITES = ("reddit", "linktree")
_EXCLUDED_HOSTS = {"instagram.com": "instagram", "threads.net": "threads",
                   "threads.com": "threads", "facebook.com": "facebook", "fb.com": "facebook",
                   "fb.me": "facebook", "tiktok.com": "tiktok", "reddit.com": "reddit",
                   "linktr.ee": "linktree"}
# Group and link-hub pages: their links belong to members, not to the page's owner.
AGGREGATOR_HOSTS = {"skool.com", "meetup.com", "linktr.ee", "bio.link", "beacons.ai",
                    "lu.ma", "luma.com"}
# Profile text that asks not to be collected or quoted.
NO_SCRAPE = re.compile(r"#no(?:bot|scrape|scraping|search|index|archive|quote)\b"
                       r"|\bdo not (?:scrape|quote|archive)|\bno (?:scraping|bots)\b",
                       re.IGNORECASE)
# Phrases that say the poster will be there; a tagged post without one adds no one.
ATTENDING = re.compile(
    r"\b(I'?ll be|I will be|I'?m (at|in|heading|going|speaking|attending)|I am (at|going|"
    r"speaking|attending)|see you at|heading to|attending|speaking at|we'?ll be at|"
    r"come (say hi|find me|see me)|catch me at|meet me at|join me at)\b",
    re.IGNORECASE,
)
# A post that says the poster will not be there.
NOT_ATTENDING = re.compile(
    r"\b(not|n't|never|won'?t|can'?t|cannot|unable to|wish I (were|was|could))\b"
    r"[^.!?\n]{0,25}\b(be|go|going|attend|attending|make it|there|at)\b"
    r"|\b(missing|skipping|watching (the )?(live)?stream)\b",
    re.IGNORECASE,
)


def says_attending(text: str | None) -> bool:
    """Whether a post states that its author will be at the event."""
    return bool(text) and bool(ATTENDING.search(text or "")) and not NOT_ATTENDING.search(
        text or "")


def excluded_platform(url: str | None) -> str | None:
    """The excluded platform a profile URL belongs to, if any."""
    if not url:
        return None
    classified = classify_social_url(url)
    if classified and classified[0] in EXCLUDED_PLATFORMS:
        return classified[0]
    host = (urlparse(url if "://" in url else f"https://{url}").hostname or "").lower()
    return _EXCLUDED_HOSTS.get(re.sub(r"^(?:www|m|mobile|web|l)\.", "", host))


def excluded_name(name: str | None) -> bool:
    """A platform name, as a catalog attribute or GitHub provider gives it, that is excluded."""
    return (name or "").strip().lower() in EXCLUDED_PLATFORMS


def email_in_url(url: str | None) -> bool:
    """A link whose host part carries a user name, such as an email address typed as a URL."""
    return bool(url) and "://" in (url or "") and "@" in urlparse(url).netloc


def keep_link(url: Any) -> bool:
    return not (isinstance(url, str) and (excluded_platform(url) or email_in_url(url)
                                          or url.lower().startswith("mailto:")))


# --- Free text -------------------------------------------------------------------------


def person_text(text: Any) -> Any:
    """
    What someone wrote about themselves: verbatim apart from contact details, unless
    `REDACT_SELF_STATED` also removes the clauses that state a sensitive attribute.
    """
    if not isinstance(text, str) or privacy.is_identifier(None, text):
        return text
    cleaned = privacy.redact_addresses(privacy.redact(text))
    return sensitive.redact(cleaned) if REDACT_SELF_STATED else cleaned


def professional_readme(text: Any) -> Any:
    """Keep professional README blocks, excluding personal accounts and listening widgets."""
    if not isinstance(text, str):
        return text

    def personal_account(block: str) -> bool:
        for url in re.findall(r"https?://[^\s<>\"']+", block):
            try:
                parsed = urlparse(url)
                host = (parsed.hostname or "").lower()
                if excluded_platform(url):
                    return True
            except ValueError:
                continue
            if (host == "open.spotify.com" and parsed.path.startswith("/user/")) or (
                "spotify-github-profile" in host or "spotify-recently-played" in host
            ):
                return True
        return False

    return person_text(
        "\n\n".join(block for block in text.split("\n\n") if not personal_account(block))
    )


def sanitize_text(rel_path: str, text: str) -> str:
    """Sanitize saved text/HTML before publication; structured venues retain directions."""
    return privacy.redact_addresses(privacy.redact(text))


def org_text(text: Any) -> Any:
    """What an organization says about itself, without contact details or street addresses."""
    if not isinstance(text, str) or privacy.is_identifier(None, text):
        return text
    return privacy.redact_addresses(privacy.redact(text))


def person_name(text: Any) -> Any:
    """A name someone gave themselves, without contact details."""
    if not isinstance(text, str):
        return text
    return sensitive.strip_symbols(privacy.redact(text)) if REDACT_SELF_STATED else (
        privacy.redact(text))


def location(text: Any) -> Any:
    return sensitive.city_level(text) if isinstance(text, str) else text


def without_sensitive_names(names: Any) -> Any:
    """A list of names (repositories, organizations) without those that state an attribute."""
    if not isinstance(names, list):
        return names
    return [n for n in names if not sensitive.is_sensitive(
        n if isinstance(n, str) else n.get("nameWithOwner") or n.get("login") or n.get("name")
        if isinstance(n, dict) else None)]


def apply(record: dict[str, Any], fields: dict[str, Callable[[Any], Any]]) -> None:
    for key, rule in fields.items():
        if key in record:
            record[key] = rule(record[key])


# --- Raw caches ------------------------------------------------------------------------


def _github_owner(node: Any) -> Any:
    if not isinstance(node, dict):
        return node
    if node.get("__typename") != "User":
        apply(node, {"description": org_text, "location": location})
        readme = node.get("orgReadme") or {}
        if isinstance(readme.get("object"), dict) and readme["object"].get("text"):
            readme["object"]["text"] = org_text(readme["object"]["text"])
        return node
    # Whom someone sponsors names other people and says where their money goes; stars
    # and star lists are likes, which can imply health or beliefs. Counts stay.
    node.pop("sponsoring", None)
    node.pop("lists", None)
    if isinstance(node.get("starredRepositories"), dict):
        node["starredRepositories"] = {
            "totalCount": node["starredRepositories"].get("totalCount")}
    apply(node, {"bio": person_text, "location": location, "name": person_name})
    if not keep_link(node.get("websiteUrl")):
        node["websiteUrl"] = None
    social = node.get("socialAccounts") or {}
    if isinstance(social.get("nodes"), list):
        social["nodes"] = [s for s in social["nodes"] if isinstance(s, dict)
                           and not excluded_name(s.get("provider"))
                           and keep_link(s.get("url"))]
    readme = node.get("userReadme") or {}
    if isinstance(readme.get("object"), dict) and readme["object"].get("text"):
        readme["object"]["text"] = professional_readme(readme["object"]["text"])
    orgs = node.get("organizations") or {}
    if isinstance(orgs.get("nodes"), list):
        orgs["nodes"] = without_sensitive_names(orgs["nodes"])
    return node


def _homepage(page: Any, url: str = "") -> Any:
    if not isinstance(page, dict):
        return page
    host = (urlparse(page.get("final_url") or url).hostname or "").removeprefix("www.")
    if any(host == h or host.endswith(f".{h}") for h in AGGREGATOR_HOSTS):
        page["social_links"], page["rel_me"] = [], []
    apply(page, {"title": person_text, "description": person_text})
    if isinstance(page.get("og"), dict):
        apply(page["og"], {"title": person_text, "description": person_text,
                           "site_name": person_text})
    for key in ("rel_me", "social_links"):
        if isinstance(page.get(key), list):
            page[key] = [u for u in page[key] if keep_link(u)]
    return page


def _mastodon_profile(profile: Any) -> Any:
    if not isinstance(profile, dict) or NO_SCRAPE.search(str(profile.get("bio") or "")):
        return None
    apply(profile, {"bio": person_text, "display_name": person_name})
    if isinstance(profile.get("fields"), list):
        profile["fields"] = [f for f in profile["fields"] if isinstance(f, dict)
                             and keep_link(f.get("url")) and keep_link(f.get("value"))
                             and not sensitive.is_sensitive(f"{f.get('name')} {f.get('value')}")]
    return profile


POST_FIELDS = {"id", "url", "created_at", "text"}
ACCOUNT_FIELDS = {"acct", "url", "display_name", "bot"}


def _hashtag_timeline(timeline: Any) -> Any:
    """
    Only the posts of people who say in one of them that they will attend: their posts,
    minus language and tag bookkeeping, and their account's handle and name. Everyone
    else's posts, bots, and accounts that ask not to be collected are dropped. Sensitive
    post clauses are removed; retained attendance evidence must survive that removal.
    """
    if not isinstance(timeline, dict):
        return timeline
    posts = [
        (p, sensitive.redact(privacy.redact_addresses(privacy.redact(p.get("text") or ""))))
        for p in timeline.get("posts") or [] if isinstance(p, dict)
    ]

    def acct(post: dict[str, Any]) -> str:
        return str((post.get("account") or {}).get("acct") or "").lower()

    attending = {acct(p) for p, text in posts
                 if says_attending(p.get("text")) and says_attending(text)
                 and not (p.get("account") or {}).get("bot")
                 and not NO_SCRAPE.search(str((p.get("account") or {}).get("bio") or ""))}
    kept = []
    for post, text in posts:
        if not text or acct(post) not in attending:
            continue
        account = {k: v for k, v in (post.get("account") or {}).items() if k in ACCOUNT_FIELDS}
        apply(account, {"display_name": person_name})
        kept.append({**{k: v for k, v in post.items() if k in POST_FIELDS},
                     "text": text, "account": account})
    return {**timeline, "posts": kept}


def _bluesky_profile(profile: Any) -> Any:
    if isinstance(profile, dict):
        apply(profile, {"description": person_text, "display_name": person_name})
    return profile


def _feed(result: Any) -> Any:
    if isinstance(result, dict) and isinstance(result.get("items"), list):
        result["items"] = [i for i in result["items"] if isinstance(i, dict)
                           and not sensitive.is_sensitive(i.get("title"))]
    return result


def _catalog(data: dict[str, Any]) -> dict[str, Any]:
    data.pop("searchTimestamp", None)
    for item in data.get("items") or []:
        for participant in item.get("participants") or []:
            for key in CATALOG_BOOKKEEPING:
                participant.pop(key, None)
            apply(participant, {"bio": person_text, "globalBio": person_text})
            if isinstance(participant.get("attributevalues"), list):
                participant["attributevalues"] = [
                    a for a in participant["attributevalues"]
                    if not excluded_name(a.get("attribute")) and keep_link(a.get("value"))]
    return data


def _each(rule: Callable[[Any], Any]) -> Callable[[Any], Any]:
    return lambda data: {k: rule(v) for k, v in data.items()} if isinstance(data, dict) else data


def _feeds(data: Any) -> Any:
    # WordPress comment feeds hold other people's comments, not the owner's writing.
    return {k: _feed(v) for k, v in data.items() if "comments" not in k.lower()}


def _homepages(data: Any) -> Any:
    return {k: _homepage(v, k) for k, v in data.items() if not email_in_url(k)}


TOKEN_KEYS = {"widgetToken", "apiProfileToken", "videoPlayerFPToken", "rfcsrf"}


def _without_tokens(value: Any) -> Any:
    """A page payload without the access tokens the portal embeds, at any depth."""
    if isinstance(value, dict):
        return {k: _without_tokens(v) for k, v in value.items() if k not in TOKEN_KEYS}
    if isinstance(value, list):
        return [_without_tokens(v) for v in value]
    return value


def _repository_urls(value: Any) -> Any:
    """Registry repository URLs without a user name before the host."""
    if isinstance(value, dict):
        return {k: (re.sub(r"(?<=://)[^/@\s]+@", "", v)
                    if k == "repository_url" and isinstance(v, str) else _repository_urls(v))
                for k, v in value.items()}
    if isinstance(value, list):
        return [_repository_urls(v) for v in value]
    return value


CATALOG_BOOKKEEPING = {"es_metadata_id", "modified", "eventId"}


def _brightdata(dataset: str) -> Callable[[Any], Any]:
    from universe_kb.brightdata import sanitize

    def rule(data: Any) -> Any:
        for entry in data.values():
            entry["records"] = [sanitize(dataset, r) for r in entry.get("records") or []]
        return data
    return rule


RAW_RULES: dict[str, Callable[[Any], Any]] = {
    "github/owners.json": _each(_github_owner),
    "websites/homepages.json": _homepages,
    "websites/org-homepages.json": _each(lambda page: page if not isinstance(page, dict)
                                         else {**page, "description": org_text(
                                             page.get("description"))}),
    "packages/repo-packages.json": _repository_urls,
    "registries/npm.json": _repository_urls,
    "registries/pypi.json": _repository_urls,
    # A profile that asks not to be collected is deleted; null means not found.
    "mastodon/profiles.json": lambda d: {k: _mastodon_profile(v) for k, v in d.items()
                                         if v is None or _mastodon_profile(v) is not None},
    "mastodon/hashtags.json": _each(_hashtag_timeline),
    "bluesky/profiles.json": _each(_bluesky_profile),
    "feeds/feeds.json": _feeds,
    "rainfocus/sessions.json": _catalog,
}


def sanitize_raw(rel_path: str, data: Any) -> Any:
    """Apply the data policy to one raw JSON file's data before it is committed."""
    rule = RAW_RULES.get(rel_path)
    if rule is None and rel_path.startswith("brightdata/"):
        rule = _brightdata(Path(rel_path).stem)
    if rule is None and re.fullmatch(r"editions/[^/]+/sessions\.json", rel_path):
        rule = _catalog
    if rule is None and re.fullmatch(r"(?:rainfocus|editions/[^/]+)/pages/[^/]+\.json",
                                     rel_path):
        rule = _without_tokens
    if rule is not None:
        data = rule(data)
    return privacy.redact_payload(data)


# --- Removal requests ------------------------------------------------------------------


def exclusion_fingerprint(key: str) -> str:
    """A reproducible, pseudonymous matching key; known identities remain guessable."""
    return hashlib.sha256(key.strip().casefold().encode("utf-8")).hexdigest()


@dataclass
class Exclusions:
    """
    Suppress normalized person/account/website keys without publishing their plaintext
    identities or removal reasons. Fingerprints are dictionary-testable, not anonymous.
    """

    fingerprints: set[str] = field(default_factory=set)

    @classmethod
    def load(cls, curation_dir: Path) -> Exclusions:
        data = yaml.safe_load((curation_dir / "people.yaml").read_text()) or {}
        found = cls()
        entries = data.get("exclude", [])
        if not isinstance(entries, list):
            raise ValueError("Exclusions must be a list of sha256 fingerprints")
        for entry in entries:
            if (not isinstance(entry, dict) or set(entry) != {"sha256"}
                    or not isinstance(entry["sha256"], str)
                    or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])):
                raise ValueError("Each exclusion must contain only a lowercase sha256 fingerprint")
            found.fingerprints.add(entry["sha256"])
        return found

    def add_keys(self, keys: set[str]) -> None:
        self.fingerprints.update(exclusion_fingerprint(key) for key in keys)

    def matches(self, key: str | None) -> bool:
        return key is not None and exclusion_fingerprint(key) in self.fingerprints

    def covers(self, person_id: str | None, keys: set[str]) -> bool:
        return self.matches(person_id) or any(self.matches(key) for key in keys)


def forget_raw(snapshot: Snapshot, exclusions: Exclusions) -> dict[str, int]:
    """
    Delete raw cache entries whose normalized identity keys match the exclusion
    fingerprints. Returns the number of entries deleted from each file. The official
    catalogs keep their listings; the build leaves those people out.
    """
    from universe_kb.people import social_account_id, website_id

    def account_key(url: str) -> str | None:
        classified = classify_social_url(url)
        return social_account_id(*classified) if classified else None

    rules: dict[str, Callable[[str], str | None]] = {
        "github/owners.json": lambda login: f"gh:{login.lower()}",
        "bluesky/profiles.json": lambda handle: social_account_id("bluesky", handle),
        "mastodon/profiles.json": lambda acct: social_account_id("mastodon", acct),
        "websites/homepages.json": lambda url: website_id(
            url if "://" in url else f"https://{url}"),
    }
    rules |= {rel: account_key for rel in snapshot.entries if rel.startswith("brightdata/")}
    report: dict[str, int] = {}
    dropped_feeds: set[str] = set()
    for rel_path, key_of in rules.items():
        if not snapshot.has(rel_path):
            continue
        data = snapshot.load_json(rel_path)
        gone = [k for k in data if exclusions.matches(key_of(k))]
        if rel_path == "websites/homepages.json":
            dropped_feeds |= {f for k in gone for f in (data[k] or {}).get("feeds") or []}
        for k in gone:
            del data[k]
        if gone and snapshot.rewrite_json(rel_path, data):
            report[rel_path] = len(gone)
    if snapshot.has("mastodon/hashtags.json"):
        timelines = snapshot.load_json("mastodon/hashtags.json")
        count = 0
        for timeline in timelines.values():
            posts = timeline.get("posts") or []
            kept = [p for p in posts if not exclusions.matches(social_account_id(
                "mastodon", (p.get("account") or {}).get("acct") or ""))]
            count += len(posts) - len(kept)
            timeline["posts"] = kept
        if count and snapshot.rewrite_json("mastodon/hashtags.json", timelines):
            report["mastodon/hashtags.json"] = count
    if dropped_feeds and snapshot.has("feeds/feeds.json"):
        homepages = (snapshot.load_json("websites/homepages.json")
                     if snapshot.has("websites/homepages.json") else {})
        still_used = {f for page in homepages.values() for f in (page or {}).get("feeds") or []}
        feeds = snapshot.load_json("feeds/feeds.json")
        gone = [f for f in feeds if f in dropped_feeds - still_used]
        for f in gone:
            del feeds[f]
        if gone and snapshot.rewrite_json("feeds/feeds.json", feeds):
            report["feeds/feeds.json"] = len(gone)
    return report


def prune_raw(snapshot: Snapshot, payloads: dict[str, dict[str, Any]]) -> dict[str, int]:
    """
    Keep only what the built knowledge base uses from the caches about people, given its
    entity payloads: profiles of accounts it holds, homepages of its websites with only
    the profile links it accepted as the owner's, their feeds, and the X posts it cites.
    Everything else in those caches is data about someone the knowledge base does not
    describe, or posts it does not show. A build from the pruned snapshot is unchanged.
    """
    from universe_kb.people import social_account_id, website_id

    accounts = {k for k in payloads if k.startswith("acct:")}
    websites = {k: v for k, v in payloads.items() if k.startswith("site:")}
    cited = {e.get("url") for p in payloads.values() if p.get("person")
             for e in p.get("recent_writing") or []}
    cited |= {e.get("url") for p in payloads.values() if str(p.get("id", "")).startswith(
        "person:") for part in p.get("participations") or [] for e in part.get("evidence") or []}

    def account_key(url: str) -> str | None:
        classified = classify_social_url(url)
        return social_account_id(*classified) if classified else None

    report: dict[str, int] = {}

    def rewrite(rel_path: str, data: Any, before: int, after: int) -> None:
        if snapshot.rewrite_json(rel_path, data):
            report[rel_path] = before - after

    for rel_path, key_of in (
            ("mastodon/profiles.json", lambda k: social_account_id("mastodon", k)),
            ("bluesky/profiles.json", lambda k: social_account_id("bluesky", k)),
            ("brightdata/linkedin_profiles.json", account_key),
            ("brightdata/x_profiles.json", account_key),
            ("brightdata/linkedin_companies.json", account_key)):
        if not snapshot.has(rel_path):
            continue
        data = snapshot.load_json(rel_path)
        kept = {k: v for k, v in data.items() if key_of(k) in accounts and not (
            rel_path.startswith("brightdata/") and not any(
                not r.get("error_code") for r in (v or {}).get("records") or []))}
        if rel_path == "brightdata/x_profiles.json":
            for entry in kept.values():
                for record in entry.get("records") or []:
                    record["posts"] = [p for p in record.get("posts") or []
                                       if p.get("post_url") in cited]
        rewrite(rel_path, kept, len(data), len(kept))

    if snapshot.has("websites/homepages.json"):
        pages = snapshot.load_json("websites/homepages.json")
        kept_pages = {}
        for url, page in pages.items():
            site = websites.get(website_id(url if "://" in url else f"https://{url}"))
            if site is None:
                continue
            linked = set(site.get("linked_accounts") or [])
            if isinstance(page, dict):
                page["social_links"] = [u for u in page.get("social_links") or []
                                        if account_key(u) in linked]
            kept_pages[url] = page
        rewrite("websites/homepages.json", kept_pages, len(pages), len(kept_pages))
        if snapshot.has("feeds/feeds.json"):
            used = {f for page in kept_pages.values() for f in (page or {}).get("feeds") or []}
            feeds = snapshot.load_json("feeds/feeds.json")
            kept_feeds = {k: v for k, v in feeds.items() if k in used}
            rewrite("feeds/feeds.json", kept_feeds, len(feeds), len(kept_feeds))
    return report
