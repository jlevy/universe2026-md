"""
Build the knowledge base: read `raw/` and `curation/`, resolve every entity and
reference, and write softschema artifacts to `kb/`.

The build is deterministic and offline. It validates each payload against its Pydantic
model before writing, writes into a fresh directory, and swaps it into place only when
every artifact was written, so a failed build never leaves a half-updated `kb/`.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import tempfile
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from zoneinfo import ZoneInfo

import yaml
from pydantic import BaseModel

from universe_kb import pages
from universe_kb.artifacts import path_for, payload, write_artifact
from universe_kb.bios import bundle_hash, check_bio, load_bios, person_bundle
from universe_kb.crawl import EDITION, PAST_EDITIONS, PORTAL_URL, SITE_URL, TIMEZONE
from universe_kb.graph import write_graph
from universe_kb.html_tree import html_to_markdown
from universe_kb.ids import (
    COMPANY_LOGIN,
    account_id,
    normalize_org_name,
    org_key,
    package_id,
    parse_github_handle,
    registrable_domain,
    repo_id,
    slugify,
    social_url,
)
from universe_kb.interests import Signal, infer_interests, interest_key
from universe_kb.manifests import MANIFESTS
from universe_kb.models import (
    Affiliation,
    BriefBio,
    Claim,
    Contributions,
    Event,
    EventDay,
    Evidence,
    Experience,
    Facet,
    Faq,
    GitHubAccount,
    Link,
    MediaIndex,
    MediaItem,
    Mention,
    Organization,
    Package,
    Participation,
    Person,
    PersonSession,
    Profile,
    Repository,
    Room,
    Session,
    SessionFacets,
    SessionSpeaker,
    Software,
    Source,
    Sponsorship,
    Term,
    TimeSlot,
    Venue,
)
from universe_kb.people import (
    AccountRegistry,
    PeopleIndex,
    bluesky_handle,
    build_profile,
    canonical_profile_url,
    canonical_website_url,
    filter_catalog_people,
    github_social_links,
    identity_keys,
    social_account_id,
    website_id,
)
from universe_kb.policy import REDACT_SELF_STATED, Exclusions, professional_readme, says_attending
from universe_kb.privacy import redact_payload
from universe_kb.profile_sources import (
    OrgDetails,
    ProfileExtras,
    fill_linkedin,
    fill_mastodon,
    fill_x,
    hashtag_records,
    organization_details,
    writing_from_feeds,
    x_posts,
)
from universe_kb.publication import publish_directory
from universe_kb.render import Renderer
from universe_kb.search import write_search
from universe_kb.sensitive import city_level, is_sensitive
from universe_kb.sensitive import redact as redact_sensitive
from universe_kb.site_content import build_pages
from universe_kb.web import classify_social_url

log = logging.getLogger(__name__)

@dataclass(frozen=True)
class Catalog:
    """One edition's session catalog: where its raw files are and how its IDs are named."""

    edition: str
    year: str
    prefix: str
    current: bool

    @property
    def event_id(self) -> str:
        return f"event:github-universe-{self.year}"

    @property
    def session_url(self) -> str:
        portal = f"{PORTAL_URL}/flow/github/{self.edition}/attendee-portal/page"
        return f"{portal}/sessioncatalog/session/"

    @property
    def namespace(self) -> str:
        """Past editions' session IDs are namespaced by year: `session:2025/brk123`."""
        return "" if self.current else f"{self.year}/"

    @property
    def facet_suffix(self) -> str:
        """Each edition has its own taxonomy, because tracks and topics change by year."""
        return "" if self.current else f"-{self.year}"


CURRENT = Catalog(EDITION, f"20{EDITION[-2:]}", "rainfocus", True)
PAST_CATALOGS = [Catalog(e, f"20{e[-2:]}", f"editions/{e}", False) for e in PAST_EDITIONS]
EVENT_ID = CURRENT.event_id
LOCAL_TZ = ZoneInfo(TIMEZONE)
SESSION_URL = f"{PORTAL_URL}/flow/github/{EDITION}/attendee-portal/page/sessioncatalog/session/"
TOP_REPOSITORY_MIN_STARS = 10
TOP_REPOSITORIES_PER_ACCOUNT = 3
# Repository counts read directly by `universe-kb refresh-repos`.
REPO_STATS = "github/repo-stats.json"
NON_WEBSITE_HOSTS = {"github.com", "hubs.ly", "bit.ly", "cvent.me"}

# Catalog attribute name -> (facet id, session facet field, multi-valued).
FACETS = {
    "Session type": ("session-type", "session_type", False),
    "Track": ("track", "tracks", True),
    "Level": ("level", "level", False),
    "Topic": ("topic", "topics", True),
    "GitHub product": ("github-product", "products", True),
    "Target audience": ("audience", "audiences", True),
    "Industry": ("industry", "industries", True),
    "Delivery format": ("delivery-format", "delivery_formats", True),
    "Curated agenda": ("curated-agenda", "curated_agendas", True),
}
POPULAR_PREFIX = "This is a popular session"
# Some sessions carry their track only in this single-valued twin of "Track".
TRACK_FALLBACK = "Session TrackNot Multi"
RECENT_WRITING = 15
# Sources that describe someone's present employer authoritatively; a GitHub company field
# that disagrees with them is probably out of date.
CURRENT_BASES = {"event_listing", "linkedin", "curated"}
AFFILIATION_ORDER = {"event_listing": 0, "curated": 1, "github_profile": 2, "linkedin": 3,
                     "self_reported": 4}
# Catalog export sentinels are not usable seat counts.
UNKNOWN_CATALOG_CAPACITIES = {0, 9999}
MAX_CATALOG_CAPACITY = 100_000
# A weekday-only catalog's sparse fringe days are outside the main-program span.
MAIN_PROGRAM_DENSITY_FRACTION = 0.25
SPEAKER_ROLES = {"speaker": "speaker", "moderator": "moderator", "panelist": "panelist",
                 "facilitator": "facilitator"}
# "Hosted by X" at the start of a line or after a dash or sentence end. A lowercase
# "hosted by" mid-sentence usually names a person ("hosted by Master Blender …"), so it
# only counts in the explicit "co-hosted by" or "co-sponsored by" form.
HOST_PATTERN = re.compile(r"(?:^|[-–—.!:]\s+)(?:Hosted|Sponsored|Presented) by\s+([^.!\n]+)",
                          re.MULTILINE)
CO_HOST_PATTERN = re.compile(r"\bco-(?:hosted|sponsored) by\s+([^!\n]+?)(?:[.!]\s|[.!]?$)",
                             re.IGNORECASE | re.MULTILINE)
URL_PATTERN = re.compile(r"https?://[^\s<>\"')\]]+")
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
REGISTRATION_TEXT = re.compile(r"regist|rsvp|sign ?up|ticket|reserve|save your spot", re.I)
REGISTRATION_HOSTS = {"luma.com", "lu.ma", "eventbrite.com", "goldcast.io", "cvent.me",
                      "cvent.com", "meetup.com"}
# Company strings on GitHub profiles that are not employers.
NOT_AN_EMPLOYER = {"self", "self-employed", "freelance", "freelancer", "n/a", "-", "none",
                   "independent", "student", "retired", "me", "home"}


@dataclass
class RawData:
    root: Path
    manifest: dict[str, dict[str, Any]]

    def load(self, rel_path: str) -> Any:
        return json.loads((self.root / rel_path).read_text())

    def text(self, rel_path: str) -> str:
        return (self.root / rel_path).read_text()

    def has(self, rel_path: str) -> bool:
        return (self.root / rel_path).exists()

    def source(self, rel_path: str, record_id: str | None = None,
               url: str | None = None) -> Source:
        entry = self.manifest[rel_path]
        systems = {"site/": "githubuniverse.com", "rainfocus/": "rainfocus", "github/": "github",
                   "registries/npm": "npm", "registries/pypi": "pypi", "bluesky/": "bluesky",
                   "websites/": "website",
                   "mastodon/": "mastodon", "feeds/": "feed", "brightdata/": "brightdata",
                   "editions/": "rainfocus", "packages/": "github"}
        system = next(v for k, v in systems.items() if rel_path.startswith(k))
        link = url or entry["url"]
        return Source(system=system,  # pyright: ignore[reportArgumentType]
                      url=link if link.startswith(("http://", "https://")) else None,
                      record_id=record_id, retrieved_at=entry["retrieved_at"],
                      snapshot=f"raw/{rel_path}")


def curation_source(name: str) -> Source:
    return Source(system="curation", snapshot=f"curation/{name}")


def clean_url(url: str | None) -> str | None:
    """Trim whitespace and tracking parameters from a link."""
    if not url or not url.strip():
        return None
    url = url.strip().rstrip(".,;")
    if "://" not in url:
        url = f"https://{url}"
    parts = urlparse(url)
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_")])
    return urlunparse(parts._replace(query=query))


def website_of(url: str | None) -> str | None:
    cleaned = clean_url(url)
    if not cleaned:
        return None
    host = urlparse(cleaned).hostname or ""
    if host.removeprefix("www.") in NON_WEBSITE_HOSTS:
        return None
    return f"https://{host}"


def local_iso(utc_text: str) -> str:
    moment = datetime.strptime(utc_text, "%Y/%m/%d %H:%M:%S").replace(tzinfo=ZoneInfo("UTC"))
    return moment.astimezone(LOCAL_TZ).isoformat()


def name_tokens(text: str | None) -> set[str]:
    return set(re.findall(r"[a-z]{2,}", slugify(text or "").replace("-", " ")))


# --- Organizations ---------------------------------------------------------------------


@dataclass
class OrgRecord:
    key: str
    name: str
    aliases: set[str] = field(default_factory=set)
    roles: set[str] = field(default_factory=set)
    website: str | None = None
    github_login: str | None = None
    linkedin: str | None = None
    sponsorship: Sponsorship | None = None
    related: set[str] = field(default_factory=set)
    people: set[str] = field(default_factory=set)
    hosted_sessions: set[str] = field(default_factory=set)
    mentioned_in: set[str] = field(default_factory=set)
    sources: list[Source] = field(default_factory=list)

    @property
    def id(self) -> str:
        return f"org:{self.key}"


class OrgIndex:
    """Resolves organization names from every source to one record per organization."""

    def __init__(self, curation: dict[str, Any], mentioned: dict[str, Any]) -> None:
        self.curated: dict[str, dict[str, Any]] = {
            key: {**mentioned.get(key, {}), **curation["organizations"].get(key, {})}
            for key in mentioned.keys() | curation["organizations"].keys()}
        self.mention_only = set(mentioned) - curation["organizations"].keys()
        self.alias_to_key: dict[str, str] = {}
        for key in [*sorted(self.mention_only), *sorted(curation["organizations"])]:
            entry = self.curated[key]
            for alias in [key, entry["name"], *entry.get("aliases", [])]:
                self.alias_to_key[org_key(alias)] = key
        self.ambiguous_mentions = set(curation.get("ambiguous_mentions", []))
        self.none = {n.strip().lower() for n in curation.get("none", [])} | NOT_AN_EMPLOYER
        self.split: dict[str, list[str]] = curation.get("split", {})
        self.session_hosts: dict[str, list[str]] = curation.get("session_hosts", {})
        self.records: dict[str, OrgRecord] = {}

    def by_github_login(self, login: str) -> OrgRecord | None:
        return next((r for r in self.records.values()
                     if r.github_login and r.github_login.lower() == login.lower()), None)

    def key_for(self, name: str) -> str:
        key = org_key(name)
        return self.alias_to_key.get(key, key)

    def names_for_label(self, label: str | None) -> list[str]:
        if label is None or label.strip().lower() in self.none:
            return []
        return self.split.get(label.strip(), [label.strip()])

    def ensure(self, name: str, role: str, source: Source) -> OrgRecord:
        key = self.key_for(name)
        record = self.records.get(key)
        if record is None:
            curated = self.curated.get(key, {})
            record = OrgRecord(
                key=key,
                name=curated.get("name") or normalize_org_name(name),
                website=curated.get("website"),
                github_login=curated.get("github"),
                linkedin=curated.get("linkedin"),
                related={f"org:{k}" for k in curated.get("related", [])},
            )
            if curated:
                record.sources.append(curation_source(
                    "software.yaml" if key in self.mention_only else "organizations.yaml"))
            self.records[key] = record
        if normalize_org_name(name).lower() != record.name.lower():
            record.aliases.add(name.strip())
        record.roles.add(role)
        if source not in record.sources:
            record.sources.append(source)
        return record

    def get(self, name: str) -> OrgRecord | None:
        return self.records.get(self.key_for(name))


# --- Mentions --------------------------------------------------------------------------


class Gazetteer:
    """Case-sensitive, whole-word, longest-first matching of known names in text."""

    def __init__(self, names: dict[str, str], ignore: list[str] | None = None) -> None:
        # Ignored phrases ("Salesforce Park") take part in longest-first matching so they
        # consume the span, then produce no mention.
        self.targets: dict[str, str | None] = {**names, **dict.fromkeys(ignore or [])}
        alternatives = "|".join(re.escape(n) for n in sorted(self.targets, key=len,
                                                              reverse=True))
        # A name joined to a capitalized word is a coinage ("Git-Together"), not a mention;
        # a lowercase suffix ("MCP-powered", "Azure-ready") still mentions the name.
        self.pattern = re.compile(rf"(?<![\w.#+@/-])({alternatives})(?![\w#+@]|\.\w|-[A-Z])")

    def find(self, text: str) -> list[tuple[str, str]]:
        found = []
        for match in self.pattern.finditer(text):
            target = self.targets[match.group(1)]
            if target:
                if (target.startswith("org:") and match.group(1) == "Principal" and re.match(
                        r"\s+(?:Software\s+)?(?:Engineers?|Architects?|Researchers?|Developers?)\b",
                        text[match.end():], re.IGNORECASE)):
                    continue
                found.append((match.group(1), target))
        return found


def mentions_in(gazetteer: Gazetteer, field_name: str, text: str | None,
                exclude: set[str]) -> list[Mention]:
    found: dict[str, Mention] = {}
    for surface, target in gazetteer.find(text or ""):
        if target in exclude or target in found:
            continue
        found[target] = Mention(target=target, text=surface, field=field_name,  # pyright: ignore[reportArgumentType]
                                method="gazetteer")
    return list(found.values())


# --- Build -----------------------------------------------------------------------------


@dataclass
class Built:
    models: dict[str, tuple[str, BaseModel, str | None]] = field(default_factory=dict)

    def add(self, rel_path: str, envelope: str, model: BaseModel,
            title: str | None = None) -> None:
        if rel_path in self.models:
            raise ValueError(f"two entities map to {rel_path}")
        self.models[rel_path] = (envelope, model, title)


def sync_website_backlinks(built: Built, registry: AccountRegistry) -> None:
    """Refresh both owner views after the registry's final ownership decisions."""
    for _, model, _ in built.models.values():
        if isinstance(model, (Person, Organization)):
            model.websites = registry.owned_by(model.id)[1]


def build(raw_dir: Path, curation_dir: Path, kb_dir: Path, schema_dir: Path) -> dict[str, Any]:
    raw = RawData(raw_dir, json.loads((raw_dir / "manifest.json").read_text())["files"])
    org_curation = yaml.safe_load((curation_dir / "organizations.yaml").read_text())
    software_curation = yaml.safe_load((curation_dir / "software.yaml").read_text())
    venue_curation = yaml.safe_load((curation_dir / "venues.yaml").read_text())
    people_curation = yaml.safe_load((curation_dir / "people.yaml").read_text()) or {}
    renames = people_curation.get("names") or {}
    rejected_sources = set(people_curation.get("rejected_sources_sha256") or [])

    mentioned_orgs = software_curation.get("mentioned_organizations", {})
    orgs = OrgIndex(org_curation, mentioned_orgs)
    organizer = orgs.ensure(org_curation["organizer"], "organizer",
                            curation_source("organizations.yaml"))

    items = catalog_items(raw, CURRENT)
    filter_catalog_people(items, f"{CURRENT.prefix}/sessions.json", rejected_sources)
    owners: dict[str, Any] = raw.load("github/owners.json") if raw.has("github/owners.json") else {}
    built = Built()

    canonicalize_attributes(raw, CURRENT, items)
    normalize_names(items, renames)
    facets, term_by_label = build_facets(raw, items)
    venues = build_venues(venue_curation)
    rooms = build_rooms(raw, items, venues, venue_curation)

    # Sponsors first, so speaker affiliations and hosts resolve to the same records.
    sponsor_matches = (raw.load("github/sponsor-orgs.json")
                       if raw.has("github/sponsor-orgs.json") else {})
    for item in exhibitors(raw):
        record = orgs.ensure(item["name"].strip(), "sponsor",
                             raw.source("rainfocus/exhibitors.json", item["exhibitorID"]))
        tier = next(a["value"] for a in item["attributevalues"]
                    if a["attribute"] == "Exhibitor Type")
        logo = next((f["url"] for f in item.get("files") or []
                     if f.get("fileCode") == "catalog_tile_image"), None)
        record.sponsorship = Sponsorship(
            tier=tier.lower(),  # pyright: ignore[reportArgumentType]
            summary=html_to_markdown(item.get("description") or "") or None,
            link=clean_url(item.get("externalLink")),
            logo_url=logo,
            industries=sorted({a["value"] for a in item["attributevalues"]
                               if a["attribute"] == "Industry?"}),
            booth=next((b["booth"] for b in item.get("booths") or [] if b.get("booth")), None),
            exhibitor_id=item["exhibitorID"],
        )
        record.website = record.website or website_of(item.get("externalLink"))
        match = sponsor_matches.get(item["name"].strip(), {})
        if not record.github_login and match.get("accepted"):
            record.github_login = match["accepted"]
            record.sources.append(raw.source("github/sponsor-orgs.json", match["accepted"]))

    # People, keyed by RainFocus user, in catalog order.
    raw_people: dict[str, dict[str, Any]] = {}
    for item in items:
        for participant in item.get("participants") or []:
            raw_people.setdefault(participant["userRef"], participant)
    person_ids = assign_ids({ref: person_name(p) for ref, p in raw_people.items()}, "person")

    # Sessions: the catalog repeats a session once per time slot.
    by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_session[item["sessionID"]].append(item)
    session_ids = assign_ids({sid: rows[0]["code"] for sid, rows in by_session.items()},
                             "session")

    software_entries = {f"software:{s['id']}": s for s in software_curation["software"]}
    ambiguous = set(software_curation.get("ambiguous_org_names", [])) | orgs.ambiguous_mentions

    people_sessions: dict[str, list[PersonSession]] = defaultdict(list)
    sessions: list[Session] = []
    day_ids: set[str] = set()
    for rows in by_session.values():
        session = build_session(raw, rows, session_ids, person_ids, term_by_label, rooms, orgs)
        sessions.append(session)
        day_ids.update(slot.day for slot in session.slots)
        for speaker in session.speakers:
            people_sessions[speaker.person].append(
                PersonSession(session=session.id, role=speaker.role))
        for host in session.hosts:
            orgs.records[host.removeprefix("org:")].hosted_sessions.add(session.id)

    for room in rooms.values():
        room.sessions.sort()

    # Speakers first: the official catalog is the strongest identity source.
    registry = AccountRegistry(
        rejected={(f"person:{r['person']}", r["link"])
                  for r in people_curation.get("rejected_links") or []},
        rejected_hashes=set(people_curation.get("rejected_links_sha256") or []))
    index = PeopleIndex()
    people: dict[str, Person] = {}
    session_urls = {s.id: s.url for s in sessions}
    for user_ref, participant in raw_people.items():
        person = build_person(raw, participant, person_ids[user_ref], orgs, owners, registry)
        person.sessions = sorted(people_sessions[person.id], key=lambda s: s.session)
        person.participations[0].evidence = [Evidence(url=session_urls[s.session], ref=s.session)
                                             for s in person.sessions]
        people[person.id] = person
        index.register(person.id, person.name, person_keys(person, registry)
                       | listing_keys(participant))

    # Then people from curation, each with a public source for their part.
    for record in curated_people(curation_dir):
        add_imported_person(raw, record, people, index, registry, orgs, owners)

    # Past editions: their sessions, taxonomies and speakers, merged into the people above.
    past_events: list[Event] = []
    for catalog in PAST_CATALOGS:
        if not raw.has(f"{catalog.prefix}/sessions.json"):
            continue
        edition = add_edition(raw, catalog, people, index, registry, orgs, owners, rooms,
                              venues, venue_curation, renames, rejected_sources)
        facets += edition.facets
        sessions += edition.sessions
        past_events.append(edition.event)
    for person in people.values():
        person.sessions.sort(key=lambda s: s.session)

    # Organization names for mentions, before GitHub company fields add looser names.
    org_names = {}
    for record in orgs.records.values():
        for name in [record.name, *record.aliases]:
            if name not in ambiguous and len(name) >= 3 and record.key != organizer.key:
                org_names[name] = record.id
    for key, entry in mentioned_orgs.items():
        for name in [entry["name"], *entry.get("aliases", [])]:
            org_names.setdefault(name, f"org:{key}")

    discover_github_claims(raw, people, owners, registry, orgs)
    link_github_profiles(raw, people, owners, registry, orgs)
    link_websites(raw, registry, people, orgs, finalize_ownership=False)
    fill_bluesky(raw, registry)
    fill_mastodon(raw, registry)
    fill_x(raw, registry, people)
    linkedin_extras = fill_linkedin(raw, registry, people, orgs)
    # Fill websites linked by X, LinkedIn and Mastodon before profile assembly.
    link_websites(raw, registry, people, orgs, finalize_ownership=False)
    adopted = adopt_github_claims(raw, people, owners, registry, orgs)
    link_github_profiles(raw, adopted, owners, registry, orgs, organizations=False)
    # Validate company profiles before website ownership and writing are finalized.
    org_details = organization_details(raw, orgs.records, owners, registry)
    for organization in orgs.records.values():
        details = org_details.get(organization.id)
        if details and details.website and not organization.website:
            organization.website = details.website
            organization.sources.extend(s for s in details.sources if s not in organization.sources)
    # Reconsider ownership even for homepages fetched by an earlier pass.
    link_websites(raw, registry, people, orgs)
    writing = writing_from_feeds(raw, registry)
    x_writing, x_universe_posts = x_posts(raw, registry)
    for person in people.values():
        settle_affiliation_currency(person)
        universe_posts = x_universe_posts.get(person.id, [])
        if universe_posts:
            current = next((p for p in person.participations if p.event == EVENT_ID), None)
            # A past speaker attends this year only if a post says so; mentioning
            # Universe is not attending.
            attending = [e for e in universe_posts if says_attending(e.quote)]
            if current is None and attending:
                person.participations.append(Participation(
                    event=EVENT_ID, role="attendee", status="self_reported",
                    evidence=attending))
            elif current is not None:
                current.evidence.extend(universe_posts)
        # Accounts linked since the first registration can now match new records.
        index.register(person.id, person.name, person_keys(person, registry))
    for record in hashtag_records(raw):
        add_imported_person(raw, record, people, index, registry, orgs, owners)
    remove_people(Exclusions.load(curation_dir), people, sessions, registry)
    for platform, ids in sorted(registry.excluded.items()):
        log.info("left out %s %s accounts: personal by default", len(ids), platform)
    for person in people.values():
        accounts, websites = registry.owned_by(person.id)
        person.accounts = ([person.github] if person.github else []) + accounts
        person.websites = websites
        person.affiliations.sort(key=lambda a: (not a.current, AFFILIATION_ORDER[a.basis]))
        for affiliation in person.affiliations:
            if affiliation.current:
                orgs.records[affiliation.organization.removeprefix("org:")].people.add(person.id)

    software_names = {alias: ref for ref, entry in software_entries.items()
                      for alias in entry.get("aliases", [])}
    gazetteer = Gazetteer({**org_names, **software_names},
                          ignore=software_curation.get("ignore_phrases", []))

    mentioned_in: dict[str, set[str]] = defaultdict(set)
    for session in sessions:
        exclude = set(session.hosts)
        session.mentions = dedupe_mentions(
            mentions_in(gazetteer, "title", session.title, exclude)
            + mentions_in(gazetteer, "abstract", session.abstract, exclude))
        for mention in session.mentions:
            mentioned_in[mention.target].add(session.id)
    for person in people.values():
        own = {a.organization for a in person.affiliations}
        person.mentions = mentions_in(gazetteer, "bio", person.bio, own)
        for mention in person.mentions:
            mentioned_in[mention.target].add(person.id)
    for target, subjects in mentioned_in.items():
        if target.startswith("org:"):
            key = target.removeprefix("org:")
            record = orgs.records.get(key) or orgs.ensure(
                mentioned_orgs[key]["name"], "mentioned", curation_source("software.yaml"))
            record.roles.add("mentioned")
            record.mentioned_in.update(subjects)

    featured = build_featured(raw, list(people.values()))

    # GitHub, software and packages.
    accounts, repositories = build_github(raw, owners, list(people.values()), orgs, registry)
    for account in accounts.values():
        linked, sites = registry.owned_by(account.entity or "")
        account.linked_accounts = [a for a in linked if "github_profile"
                                   in registry.accounts[a].account.link_basis]
        account.websites = [w for w in sites if "github_profile"
                            in registry.websites[w].website.link_basis]
    software, packages = build_software(raw, software_entries, mentioned_in, orgs,
                                        repositories, term_by_label, set(accounts))
    for repo in repositories.values():
        if repo.software is None:
            repo.software = next((s.id for s in software if repo.id in s.repositories), None)
    log.info("fresh counts for %s of %s repositories", apply_repo_stats(raw, repositories),
             len(repositories))

    published = repository_packages(raw, repositories, accounts, packages)

    # Profiles last: they draw on everything above.
    term_labels = {t.id: t.label for f in facets for t in f.terms}
    software_labels = {s.id: s.name for s in software}
    product_software = {s.product_term: s.id for s in software if s.product_term}
    org_labels = {r.id: r.name for r in orgs.records.values()}
    bluesky_profiles = raw.load("bluesky/profiles.json") if raw.has("bluesky/profiles.json") else {}
    session_by_id = {s.id: s for s in sessions}
    profiles = []
    for person in people.values():
        node = owners.get(person.github.removeprefix("gh:")) if person.github else None
        handle = next((registry.accounts[a].account.handle for a in person.accounts
                       if a.startswith("acct:bluesky/")), None)
        profile_sources = list(person.sources)
        profile = build_profile(
            person, session_by_id, term_labels, software_labels, product_software, node,
            repositories, bluesky_profiles.get(handle) if handle else None,
            org_labels, profile_sources,
            detailed=frozenset(registry.accounts[a].account.platform for a in person.accounts
                               if a in registry.accounts
                               and registry.accounts[a].account.details_fetched))
        extras = linkedin_extras.get(person.id) or ProfileExtras()
        profile.experience = extras.experience
        profile.education = extras.education
        profile.credentials = extras.credentials
        profile.publications = extras.publications
        profile.patents = extras.patents
        profile.spoken_languages = extras.spoken_languages
        profile.activities = extras.activities
        items = [*writing.get(person.id, []), *extras.writing, *x_writing.get(person.id, [])]
        items.sort(key=lambda w: w.published or "", reverse=True)
        profile.recent_writing = items[:RECENT_WRITING]
        profile.packages = sorted(published.get(person.id, set()))
        profile.recognitions += program_recognitions(node, profile.recognitions)
        inferred = infer_interests(interest_signals(profile, session_by_id, term_labels,
                                                    repositories))
        stated = {interest_key(c.label) for c in profile.interests}
        profile.interests += [c for c in inferred if interest_key(c.label) not in stated]
        person.profile = profile.id
        profiles.append(profile)

    for facet in facets:
        built.add(f"taxonomy/{facet.id}.yaml", "facet", facet)
    for venue in venues.values():
        built.add(path_for(venue.id), "venue", venue)
    for room in rooms.values():
        built.add(path_for(room.id), "room", room)
    for session in sessions:
        built.add(path_for(session.id), "session", session, session.title)
    for person in people.values():
        person.featured = person.id in featured
        built.add(path_for(person.id), "person", person, person.name)
    for profile in profiles:
        built.add(path_for(profile.id), "profile", profile)
    # Mention-only organizations added since enrichment have no linked company accounts.
    remaining_orgs = {key: r for key, r in orgs.records.items() if r.id not in org_details}
    if remaining_orgs:
        org_details.update(organization_details(raw, remaining_orgs, owners, AccountRegistry()))
    for record in orgs.records.values():
        github = (account_id(record.github_login)
                  if record.github_login and owners.get(record.github_login.lower()) else None)
        org_accounts, _ = registry.owned_by(record.id)
        details = org_details.get(record.id) or OrgDetails()
        sponsor_logo = record.sponsorship.logo_url if record.sponsorship else None
        org = Organization(
            id=record.id, name=record.name, aliases=sorted(record.aliases),
            roles=sorted(record.roles),  # pyright: ignore[reportArgumentType]
            description=details.descriptions[0].text if details.descriptions else None,
            descriptions=details.descriptions, tagline=details.tagline,
            industry=details.industry, size=details.size, headquarters=details.headquarters,
            founded=details.founded, specialties=details.specialties,
            logo_url=details.logo_url or sponsor_logo,
            website=record.website or details.website, github=github,
            accounts=([github] if github else []) + org_accounts,
            related_organizations=sorted(
                {r for r in record.related if r.removeprefix("org:") in orgs.records}
                | {p.organization for p in details.affiliated if p.organization}),
            affiliated=details.affiliated, locations=details.locations,
            updates=details.updates,
            sponsorship=record.sponsorship, people=sorted(record.people),
            hosted_sessions=sorted(record.hosted_sessions),
            mentioned_in=sorted(record.mentioned_in),
            sources=[*record.sources, *(s for s in details.sources if s not in record.sources)],
        )
        built.add(path_for(org.id), "organization", org, org.name)
    for account in accounts.values():
        built.add(path_for(account.id), "github_account", account)
    for record in registry.accounts.values():
        built.add(path_for(record.account.id), "social_account", record.account)
    for record in registry.websites.values():
        built.add(path_for(record.website.id), "website", record.website)
    for repo in repositories.values():
        built.add(path_for(repo.id), "repository", repo)
    for package in packages:
        built.add(path_for(package.id), "package", package)
    for entry in software:
        built.add(path_for(entry.id), "software", entry)
    for experience in build_experiences(raw, venues):
        built.add(path_for(experience.id), "experience", experience)

    event = build_event(raw, organizer, day_ids,
                        [p.id for p in people.values() if p.id in featured])
    built.add(path_for(event.id), "event", event, event.name)
    for past in past_events:
        built.add(path_for(past.id), "event", past, past.name)
    built.add("faq.yaml", "faq", Faq(
        event=EVENT_ID,
        entries=pages.faq_entries(raw.load("rainfocus/pages/universe-faq.json")),  # pyright: ignore[reportArgumentType]
        sources=[raw.source("rainfocus/pages/universe-faq.json")],
    ))

    for page in build_pages(raw_dir, raw.manifest):
        built.add(path_for(page.id), "page", page, page.title)
    sync_website_backlinks(built, registry)
    built.add("media.yaml", "media", media_index(built, raw))
    # Redact first: bios are written from the redacted kb, so their evidence hashes must
    # be computed from the same text.
    redact_contacts(built)
    redact_sensitive_text(built)
    attach_bios(built, curation_dir.parent / "synthesis" / "brief-bios.yaml")

    # Fields were mutated after construction (backlinks, mentions); re-check each model.
    for _, model, _ in built.models.values():
        type(model).model_validate(model.model_dump())

    stats = write_kb(built, kb_dir, schema_dir)
    if registry.rejected_hashes:
        stats["rejected_links_sha256"] = sorted(registry.rejected_hashes)
    return stats


IMAGE_FIELDS = {"photo_url": "photo", "avatar_url": "avatar", "banner_url": "banner",
                "logo_url": "logo", "image_url": "tile", "thumbnail_url": "thumbnail"}


def media_index(built: Built, raw: RawData) -> MediaIndex:
    """
    Every image URL in the knowledge base with the entities that show it, so a site can
    mirror or proxy images in one pass.
    """
    users: dict[str, set[str]] = defaultdict(set)
    kinds: dict[str, str] = {}
    alts: dict[str, str] = {}

    def visit(value: Any, owner: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in IMAGE_FIELDS and isinstance(item, str) and item.startswith("http"):
                    users[item].add(owner)
                    kinds.setdefault(item, IMAGE_FIELDS[key])
                elif key == "images" and isinstance(item, list):
                    for image in item:
                        if isinstance(image, dict) and str(image.get("url", "")).startswith("http"):
                            users[image["url"]].add(owner)
                            kinds.setdefault(image["url"], "illustration")
                            if image.get("alt"):
                                alts.setdefault(image["url"], image["alt"])
                else:
                    visit(item, owner)
        elif isinstance(value, list):
            for item in value:
                visit(item, owner)

    for rel_path, (_, model, _) in built.models.items():
        visit(payload(model), getattr(model, "id", None) or rel_path)
    items = [MediaItem(url=url, kind=kinds[url],  # pyright: ignore[reportArgumentType]
                       alt=alts.get(url), used_by=sorted(owners))
             for url, owners in sorted(users.items())]
    return MediaIndex(event=EVENT_ID, items=items,
                      sources=[raw.source("rainfocus/sessions.json"),
                               raw.source("site/home.html")])


def bundles_from(payloads: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Each person's bio evidence bundle, from entity payloads keyed by ID."""
    bundles = {}
    for entity_id, person in payloads.items():
        if entity_id.startswith("person:"):
            profile = payloads.get(person.get("profile") or "")
            bundles[entity_id] = person_bundle(person, profile, payloads)
    return bundles


PERSON_ENVELOPES = {"person", "profile", "github_account", "social_account", "website"}


def redact_contacts(built: Built) -> None:
    """Remove email addresses and phone numbers from the free text of every artifact."""
    for rel_path, (envelope, model, title) in list(built.models.items()):
        payload = model.model_dump(mode="json", exclude_none=True)
        cleaned = redact_payload(payload)
        if cleaned != payload:
            built.models[rel_path] = (envelope, type(model).model_validate(cleaned), title)


# Text people wrote about themselves and published, by envelope. It stays verbatim
# unless `REDACT_SELF_STATED` is set. Publications, patents and other professional work
# are left as listed: their topics are not attributes of anyone.
SELF_DESCRIBED = {
    "person": {"bio"},
    "social_account": {"bio", "headline", "display_name"},
    "github_account": {"bio", "profile_readme", "name"},
    "website": {"title", "description"},
}
# Lists of items the build selects or derives for a profile; an item whose words state a
# sensitive attribute is dropped, whatever its source.
DERIVED_LISTS = {"recent_writing": ("title", "summary"), "activities": ("title", "detail"),
                 "credentials": ("title", "issuer", "description"),
                 "interests": ("label",), "expertise": ("label",), "recognitions": ("label",)}


def _derived_quotes(value: Any) -> Any:
    """Evidence quotes the build picked, without clauses that state a sensitive attribute."""
    if isinstance(value, dict):
        return {k: (redact_sensitive(v) if k == "quote" and isinstance(v, str)
                    else _derived_quotes(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_derived_quotes(v) for v in value]
    return value


def redact_sensitive_text(built: Built) -> None:
    """
    Keep what the build derives about people free of sensitive attributes: profile
    headlines, selected posts, activities, credentials, inferred labels and evidence
    quotes. Locations are kept at city level. Text people wrote about themselves stays
    verbatim unless `REDACT_SELF_STATED` is set; the raw sanitizer already applied the
    same rules, so this keeps a curated or derived field from slipping through.
    """
    for rel_path, (envelope, model, title) in list(built.models.items()):
        owner = str(getattr(model, "owner", None) or getattr(model, "entity", None) or "")
        if envelope not in {"person", "profile"} and not (
                envelope in SELF_DESCRIBED and owner.startswith("person:")):
            continue
        payload = model.model_dump(mode="json", exclude_none=True)
        cleaned = _derived_quotes(payload)
        if REDACT_SELF_STATED:
            cleaned |= {k: redact_sensitive(v) for k, v in cleaned.items()
                        if k in SELF_DESCRIBED.get(envelope, ()) and isinstance(v, str)}
        if envelope == "profile":
            if isinstance(cleaned.get("headline"), str):
                cleaned["headline"] = redact_sensitive(cleaned["headline"])
            for key, fields in DERIVED_LISTS.items():
                cleaned[key] = [item for item in cleaned.get(key) or [] if not any(
                    is_sensitive(item.get(f)) for f in fields)]
        if isinstance(cleaned.get("location"), str):
            cleaned["location"] = city_level(cleaned["location"])
        cleaned = {k: v for k, v in cleaned.items() if v is not None}
        if cleaned != payload:
            built.models[rel_path] = (envelope, type(model).model_validate(cleaned), title)


def remove_people(exclusions: Exclusions, people: dict[str, Person], sessions: list[Session],
                  registry: AccountRegistry) -> list[str]:
    """
    Leave out people who asked to be removed, with the sessions' references to them and
    the accounts and websites they own. Returns the IDs removed.
    """
    removed = sorted(pid for pid, person in people.items()
                     if exclusions.covers(pid, person_keys(person, registry)
                                          | ({person.github} if person.github else set())))
    for pid in removed:
        del people[pid]
    if removed:
        log.info("excluded %d person records by curation", len(removed))
    gone = set(removed)
    for session in sessions:
        session.speakers = [s for s in session.speakers if s.person not in gone]
    registry.accounts = {k: r for k, r in registry.accounts.items() if r.owner not in gone}
    registry.websites = {k: r for k, r in registry.websites.items() if r.owner not in gone}
    return removed


def attach_bios(built: Built, bios_path: Path) -> None:
    """Attach written bios to profiles, marking each stale if its evidence has changed."""
    written = load_bios(bios_path)
    payloads: dict[str, dict[str, Any]] = {}
    for _, model, _ in built.models.values():
        entity_id = getattr(model, "id", None)
        if isinstance(entity_id, str):
            payloads[entity_id] = payload(model)
    for person_id, bundle in bundles_from(payloads).items():
        entry = written.get(person_id)
        profile_id = person_id.replace("person:", "profile:", 1)
        profile = next((m for _, m, _ in built.models.values()
                        if isinstance(m, Profile) and m.id == profile_id), None)
        if entry is None or profile is None:
            continue
        if check_bio(entry["text"], bundle, entry["cites"]):
            log.warning("omitted a stored bio that failed evidence validation")
            continue
        profile.brief_bio = BriefBio(
            text=entry["text"], cites=entry["cites"], written_by=entry["written_by"],
            written_at=entry["written_at"], input_sha256=entry["input_sha256"],
            stale=entry["input_sha256"] != bundle_hash(bundle))


def write_kb(built: Built, kb_dir: Path, schema_dir: Path) -> dict[str, Any]:
    """
    Write the knowledge base into a `.kb-*` staging directory beside `kb_dir` and swap it
    into place, so a failed build never leaves a half-written `kb_dir`.
    """
    kb_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".kb-", dir=kb_dir.parent))
    try:
        entities: dict[str, BaseModel] = {}
        for _, model, _ in built.models.values():
            entity_id = getattr(model, "id", None)
            if isinstance(model, Facet):
                # Facets carry the term labels the renderer shows in session bodies.
                entities[f"facet:{model.id}"] = model
            elif isinstance(entity_id, str) and ":" in entity_id:
                entities[entity_id] = model
        renderer = Renderer(entities)
        # Ship the compiled schemas inside the knowledge base so its relative schema
        # pointers resolve wherever the directory is copied.
        published_schemas = staging / "_schemas"
        published_schemas.mkdir()
        for schema in sorted(schema_dir.glob("*.schema.yaml")):
            shutil.copy2(schema, published_schemas / schema.name)
        for rel_path, (envelope, model, title) in built.models.items():
            body = renderer.body(envelope, model, rel_path) if rel_path.endswith(".md") else None
            write_artifact(staging, published_schemas, model, envelope=envelope,
                           rel_path=rel_path, title=title, body=body)
        stats = write_graph(staging, built.models)
        write_search(staging, built.models)
        renderer.write_index(staging, stats)
        publish_directory(staging, kb_dir)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return stats


def assign_ids(names: dict[str, str], prefix: str, namespace: str = "") -> dict[str, str]:
    """
    Slug IDs in input order; a taken slug gets the first free `-2`, `-3`, … suffix, so a
    name whose own slug looks like a suffix ("Jane Doe 2") cannot collide.
    """
    ids: dict[str, str] = {}
    taken: set[str] = set()
    for key, name in names.items():
        slug = candidate = slugify(name)
        suffix = 1
        while candidate in taken:
            suffix += 1
            candidate = f"{slug}-{suffix}"
        taken.add(candidate)
        ids[key] = f"{prefix}:{namespace}{candidate}"
    return ids


def dedupe_mentions(mentions: list[Mention]) -> list[Mention]:
    seen: set[str] = set()
    unique = []
    for mention in mentions:
        if mention.target not in seen:
            seen.add(mention.target)
            unique.append(mention)
    return unique


def exhibitors(raw: RawData) -> list[dict[str, Any]]:
    result = raw.load("rainfocus/exhibitors.json")
    return [item for section in result.get("sectionList") or [result]
            for item in section.get("items") or []]


# --- Taxonomy --------------------------------------------------------------------------


def build_facets(raw: RawData, items: list[dict[str, Any]], catalog: Catalog = CURRENT
                 ) -> tuple[list[Facet], dict[tuple[str, str], str]]:
    attributes = raw.load(f"{catalog.prefix}/attributes.json")["attributes"]
    glossary = {slugify(e["label"]): e for e in pages.catalog_glossary(
        raw.load(f"{catalog.prefix}/pages/sessioncatalog.json"))}
    counts: Counter[tuple[str, str]] = Counter()
    for item in items_by_session(items):
        for value in {(v["attribute"], v["value"]) for v in item["attributevalues"]}:
            counts[value] += 1

    facets: list[Facet] = []
    term_by_label: dict[tuple[str, str], str] = {}
    seen: set[str] = set()
    names = {a["name"].lower() for a in attributes}
    aliases = {"session track": "Track"} if "track" not in names else {}
    for attribute in attributes:
        name = FACET_KEYS.get(attribute["name"].lower()) or aliases.get(attribute["name"].lower())
        if name is None or name in seen:
            continue
        seen.add(name)
        base_id, _, multi = FACETS[name]
        facet_id = base_id + catalog.facet_suffix
        terms = []
        for value in attribute["values"]:
            label = value["name"].strip()
            term_id = f"term:{facet_id}/{slugify(label)}"
            term_by_label[(name, label)] = term_id
            entry = glossary.get(slugify(label))
            terms.append(Term(id=term_id, label=label,
                              description=entry["description"] if entry else None,
                              duration_minutes=entry["duration_minutes"] if entry else None,
                              source_id=value.get("id"),
                              session_count=counts[(name, value["name"])]))
        facets.append(Facet(id=facet_id, event=catalog.event_id, label=name,
                            multi_valued=multi, terms=terms,
                            sources=[raw.source(f"{catalog.prefix}/attributes.json",
                                                attribute.get("rf_attribute_id"))]))
    return facets, term_by_label


FACET_KEYS = {name.lower(): name for name in FACETS}


def canonicalize_attributes(raw: RawData, catalog: Catalog,
                            items: list[dict[str, Any]]) -> None:
    """
    Rename facet attributes in catalog rows to this edition's spelling ("Session Type" →
    "Session type"). 2023 has no "Track" attribute and calls its tracks "Session Track";
    later catalogs have both, and there "Session Track" holds combinations, not tracks.
    """
    names = {a["name"].lower() for a in raw.load(f"{catalog.prefix}/attributes.json")
             ["attributes"]}
    aliases = {"session track": "Track"} if "track" not in names else {}
    for item in items:
        for value in item["attributevalues"]:
            key = FACET_KEYS.get(value["attribute"].lower()) or aliases.get(
                value["attribute"].lower())
            if key:
                value["attribute"] = key


def items_by_session(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for item in items:
        unique.setdefault(item["sessionID"], item)
    return list(unique.values())


# --- Places ----------------------------------------------------------------------------


def build_venues(curation: dict[str, Any]) -> dict[str, Venue]:
    campus = curation["campus"]
    source = curation_source("venues.yaml")
    venues: dict[str, Venue] = {}
    for key, entry in curation["venues"].items():
        is_campus = key == campus["id"]
        venues[key] = Venue(
            id=f"venue:{key}", name=entry["name"], kind=entry["kind"],
            parent=None if is_campus else f"venue:{campus['id']}",
            address=campus["address"] if is_campus else None, sources=[source],
        )
    for key, entry in (curation.get("places") or {}).items():
        venues[key] = Venue(id=f"venue:{key}", name=entry["name"], kind=entry["kind"],
                            address=entry.get("address"), sources=[source])
    return venues


def match_place(name: str, curation: dict[str, Any]) -> tuple[str, str] | None:
    """An earlier edition's place named as a room-label prefix: (venue key, room name)."""
    for key, entry in (curation.get("places") or {}).items():
        for prefix in entry["prefixes"]:
            if name.startswith(prefix):
                return key, name[len(prefix):].strip()
    return None


def match_venue(text: str, curation: dict[str, Any]) -> str | None:
    for key, entry in curation["venues"].items():
        if any(text.strip().lower() == alias.lower() for alias in entry["aliases"]):
            return key
    return None


def split_room_label(label: str, curation: dict[str, Any]
                     ) -> tuple[str, str | None, str | None, str | None]:
    """
    Split "Room @ Place, detail" into (room name, campus venue key, location note,
    outside address). Places that match no campus alias are outside venues.
    """
    parts_at = re.split(r"\s*@\s*", label, maxsplit=1)
    name = parts_at[0].strip()
    place = parts_at[1].strip() if len(parts_at) == 2 else ""
    if not place:
        return name, match_venue(name, curation), None, None
    parts = [p.strip() for p in place.split(",")]
    for index, part in enumerate(parts):
        level = re.search(r"\s*\((Level \d+)\)$", part, re.IGNORECASE)
        base = part[:level.start()].strip() if level else part
        key = match_venue(base, curation)
        if key:
            note = ", ".join(parts[:index] + ([level[1]] if level else [])
                             + parts[index + 1:]) or None
            return name, key, note, None
    return name, None, None, place


def catalog_capacity(value: Any) -> int | None:
    """RainFocus uses 0, 9999 and very large values as unknown-capacity sentinels."""
    try:
        capacity = int(value)
    except (TypeError, ValueError):
        return None
    return (capacity if 0 <= capacity < MAX_CATALOG_CAPACITY
            and capacity not in UNKNOWN_CATALOG_CAPACITIES else None)


def build_rooms(raw: RawData, items: list[dict[str, Any]], venues: dict[str, Venue],
                curation: dict[str, Any], rooms: dict[str, Room] | None = None,
                catalog: Catalog = CURRENT) -> dict[str, Room]:
    """Rooms from a catalog's time slots; the same room label in another year is one room."""
    rooms = {} if rooms is None else rooms
    source = raw.source(f"{catalog.prefix}/sessions.json")
    for item in items:
        for time in item["times"]:
            label = time.get("room")
            if not label:
                continue
            room_id = f"room:{slugify(label)}"
            capacity = catalog_capacity(time.get("capacity"))
            room = rooms.get(room_id)
            if room is None:
                name, venue_key, note, address = split_room_label(label, curation)
                place = match_place(name, curation) if venue_key is None else None
                if place:
                    venue_key, name = place
                if venue_key is None:
                    # An outside venue: the catalog names the place as the room.
                    venue_key = slugify(name)
                    venues.setdefault(venue_key, Venue(
                        id=f"venue:{venue_key}", name=name, kind="external", address=address,
                        sources=[source]))
                room = Room(id=room_id, name=name, label=label, venue=f"venue:{venue_key}",
                            location_note=note, capacity=capacity, source_ids=[],
                            sources=[source, raw.source("rainfocus/rooms.json")])
                rooms[room_id] = room
            if time["roomId"] not in room.source_ids:
                room.source_ids.append(time["roomId"])
            if source not in room.sources:
                room.sources.append(source)
            if capacity and (room.capacity or 0) < capacity:
                room.capacity = capacity
    return rooms


# --- Sessions --------------------------------------------------------------------------


def build_session(raw: RawData, rows: list[dict[str, Any]], session_ids: dict[str, str],
                  person_ids: dict[str, str], term_by_label: dict[tuple[str, str], str],
                  rooms: dict[str, Room], orgs: OrgIndex, catalog: Catalog = CURRENT) -> Session:
    first = rows[0]
    session_id = session_ids[first["sessionID"]]
    values = [(v["attribute"], v["value"]) for v in first["attributevalues"]]
    facet_values: dict[str, list[str]] = defaultdict(list)
    for attribute, value in values:
        if attribute in FACETS:
            term = term_by_label.get((attribute, value.strip()))
            if term and term not in facet_values[FACETS[attribute][1]]:
                facet_values[FACETS[attribute][1]].append(term)
    if not facet_values.get("tracks"):
        for attribute_name, value in values:
            term = term_by_label.get(("Track", value.strip()))
            if attribute_name == TRACK_FALLBACK and term:
                facet_values["tracks"].append(term)
    session_type = facet_values.pop("session_type", [])
    level = facet_values.pop("level", [])
    facets = SessionFacets(
        session_type=session_type[0] if session_type else
        f"term:session-type{catalog.facet_suffix}/{slugify(first['type'])}",
        level=level[0] if level else None,
        **facet_values,  # pyright: ignore[reportArgumentType]
    )

    slots = []
    for row in rows:
        for time in row["times"]:
            start = local_iso(time["utcStartTime"])
            room_id = f"room:{slugify(time['room'])}" if time.get("room") else None
            if room_id and session_id not in rooms[room_id].sessions:
                rooms[room_id].sessions.append(session_id)
            capacity = catalog_capacity(time.get("capacity"))
            slots.append(TimeSlot(
                start=start, end=local_iso(time["utcEndTime"]), day=f"day:{start[:10]}",
                room=room_id, capacity=capacity,
                in_person=bool(time.get("inPersonTime", True)),
                virtual=bool(time.get("virtualTime", False)), source_id=time["sessionTimeID"],
            ))
    slots.sort(key=lambda s: s.start)

    speakers = []
    listed = [p for p in first.get("participants") or [] if p["userRef"] in person_ids]
    for order, participant in enumerate(listed):
        role = next((s["speakerRole"] for s in participant.get("session") or []
                     if s["sessionID"] == first["sessionID"]), "Speaker")
        speakers.append(SessionSpeaker(
            person=person_ids[participant["userRef"]],
            role=SPEAKER_ROLES.get(role.lower(), "speaker"),  # pyright: ignore[reportArgumentType]
            order=order))

    abstract = html_to_markdown(first.get("abstract") or "")
    source = raw.source(f"{catalog.prefix}/sessions.json", first["sessionID"],
                        url=f"{catalog.session_url}{first['sessionID']}")
    hosts = session_hosts(first, abstract, raw_people_affiliations(first), orgs, source)
    urls = [clean_url(u) for u in URL_PATTERN.findall(abstract)]
    related = []
    for url in urls:
        match = re.search(r"/session/([A-Za-z0-9]+)", url or "")
        if url and "githubuniverse.com" in url and match and match.group(1) in session_ids:
            related.append(session_ids[match.group(1)])
    registration = registration_link(abstract)
    image = next((v for a, v in values if a == "Session Tile Image"), None)

    return Session(
        id=session_id, event=catalog.event_id, code=first["code"],
        title=" ".join(first["title"].split()), abstract=abstract,
        url=f"{catalog.session_url}{first['sessionID']}", slots=slots,
        speakers=speakers, facets=facets,
        sponsored=any(a == "Sponsor Session?" and v == "Yes" for a, v in values),
        popular=any(a.startswith(POPULAR_PREFIX) for a, _ in values),
        hosts=hosts, registration_url=registration,
        related=[r for r in dict.fromkeys(related) if r != session_id],
        image_url=image, sources=[source],
    )


def raw_people_affiliations(item: dict[str, Any]) -> list[str]:
    return [event_field(p, "companyName", "globalCompany") or ""
            for p in item.get("participants") or []]


def session_hosts(item: dict[str, Any], abstract: str, affiliations: list[str],
                  orgs: OrgIndex, source: Source) -> list[str]:
    """
    Organizations that host a session: names after "Hosted by" or "Sponsored by" in the
    title or abstract, plus speakers' companies when the catalog marks it a sponsor
    session.
    """
    hosts: list[str] = []
    for text in (item["title"], abstract.replace("\xa0", " ")):
        matches = [*HOST_PATTERN.finditer(text), *CO_HOST_PATTERN.finditer(text)]
        for match in matches:
            for name in re.split(r",\s*|\s+&\s+|\s+and\s+", match.group(1)):
                # An Oxford comma leaves "and Tailscale" as the last item.
                name = re.sub(r"^(?:and|&)\s+", "", name.strip())
                if not name or not name[0].isupper() or len(name.split()) > 4:
                    continue
                hosts.append(orgs.ensure(name, "session_host", source).id)
    sponsored = any(v["attribute"] == "Sponsor Session?" and v["value"] == "Yes"
                    for v in item["attributevalues"])
    if sponsored:
        for label in affiliations:
            for name in orgs.names_for_label(label):
                record = orgs.get(name)
                if record and "sponsor" in record.roles:
                    record.roles.add("session_host")
                    hosts.append(record.id)
    for key in orgs.session_hosts.get(item["code"], []):
        record = orgs.records.get(key)
        if record is None:
            record = orgs.ensure(orgs.curated[key]["name"], "session_host", source)
        record.roles.add("session_host")
        hosts.append(record.id)
    return list(dict.fromkeys(hosts))


def registration_link(abstract: str) -> str | None:
    """
    An external sign-up page: a link whose text asks you to register, or any link to an
    event platform. A link to a host's homepage is not a registration page.
    """
    for text, url in MARKDOWN_LINK.findall(abstract):
        host = (urlparse(url).hostname or "").removeprefix("www.")
        if "githubuniverse.com" in host:
            continue
        if REGISTRATION_TEXT.search(text) or any(host == h or host.endswith(f".{h}")
                                                  for h in REGISTRATION_HOSTS):
            return clean_url(url)
    for url in URL_PATTERN.findall(abstract):
        host = (urlparse(url).hostname or "").removeprefix("www.")
        if any(host == h or host.endswith(f".{h}") for h in REGISTRATION_HOSTS):
            return clean_url(url)
    return None


# --- People ----------------------------------------------------------------------------


def attribute(participant: dict[str, Any], name: str) -> str | None:
    return next((a.get("value") for a in participant.get("attributevalues") or []
                 if a.get("attribute") == name), None)


# Corporate-directory decorations on a listed name: a team code in capitals, "(ITDV XD)",
# and a trailing unit code, " - AF".
_DIRECTORY_CODES = re.compile(r"\s*\((?:[A-Z0-9]{2,}\s?)+\)|\s+-\s+[A-Z]{1,4}$")
_NAME_SUFFIXES = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "phd", "md"}


def clean_name(name: str) -> tuple[str, str | None, str | None]:
    """
    A listed name in display order, with given and family names when cleaning had to
    reorder it: "Harrington, Joe" becomes ("Joe Harrington", "Joe", "Harrington").
    """
    name = " ".join(_DIRECTORY_CODES.sub("", name).split())
    family, comma, given = (part.strip() for part in name.partition(","))
    if comma and given and "," not in given and given.lower() not in _NAME_SUFFIXES:
        return f"{given} {family}", given, family
    return name, None, None


def normalize_names(items: list[dict[str, Any]], renames: dict[str, str]) -> None:
    """
    Put every participant's name in display order before identity matching, and apply
    curated renames (`curation/people.yaml` `names`) for what no rule can tell.
    """
    for item in items:
        for participant in item.get("participants") or []:
            listed = person_name(participant)
            name, given, family = clean_name(renames.get(listed, listed))
            if name == listed:
                continue
            if given is None:
                given, _, family = name.rpartition(" ")
            for full, first, last in (("fullName", "firstName", "lastName"),
                                      ("globalFullName", "globalFirstname", "globalLastname")):
                participant[full], participant[first], participant[last] = name, given, family


def person_name(participant: dict[str, Any]) -> str:
    return " ".join((participant.get("globalFullName") or participant.get("fullName")
                     or "").split())


def event_field(participant: dict[str, Any], event_key: str, global_key: str) -> str | None:
    """
    The event-level value, falling back to the speaker's global RainFocus profile. Event
    fields are what this conference published; global fields can be stale or blank.
    """
    value = (participant.get(event_key) or participant.get(global_key) or "").strip()
    return value or None


def build_person(raw: RawData, participant: dict[str, Any], person_id: str, orgs: OrgIndex,
                 owners: dict[str, Any], registry: AccountRegistry,
                 catalog: Catalog = CURRENT) -> Person:
    source = raw.source(f"{catalog.prefix}/sessions.json", participant["userRef"])
    label = event_field(participant, "companyName", "globalCompany")
    title = event_field(participant, "jobTitle", "globalJobtitle")
    # A past edition's listing says where someone worked then, not now.
    # A split label ("Flox and NixOS") lists the primary organization first; the title
    # belongs to it.
    affiliations = [Affiliation(organization=orgs.ensure(name, "affiliation", source).id,
                                title=title if i == 0 else None, current=catalog.current,
                                basis="event_listing", label=label)
                    for i, name in enumerate(orgs.names_for_label(label))]

    for kind, value in (("linkedin", participant.get("linkedIn") or attribute(participant,
                                                                               "LinkedIn")),
                        ("x", participant.get("twitter") or attribute(participant, "X (Twitter)"))):
        url = clean_url(social_url(kind, value))  # pyright: ignore[reportArgumentType]
        if url:
            registry.add_url(url, person_id, "event_listing", source)
    handle = bluesky_handle(attribute(participant, "Bluesky"))
    if handle:
        registry.add_social("bluesky", handle, person_id, "event_listing", source)

    login, status = parse_github_handle(attribute(participant, "GitHub Handle"))
    github = None
    match = None
    links = []
    resolution = {"absent": "absent", "invalid": "invalid",
                  "enterprise_managed": "enterprise_managed"}.get(status, "unverified")
    sources = [source]
    if login and status == "candidate":
        node = owners.get(login.lower()) if login.lower() in owners else None
        if login.lower() not in owners:
            resolution = "unverified"
        elif node is None:
            resolution = "not_found"
        elif node["__typename"] == "Organization":
            # The speaker gave their company's account; it belongs to the organization.
            resolution = "organization_account"
            employer = orgs.records.get(affiliations[0].organization.removeprefix("org:")
                                        ) if affiliations else None
            if employer and not employer.github_login:
                employer.github_login = node["login"]
        else:
            resolution = "resolved"
            github = account_id(node["login"])
            sources.append(raw.source("github/owners.json", node["login"]))
            person_tokens = name_tokens(person_name(participant))
            same_name = bool(name_tokens(node.get("name")) & person_tokens)
            in_login = any(t in node["login"].lower() for t in person_tokens if len(t) >= 3)
            match = "name" if same_name or in_login else "unconfirmed"
        if github is None and resolution != "organization_account":
            links.append(Link(kind="github", url=f"https://github.com/{login}",
                              label="unverified"))

    return Person(
        id=person_id, name=person_name(participant),
        given_name=event_field(participant, "firstName", "globalFirstname"),
        family_name=event_field(participant, "lastName", "globalLastname"),
        job_title=title, listed_for=catalog.event_id, affiliations=affiliations,
        affiliation_label=label,
        bio=html_to_markdown(participant.get("bio") or participant.get("globalBio") or "")
        or None,
        photo_url=participant.get("photoURL") or None,
        inclusion_basis="published_by_event",
        participations=[Participation(event=catalog.event_id, role="speaker",
                                      status="confirmed")],
        links=links, github=github,
        github_resolution=resolution,  # pyright: ignore[reportArgumentType]
        github_match=match,  # pyright: ignore[reportArgumentType]
        sources=sources,
    )


def settle_affiliation_currency(person: Person) -> None:
    """
    A GitHub company field counts as current only when it agrees with the event listing,
    LinkedIn or curation, or when nothing else says where the person works.
    """
    authoritative = {a.organization for a in person.affiliations if a.basis in CURRENT_BASES}
    for affiliation in person.affiliations:
        if affiliation.basis == "github_profile" and authoritative:
            affiliation.current = affiliation.organization in authoritative


def person_keys(person: Person, registry: AccountRegistry) -> set[str]:
    accounts, websites = registry.owned_by(person.id)
    return set(accounts) | set(websites) | ({person.github} if person.github else set())


def curated_people(curation_dir: Path) -> list[dict[str, Any]]:
    """
    Hand-curated people, in the record shape hashtag attendees share. A curated person
    must cite a public source that states their part, such as their own post saying they
    will attend; nobody is listed on inference.
    """
    records: list[dict[str, Any]] = []
    curated = yaml.safe_load((curation_dir / "people.yaml").read_text()) or {}
    for entry in curated.get("people") or []:
        public = any(str(e.get("url") or "").startswith("http")
                     for e in entry.get("evidence") or [])
        if (not entry.get("role") or entry.get("status") not in {"confirmed", "self_reported"}
                or not public):
            raise ValueError(f"curation/people.yaml: {entry.get('name')} needs a role, a status "
                             "of confirmed or self_reported, and evidence with a public URL")
        affiliation = entry.get("affiliation") or {}
        records.append({
            "source": "curated",
            "name": entry["name"],
            "accounts": entry.get("accounts") or {},
            "bio": entry.get("bio"),
            "photo_url": entry.get("photo_url"),
            "role": {"title": affiliation.get("title"),
                     "organization": affiliation.get("organization")},
            "participation": {"role": entry["role"],
                              "status": entry["status"],
                              "evidence": entry.get("evidence") or []},
            "inclusion_basis": entry.get("inclusion_basis", "curated"),
            "interests": [],
        })
    return records


def _evidence(items: list[dict[str, Any]]) -> list[Evidence]:
    return [Evidence(url=e.get("url") if str(e.get("url") or "").startswith("http") else None,
                     quote=e.get("quote"), observed_at=e.get("observed_at"))
            for e in items if e.get("url") or e.get("quote")]


def add_imported_person(raw: RawData, record: dict[str, Any], people: dict[str, Person],
                        index: PeopleIndex, registry: AccountRegistry, orgs: OrgIndex,
                        owners: dict[str, Any]) -> Person:
    curated = record["source"] == "curated"
    basis = "curated" if curated else "attendance_post"
    source = (curation_source("people.yaml") if curated
              else raw.source(record["snapshot"], record.get("record_id")))
    accounts: dict[str, str | None] = record.get("accounts") or {}
    participation = record["participation"]
    evidence = _evidence(participation.get("evidence") or [])
    person_id = index.resolve(record["name"], identity_keys(accounts),
                              claims_speaking=participation["role"] == "speaker")
    if person_id:
        person = people[person_id]
        same_role = next((p for p in person.participations
                          if p.role == participation["role"]), None)
        is_speaker = any(p.role == "speaker" for p in person.participations)
        if same_role:
            same_role.evidence.extend(evidence)
        elif not (participation["role"] == "attendee" and is_speaker):
            person.participations.append(Participation(
                event=EVENT_ID, role=participation["role"], status=participation["status"],
                evidence=evidence))
        if source not in person.sources:
            person.sources.append(source)
    else:
        person_id = unique_id(f"person:{slugify(record['name'])}", people)
        photo = record.get("photo_url")
        person = Person(
            id=person_id, name=record["name"], bio=record.get("bio"),
            photo_url=photo if str(photo or "").startswith("http") else None,
            inclusion_basis=record.get("inclusion_basis") or "public_self_report",
            participations=[Participation(event=EVENT_ID, role=participation["role"],
                                          status=participation["status"],
                                          evidence=evidence)],
            github_resolution="absent", sources=[source],
        )
        people[person_id] = person

    for platform, value in accounts.items():
        if not value:
            continue
        if platform == "github":
            node = owners.get(value.lower())
            if node and node.get("__typename") == "User" and not person.github:
                person.github = account_id(node["login"])
                person.github_resolution = "resolved"
        elif platform == "website":
            registry.add_website(value, person_id, basis, source)
        elif platform == "bluesky":
            handle = bluesky_handle(value)
            if handle:
                registry.add_social("bluesky", handle, person_id, basis, source)
        else:
            url = value if "://" in value else canonical_profile_url(platform, value.lstrip("@"))
            registry.add_url(url, person_id, basis, source)

    role = record.get("role") or {}
    if role.get("organization"):
        org = orgs.ensure(role["organization"], "affiliation", source)
        # The research matched the role to a LinkedIn profile, not to the attendance post.
        linkedin = accounts.get("linkedin")
        if not any(a.organization == org.id and a.basis == basis for a in person.affiliations):
            person.affiliations.append(Affiliation(
                organization=org.id, title=role.get("title"), current=True,
                basis=basis,  # pyright: ignore[reportArgumentType]
                label=role["organization"],
                evidence=[Evidence(url=linkedin)] if linkedin else []))
    if not person.job_title and role.get("title"):
        person.job_title = role["title"]
    index.register(person_id, person.name, person_keys(person, registry))
    return person


def unique_id(candidate: str, taken: dict[str, Any]) -> str:
    entity_id, suffix = candidate, 1
    while entity_id in taken:
        suffix += 1
        entity_id = f"{candidate}-{suffix}"
    return entity_id


def github_company_orgs(company: str | None, owners: dict[str, Any], orgs: OrgIndex,
                        source: Source) -> list[OrgRecord]:
    """
    Organizations a GitHub user names as their company. `@login` mentions resolve through
    GitHub; plain names are kept only when short enough to be a company name.
    """
    text = (company or "").strip()
    if not text or text.lower() in orgs.none:
        return []
    # An organization handle can state an origin ("@Latina-Dev"); no affiliation is
    # derived from one.
    logins = [login for login in COMPANY_LOGIN.findall(text) if not is_sensitive(login)]
    if logins:
        found = []
        for login in logins:
            record = orgs.by_github_login(login)
            if record is None:
                node = owners.get(login.lower())
                if not node or node.get("__typename") != "Organization":
                    continue
                if (node.get("name") or node["login"]).strip().lower() in orgs.none:
                    continue
                record = orgs.ensure(node.get("name") or node["login"], "affiliation", source)
                record.github_login = record.github_login or node["login"]
            record.roles.add("affiliation")
            found.append(record)
        return found
    if "@" in text or "://" in text or len(text.split()) > 5:
        return []
    return [orgs.ensure(name, "affiliation", source) for name in orgs.names_for_label(text)]


# GitHub programs the GraphQL API reports directly, by the field that says so.
GITHUB_PROGRAMS = {"isGitHubStar": "GitHub Star", "isCampusExpert": "GitHub Campus Expert"}


def program_recognitions(node: dict[str, Any] | None, existing: list[Claim]) -> list[Claim]:
    """Program memberships GitHub itself states, unless the profile already names them."""
    named = {c.label.lower() for c in existing}
    return [Claim(label=label, basis="github_profile", confidence="high",
                  evidence=[Evidence(url=node["url"], ref=account_id(node["login"]))])
            for flag, label in GITHUB_PROGRAMS.items()
            if node and node.get(flag) and label.lower() not in named]


def interest_signals(profile: Profile, sessions: dict[str, Session],
                     term_labels: dict[str, str], repositories: dict[str, Repository]
                     ) -> list[Signal]:
    """
    The sightings `infer_interests` weighs for one person: the topics of their sessions
    and of the repositories they own, pin or contribute to. Stars and hashtags are not
    signals: they are likes and personal tags, which can imply health or beliefs.
    """
    signals = []
    for talk in profile.talks:
        session = sessions.get(talk)
        if session is None:
            continue
        # Topics and products name subjects; tracks are themes ("Build software, not code").
        for term in [*session.facets.topics, *session.facets.products]:
            if term in term_labels:
                signals.append(Signal("session_facets", term_labels[term],
                                      Evidence(url=session.url, ref=session.id), target=term))
    for work in profile.open_source:
        repo = repositories.get(work.repository)
        for topic in repo.topics if repo else []:
            signals.append(Signal("github_repositories", topic,
                                  Evidence(url=repo.url, ref=repo.id) if repo else Evidence()))
    return signals


def reject_conflicting_github_claims(people: dict[str, Person], orgs: OrgIndex,
                                    registry: AccountRegistry) -> set[str]:
    """Reject every owner of a shared login; cleared claims remain known for this build."""
    for person in people.values():
        if person.github:
            registry.claim_github(person.github.removeprefix("gh:"), person.id, "listed")
    for record in orgs.records.values():
        if record.github_login:
            registry.claim_github(record.github_login, record.id, "organization")
    ambiguous = {login for login, claimants in registry.github_claimants().items()
                 if len(claimants) > 1}
    for person in people.values():
        candidates = set(registry.github_claims.get(person.id, {})) & ambiguous
        for candidate in sorted(candidates):
            url = f"https://github.com/{candidate}"
            if not any(link.kind == "github" and link.url.lower() == url for link in person.links):
                person.links.append(Link(kind="github", url=url, label="unverified"))
        login = person.github.removeprefix("gh:").lower() if person.github else None
        if login is None or login not in ambiguous:
            if candidates and not person.github and person.github_resolution == "absent":
                person.github_resolution = "unverified"
            continue
        person.github = None
        person.github_match = None
        person.github_resolution = "unverified"
        person.accounts = [ref for ref in person.accounts if ref.lower() != account_id(login)]
        person.sources = [source for source in person.sources
                          if not (source.snapshot == "raw/github/owners.json"
                                  and (source.record_id or "").lower() == login)]
    for record in orgs.records.values():
        if record.github_login and record.github_login.lower() in ambiguous:
            record.github_login = None
    return ambiguous


def discover_github_claims(raw: RawData, people: dict[str, Person], owners: dict[str, Any],
                           registry: AccountRegistry, orgs: OrgIndex) -> None:
    """Discover conflicts on private copies before GitHub facts enrich real owners."""
    preview_people, preview_registry, preview_orgs = deepcopy((people, registry, orgs))
    reject_conflicting_github_claims(preview_people, preview_orgs, preview_registry)
    link_github_profiles(raw, preview_people, owners, preview_registry, preview_orgs)
    link_websites(raw, preview_registry, preview_people, preview_orgs, finalize_ownership=False)
    fill_bluesky(raw, preview_registry)
    fill_mastodon(raw, preview_registry)
    fill_x(raw, preview_registry, preview_people)
    fill_linkedin(raw, preview_registry, preview_people, preview_orgs)
    link_websites(raw, preview_registry, preview_people, preview_orgs, finalize_ownership=False)
    adopted = adopt_github_claims(raw, preview_people, owners, preview_registry, preview_orgs)
    link_github_profiles(raw, adopted, owners, preview_registry, preview_orgs, organizations=False)
    details = organization_details(raw, preview_orgs.records, owners, preview_registry)
    for organization in preview_orgs.records.values():
        profile = details.get(organization.id)
        if profile and profile.website and not organization.website:
            organization.website = profile.website
    link_websites(raw, preview_registry, preview_people, preview_orgs)
    for owner, claims in preview_registry.github_claims.items():
        for login, bases in claims.items():
            for basis in bases:
                registry.claim_github(login, owner, basis)
    reject_conflicting_github_claims(people, orgs, registry)


def adopt_github_claims(raw: RawData, people: dict[str, Person], owners: dict[str, Any],
                        registry: AccountRegistry, orgs: OrgIndex | None = None
                        ) -> dict[str, Person]:
    """
    Give a GitHub account to people whose listing had none, when their own LinkedIn, X,
    Mastodon or homepage links one. The best-corroborated user account wins; its name
    decides `github_match` as for listed handles. Returns the people changed.
    """
    ambiguous = reject_conflicting_github_claims(
        people, orgs if orgs is not None else OrgIndex({"organizations": {}}, {}), registry)
    adopted: dict[str, Person] = {}
    for person in people.values():
        claims = registry.github_claims.get(person.id) or {}
        if person.github or not claims:
            continue
        tokens = name_tokens(person.name)
        users = [(login, bases, owners[login]) for login, bases in claims.items()
                 if login not in ambiguous
                 and (owners.get(login) or {}).get("__typename") == "User"]
        if not users:
            continue
        login, _, node = max(users, key=lambda u: (
            len(u[1]), bool(name_tokens(u[2].get("name")) & tokens), u[0]))
        person.github = account_id(node["login"])
        person.github_resolution = "resolved"
        same_name = bool(name_tokens(node.get("name")) & tokens)
        in_login = any(t in login for t in tokens if len(t) >= 3)
        person.github_match = "name" if same_name or in_login else "unconfirmed"
        person.sources.append(raw.source("github/owners.json", node["login"]))
        adopted[person.id] = person
    return adopted


def link_github_profiles(raw: RawData, people: dict[str, Person], owners: dict[str, Any],
                         registry: AccountRegistry, orgs: OrgIndex,
                         organizations: bool = True) -> None:
    """
    Accounts, websites and current employers that people declare on their GitHub profile,
    and, unless `organizations` is false, organizations' X accounts and websites.
    """
    reject_conflicting_github_claims(people, orgs, registry)
    for person in people.values():
        node = owners.get(person.github.removeprefix("gh:")) if person.github else None
        if not node:
            continue
        source = raw.source("github/owners.json", node["login"])
        # `add_url` decides account or website from the URL itself: GitHub labels many
        # profile links (Threads, Mastodon, YouTube) as generic websites.
        for _platform, url in github_social_links(node):
            registry.add_url(url, person.id, "github_profile", source)
        company = (node.get("company") or "").strip()
        for org in github_company_orgs(company, owners, orgs, source):
            if not any(a.organization == org.id and a.basis == "github_profile"
                       for a in person.affiliations):
                person.affiliations.append(Affiliation(
                    organization=org.id, current=True, basis="github_profile", label=company,
                    evidence=[Evidence(url=node["url"], quote=company)]))
    if not organizations:
        return
    for record in list(orgs.records.values()):
        node = owners.get(record.github_login.lower()) if record.github_login else None
        if not node:
            continue
        source = raw.source("github/owners.json", node["login"])
        if node.get("twitterUsername"):
            registry.add_social("x", node["twitterUsername"], record.id, "github_profile",
                                source)
        if not record.website and node.get("websiteUrl"):
            record.website = website_of(node["websiteUrl"])


def is_company_site(url: str, person: Person | None, orgs: OrgIndex) -> bool:
    """
    Whether a site a person links to belongs to one of their organizations: its domain
    matches the organization's website, or a part of its host contains the organization's
    name ("floxdev.com" for Flox).
    """
    if person is None:
        return False
    domain = registrable_domain(url) or ""
    host = (urlparse(url if "://" in url else f"https://{url}").hostname or "").lower()
    # Every part of a company host can name it ("m365.cloud.microsoft"); on a personal
    # hosting domain ("ada.github.io") only the user's own part could.
    labels = set(host.split(".")) if domain not in PERSONAL_HOSTING else {host.split(".")[0]}
    if any(record.website and registrable_domain(record.website) == domain
           for record in orgs.records.values()):
        return True
    for affiliation in person.affiliations:
        record = orgs.records.get(affiliation.organization.removeprefix("org:"))
        if record is None:
            continue
        if record.website and registrable_domain(record.website) == domain:
            return True
        key = record.key.replace("-", "")
        if len(key) >= 3 and any(key in part for part in labels):
            return True
    return False


# Domains where each user gets a personal subdomain.
PERSONAL_HOSTING = {"github.io", "gitlab.io", "blogspot.com", "wordpress.com", "substack.com",
                    "medium.com", "netlify.app", "vercel.app", "pages.dev", "dev.to"}


def company_site_owners(url: str, orgs: OrgIndex) -> set[str]:
    """Organization owners supported by an exact authoritative host or its subdomain."""
    host = (urlparse(url if "://" in url else f"https://{url}").hostname or "").lower()
    host = host.rstrip(".").removeprefix("www.")
    matches = set()
    for organization in orgs.records.values():
        if not organization.website:
            continue
        website = organization.website
        authoritative = (urlparse(website if "://" in website else f"https://{website}")
                         .hostname or "").lower().rstrip(".").removeprefix("www.")
        if authoritative and (host == authoritative or host.endswith(f".{authoritative}")):
            matches.add(organization.id)
    return matches


def link_websites(raw: RawData, registry: AccountRegistry, people: dict[str, Person],
                  orgs: OrgIndex, *, finalize_ownership: bool = True) -> None:
    """
    Fill websites from fetched homepages. Site links corroborate accounts already
    attributed by a person's own profile or listing; linking a site does not establish
    that the person owns the site or the site's accounts.
    """
    homepages = raw.load("websites/homepages.json") if raw.has("websites/homepages.json") else {}
    pages_by_site = {}
    # Prefer an untracked cache entry and make any remaining alias choice deterministic.
    for url, page in sorted(homepages.items(), key=lambda item: (
            canonical_website_url(item[0]) != item[0], item[0])):
        if not isinstance(page, dict) or not page:
            continue
        pages_by_site.setdefault(website_id(url if "://" in url else f"https://{url}"), (url, page))
    for site_id, record in list(registry.websites.items()):
        site = record.website
        owners = company_site_owners(site.url, orgs)
        if len(owners) > 1 or (finalize_ownership and not owners and is_company_site(
                site.url, people.get(record.owner), orgs)):
            # A company-site signal cannot establish which organization owns it.
            registry.websites.pop(site_id)
            continue
        if owners:
            owner = next(iter(owners))
            record.owner = site.owner = owner
            site.kind = "company"
            organization = orgs.records[owner.removeprefix("org:")]
            site.sources.extend(s for s in organization.sources if s not in site.sources)
            site.linked_accounts = [a for a in site.linked_accounts
                                    if a in registry.accounts
                                    and registry.accounts[a].owner == owner]
        cached = pages_by_site.get(site_id)
        # Ownership can change on a later pass after validated company details arrive.
        if not cached or site.fetch_status != "not_fetched":
            continue
        input_url, page = cached
        site.fetch_status = "ok" if page.get("status") == 200 else "error"
        site.http_status = page.get("status")
        site.title = page.get("title")
        site.description = page.get("description")
        site.identity_links = [u for u in page.get("rel_me") or [] if u.startswith("http")]
        site.feeds = [u for u in page.get("feeds") or [] if u.startswith("http")]
        source = raw.source("websites/homepages.json", input_url,
                            url=page.get("final_url") or site.url)
        site.sources.append(source)
        linked = []
        for link in page.get("rel_me") or []:
            # A person can link a project or employer site. Its rel=me says who
            # owns the site, not who owns every profile that linked to the site.
            classified = classify_social_url(link)
            existing = registry.accounts.get(social_account_id(*classified)) if classified \
                else None
            if existing and existing.owner == record.owner:
                linked.append(existing.account.id)
        for link in page.get("social_links") or []:
            classified = classify_social_url(link)
            if not classified or classified[0] == "github":
                continue
            existing = registry.accounts.get(social_account_id(*classified))
            if existing and existing.owner == record.owner:
                if "website_link" not in existing.account.link_basis:
                    existing.account.link_basis.append("website_link")
                linked.append(existing.account.id)
        site.linked_accounts = sorted(set(linked))


def fill_bluesky(raw: RawData, registry: AccountRegistry) -> None:
    if not raw.has("bluesky/profiles.json"):
        return
    profiles = raw.load("bluesky/profiles.json")
    for record in registry.accounts.values():
        account = record.account
        profile = profiles.get(account.handle.lower()) if account.platform == "bluesky" else None
        if not profile:
            continue
        account.display_name = profile.get("display_name") or None
        account.bio = profile.get("description") or None
        account.followers = profile.get("followers")
        created = profile.get("created_at")
        account.created_at = re.sub(r"\.\d+(?=Z|[+-])", "", created) if created else None
        account.details_fetched = True
        account.sources.append(raw.source("bluesky/profiles.json", account.handle))


@dataclass
class Edition:
    event: Event
    sessions: list[Session]
    facets: list[Facet]


def catalog_items(raw: RawData, catalog: Catalog) -> list[dict[str, Any]]:
    """Catalog rows, without RainFocus test records and rows with no scheduled time."""
    return [item for item in raw.load(f"{catalog.prefix}/sessions.json")["items"]
            if item.get("times") and not item.get("testRecord")
            and "test speaker" not in item.get("title", "").lower()]


def listing_keys(participant: dict[str, Any]) -> set[str]:
    """Identity keys from a catalog speaker record's own account fields."""
    keys = {f"rainfocus:{participant['userRef']}"} if participant.get("userRef") else set()
    login, status = parse_github_handle(attribute(participant, "GitHub Handle"))
    if login and status == "candidate":
        keys.add(account_id(login))
    for kind, value in (("linkedin", participant.get("linkedIn") or attribute(participant,
                                                                               "LinkedIn")),
                        ("x", participant.get("twitter") or attribute(participant, "X (Twitter)"))):
        url = social_url(kind, value)  # pyright: ignore[reportArgumentType]
        classified = classify_social_url(url) if url else None
        if classified:
            keys.add(social_account_id(*classified))
    handle = bluesky_handle(attribute(participant, "Bluesky"))
    if handle:
        keys.add(social_account_id("bluesky", handle))
    return keys


def merge_listing(raw: RawData, participant: dict[str, Any], person: Person, orgs: OrgIndex,
                  registry: AccountRegistry, catalog: Catalog) -> None:
    """Add a past edition's speaker record to a person who is already in the graph."""
    source = raw.source(f"{catalog.prefix}/sessions.json", participant["userRef"])
    if not any(p.event == catalog.event_id for p in person.participations):
        person.participations.append(Participation(event=catalog.event_id, role="speaker",
                                                   status="confirmed"))
    label = event_field(participant, "companyName", "globalCompany")
    title = event_field(participant, "jobTitle", "globalJobtitle")
    for i, name in enumerate(orgs.names_for_label(label)):
        org = orgs.ensure(name, "affiliation", source)
        held = title if i == 0 else None
        if not any(a.organization == org.id and a.basis == "event_listing" and not a.current
                   and a.title == held for a in person.affiliations):
            person.affiliations.append(Affiliation(
                organization=org.id, title=held, current=False, basis="event_listing",
                label=label, evidence=[Evidence(observed_at=catalog.year)]))
    for kind, value in (("linkedin", participant.get("linkedIn") or attribute(participant,
                                                                               "LinkedIn")),
                        ("x", participant.get("twitter") or attribute(participant, "X (Twitter)"))):
        url = clean_url(social_url(kind, value))  # pyright: ignore[reportArgumentType]
        if url:
            registry.add_url(url, person.id, "event_listing", source)
    handle = bluesky_handle(attribute(participant, "Bluesky"))
    if handle:
        registry.add_social("bluesky", handle, person.id, "event_listing", source)
    if not person.bio:
        person.bio = html_to_markdown(participant.get("bio") or participant.get("globalBio")
                                      or "") or None
    if not person.photo_url:
        person.photo_url = participant.get("photoURL") or None
    if source not in person.sources:
        person.sources.append(source)


def add_edition(raw: RawData, catalog: Catalog, people: dict[str, Person], index: PeopleIndex,
                registry: AccountRegistry, orgs: OrgIndex, owners: dict[str, Any],
                rooms: dict[str, Room], venues: dict[str, Venue],
                venue_curation: dict[str, Any], renames: dict[str, str],
                rejected_sources: set[str]) -> Edition:
    """
    One past edition: its taxonomy, rooms, sessions and speakers. A returning speaker
    merges into the existing person by any shared account or a unique name; everyone
    else becomes a person whose listed affiliation is marked as past.
    """
    items = catalog_items(raw, catalog)
    filter_catalog_people(items, f"{catalog.prefix}/sessions.json", rejected_sources)
    canonicalize_attributes(raw, catalog, items)
    normalize_names(items, renames)
    facets, term_by_label = build_facets(raw, items, catalog)
    build_rooms(raw, items, venues, venue_curation, rooms, catalog)

    participants: dict[str, dict[str, Any]] = {}
    for item in items:
        for participant in item.get("participants") or []:
            if not participant.get("testRecord"):
                participants.setdefault(participant["userRef"], participant)
    person_ids: dict[str, str] = {}
    for user_ref, participant in participants.items():
        name = person_name(participant)
        person_id = index.resolve(name, listing_keys(participant), claims_speaking=True)
        if person_id is None:
            person_id = unique_id(f"person:{slugify(name)}", people)
            people[person_id] = build_person(raw, participant, person_id, orgs, owners,
                                             registry, catalog)
        else:
            merge_listing(raw, participant, people[person_id], orgs, registry, catalog)
        index.register(person_id, people[person_id].name,
                       person_keys(people[person_id], registry) | listing_keys(participant))
        person_ids[user_ref] = person_id

    by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_session[item["sessionID"]].append(item)
    session_ids = assign_ids({sid: rows[0]["code"] for sid, rows in by_session.items()},
                             "session", namespace=catalog.namespace)
    sessions = [build_session(raw, rows, session_ids, person_ids, term_by_label, rooms, orgs,
                              catalog) for rows in by_session.values()]
    for session in sessions:
        for speaker in session.speakers:
            person = people[speaker.person]
            person.sessions.append(PersonSession(session=session.id, role=speaker.role))
            participation = next(p for p in person.participations
                                 if p.event == catalog.event_id)
            participation.evidence.append(Evidence(url=session.url, ref=session.id))
        for host in session.hosts:
            orgs.records[host.removeprefix("org:")].hosted_sessions.add(session.id)
    for room in rooms.values():
        room.sessions.sort()
    return Edition(past_event(raw, catalog, sessions, rooms, venues), sessions, facets)


def catalog_day_labels(raw: RawData, catalog: Catalog, dates: list[str]) -> dict[str, str]:
    """
    Keep the catalog's explicit Day N labels. For weekday-only catalogs, identify
    main-program days by session density; sparse days outside that span are pre/post.
    """
    counts: Counter[str] = Counter()
    explicit: dict[str, set[str]] = defaultdict(set)
    for item in catalog_items(raw, catalog):
        for time in item["times"]:
            day = local_iso(time["utcStartTime"])[:10]
            counts[day] += 1
            label = str(time.get("dayDisplayName") or "").strip()
            if re.fullmatch(r"Day \d+", label):
                explicit[day].add(label)
    peak = max(counts.values(), default=0)
    main = [d for d in dates if counts[d] >= peak * MAIN_PROGRAM_DENSITY_FRACTION]
    first, last = (main[0], main[-1]) if main else (dates[0], dates[-1])
    numbered = {d: f"Day {i}" for i, d in enumerate(
        (d for d in dates if first <= d <= last), start=1)}
    return {d: (next(iter(explicit[d])) if len(explicit[d]) == 1 else
                "Pre-event" if d < first else "Post-event" if d > last else numbered[d])
            for d in dates}


def past_event(raw: RawData, catalog: Catalog, sessions: list[Session], rooms: dict[str, Room],
               venues: dict[str, Venue]) -> Event:
    slots = [slot for session in sessions for slot in session.slots]
    dates = sorted({slot.start[:10] for slot in slots})
    by_id = {v.id: v for v in venues.values()}
    labels = catalog_day_labels(raw, catalog, dates)

    def site(venue_id: str | None) -> Venue | None:
        venue = by_id.get(venue_id) if venue_id else None
        while venue and venue.parent:
            venue = by_id.get(venue.parent)
        return venue if venue and venue.kind != "external" else None

    # The edition's venue is the place where most of its sessions were held.
    held = Counter(found.id for slot in slots if slot.room and slot.room in rooms
                   for found in [site(rooms[slot.room].venue)] if found)
    portal = f"{PORTAL_URL}/flow/github/{catalog.edition}/attendee-portal/page/sessioncatalog"
    venue = held.most_common(1)[0][0] if held else None
    first, last = (date.fromisoformat(d) for d in (dates[0], dates[-1]))
    span = (f"{first:%B} {first.day} to {last.day}, {first.year}" if first.month == last.month
            else f"{first:%B} {first.day} to {last:%B} {last.day}, {first.year}")
    # Derived from the catalog, whose dates include sessions before and after the main
    # days; the site's own copy for past editions is not archived here.
    description = (f"GitHub Universe {catalog.year} was held"
                   + (f" at {by_id[venue].name} in San Francisco" if venue else "")
                   + f" and online. Its session catalog lists {len(sessions)} sessions"
                   f" from {span}.")
    return Event(
        id=catalog.event_id, name=f"GitHub Universe {catalog.year}", series="GitHub Universe",
        edition=catalog.year, organizer="org:github",
        start=min(slot.start for slot in slots), end=max(slot.end for slot in slots),
        timezone=TIMEZONE, attendance_modes=["in_person", "virtual"],
        venue=venue, description=description, url=portal,
        days=[EventDay(id=f"day:{d}", date=d, label=labels[d]) for d in dates],
        sources=[raw.source(f"{catalog.prefix}/sessions.json")],
    )


def repository_packages(raw: RawData, repositories: dict[str, Repository],
                        accounts: dict[str, GitHubAccount], packages: list[Package]
                        ) -> dict[str, set[str]]:
    """
    Registry package metadata, merged with gazetteer packages. Link source repositories
    only with saved manifest evidence; never infer registry publishing authority from
    repository ownership. The publisher map stays empty without independent evidence.
    """
    by_id = {p.id: p for p in packages}
    published: dict[str, set[str]] = defaultdict(set)
    if not raw.has("packages/repo-packages.json"):
        return published
    for full_name, result in raw.load("packages/repo-packages.json").items():
        repo = repositories.get(repo_id(full_name))
        if repo is None:
            continue
        for found in result.get("packages") or []:
            if not found.get("verified") or not str(found.get("url") or "").startswith("http"):
                continue
            ref = package_id(found["ecosystem"], found["name"])
            package = by_id.get(ref)
            if package is None:
                package = Package(
                    id=ref, ecosystem=found["ecosystem"], name=found["name"], url=found["url"],
                    description=found.get("description"),
                    latest_version=found.get("latest_version"), license=found.get("license"),
                    repository_url=found.get("repository_url"),
                    sources=[raw.source("packages/repo-packages.json", full_name)])
                by_id[ref] = package
                packages.append(package)
            # Legacy snapshots retain registry metadata, but a backlink alone proves
            # neither that this repository declares the package nor who publishes it.
            declaration = found.get("declared_in")
            sample = re.search(r"(?:^|[-_/])(?:samples?|templates?)(?:$|[-_/])", full_name.lower())
            checked = {c.get("file") for c in result.get("checked", []) if c.get("status") == 200}
            if (declaration not in MANIFESTS.get(found["ecosystem"], [])
                    or declaration not in checked or sample):
                continue
            package.repository = repo.id
            # Repository ownership cannot establish registry publishing authority.
            # Keep publishers empty until a separate source verifies that relation.
    return published


def build_featured(raw: RawData, people: list[Person]) -> set[str]:
    by_name = {p.name.lower(): p.id for p in people}
    featured = set()
    for name, _org in pages.home_featured_speakers(raw.text("site/home.html")):
        person = by_name.get(name.lower())
        if person:
            featured.add(person)
        else:
            log.warning("featured speaker not in catalog: %s", name)
    return featured


# --- GitHub ----------------------------------------------------------------------------


def repository_model(node: dict[str, Any], source: Source,
                     known_accounts: set[str]) -> Repository:
    owner_login = node["owner"]["login"]
    return Repository(
        id=repo_id(node["nameWithOwner"]), full_name=node["nameWithOwner"], url=node["url"],
        description=node.get("description"), homepage=node.get("homepageUrl") or None,
        stars=node["stargazerCount"], forks=node["forkCount"],
        primary_language=(node.get("primaryLanguage") or {}).get("name"),
        topics=[t["topic"]["name"] for t in node["repositoryTopics"]["nodes"]],
        license=(node.get("licenseInfo") or {}).get("spdxId"),
        archived=node["isArchived"], fork=node["isFork"],
        created_at=node.get("createdAt"), pushed_at=node.get("pushedAt"),
        owner_login=owner_login,
        owner=account_id(owner_login) if account_id(owner_login) in known_accounts else None,
        sources=[source],
    )


def apply_repo_stats(raw: RawData, repositories: dict[str, Repository]) -> int:
    """
    Replace the counts that came with an owner's record by those `universe-kb
    refresh-repos` read from each repository directly, with the time it read them.
    Repositories the refresh found missing keep their counts. Returns how many it set.
    """
    if not raw.has(REPO_STATS) or REPO_STATS not in raw.manifest:
        return 0
    stats = raw.load(REPO_STATS)
    updated = 0
    for repo in repositories.values():
        node = stats.get(repo.full_name.lower())
        if not node or node.get("missing"):
            continue
        repo.stars, repo.forks = node["stargazerCount"], node["forkCount"]
        repo.archived, repo.pushed_at = node["isArchived"], node.get("pushedAt")
        repo.watchers = (node.get("watchers") or {}).get("totalCount")
        repo.open_issues = (node.get("issues") or {}).get("totalCount")
        repo.stats_observed_at = node["fetched_at"]
        source = raw.source(REPO_STATS, repo.full_name)
        if source not in repo.sources:
            repo.sources.append(source)
        updated += 1
    return updated


def build_github(raw: RawData, owners: dict[str, Any], people: list[Person], orgs: OrgIndex,
                 registry: AccountRegistry | None = None
                 ) -> tuple[dict[str, GitHubAccount], dict[str, Repository]]:
    reject_conflicting_github_claims(
        {person.id: person for person in people}, orgs,
        registry if registry is not None else AccountRegistry())
    entity_for: dict[str, str] = {}
    for person in people:
        if person.github:
            entity_for[person.github] = person.id
    for record in orgs.records.values():
        if record.github_login and owners.get(record.github_login.lower()):
            entity_for[account_id(record.github_login)] = record.id
    known = set(entity_for)

    accounts: dict[str, GitHubAccount] = {}
    repositories: dict[str, Repository] = {}
    for account_ref, entity in entity_for.items():
        node = owners[account_ref.removeprefix("gh:")]
        source = raw.source("github/owners.json", node["login"])
        pinned = [r for r in (node.get("pinnedItems") or {}).get("nodes") or [] if r]
        top = [r for r in (node.get("repositories") or {}).get("nodes") or []
               if r and r["stargazerCount"] >= TOP_REPOSITORY_MIN_STARS
               and r["nameWithOwner"] not in {p["nameWithOwner"] for p in pinned}]
        top = top[:TOP_REPOSITORIES_PER_ACCOUNT]
        for repo_node in [*pinned, *top]:
            repo = repositories.setdefault(repo_id(repo_node["nameWithOwner"]),
                                           repository_model(repo_node, source, known))
            if repo_node in pinned and account_ref not in repo.pinned_by:
                repo.pinned_by.append(account_ref)
        contributed = [r for r in (node.get("repositoriesContributedTo") or {}).get("nodes")
                       or [] if r]
        for repo_node in contributed:
            repositories.setdefault(repo_id(repo_node["nameWithOwner"]),
                                    repository_model(repo_node, source, known))
        readme_key = "orgReadme" if node["__typename"] == "Organization" else "userReadme"
        readme = (((node.get(readme_key) or {}).get("object") or {}).get("text") or "").strip()
        counts = node.get("contributionsCollection")
        accounts[account_ref] = GitHubAccount(
            id=account_ref, login=node["login"],
            kind="organization" if node["__typename"] == "Organization" else "user",
            url=node["url"], name=node.get("name") or None, company=node.get("company"),
            bio=node.get("bio") or node.get("description") or None,
            location=node.get("location"), website=node.get("websiteUrl"),
            followers=(node.get("followers") or {}).get("totalCount"),
            public_repositories=(node.get("repositories") or {}).get("totalCount"),
            created_at=node.get("createdAt"),
            profile_readme=professional_readme(readme) or None,
            contributions_last_year=Contributions(
                total=counts["contributionCalendar"]["totalContributions"],
                commits=counts["totalCommitContributions"],
                pull_requests=counts["totalPullRequestContributions"],
                issues=counts["totalIssueContributions"],
                reviews=counts["totalPullRequestReviewContributions"],
            ) if counts else None,
            starred_repositories=(node.get("starredRepositories") or {}).get("totalCount"),
            has_sponsors_listing=node.get("hasSponsorsListing"),
            contribution_years=sorted(((counts or {}).get("contributionYears") or []),
                                      reverse=True),
            github_star=node.get("isGitHubStar"), campus_expert=node.get("isCampusExpert"),
            github_employee=node.get("isEmployee"),
            gists=(node.get("gists") or {}).get("totalCount"),
            contributed_to=[repo_id(r["nameWithOwner"]) for r in contributed],
            organization_logins=[o["login"] for o in
                                 (node.get("organizations") or {}).get("nodes") or []],
            pinned=[repo_id(r["nameWithOwner"]) for r in pinned],
            top_repositories=[repo_id(r["nameWithOwner"]) for r in top],
            entity=entity, sources=[source],
        )
    return accounts, repositories


# --- Software --------------------------------------------------------------------------


def build_software(raw: RawData, entries: dict[str, dict[str, Any]],
                   mentioned_in: dict[str, set[str]], orgs: OrgIndex,
                   repositories: dict[str, Repository],
                   term_by_label: dict[tuple[str, str], str],
                   known_accounts: set[str],
                   ) -> tuple[list[Software], list[Package]]:
    claimed = raw.load("github/repos.json") if raw.has("github/repos.json") else {}
    registries = {eco: raw.load(f"registries/{eco}.json")
                  for eco in ("npm", "pypi") if raw.has(f"registries/{eco}.json")}
    software: list[Software] = []
    packages: list[Package] = []
    for ref, entry in entries.items():
        product_term = (term_by_label.get(("GitHub product", entry["product_term"]))
                        if entry.get("product_term") else None)
        if not mentioned_in.get(ref) and not product_term:
            continue
        repos = []
        for full_name in entry.get("repositories", []):
            node = claimed.get(full_name.lower())
            if node:
                source = raw.source("github/repos.json", node["nameWithOwner"])
                repo = repositories.setdefault(repo_id(node["nameWithOwner"]),
                                               repository_model(node, source, known_accounts))
                if source not in repo.sources:
                    repo.sources.append(source)
                repo.software = ref
                repos.append(repo.id)
        package_refs = []
        for claim in entry.get("packages", []):
            ecosystem, name = claim.split(":", 1)
            found = registries.get(ecosystem, {}).get(name)
            if found:
                package = Package(
                    id=package_id(ecosystem, name), ecosystem=ecosystem,  # pyright: ignore[reportArgumentType]
                    name=found["name"] or name, url=found["url"],
                    description=found.get("description"),
                    latest_version=found.get("latest_version"), license=found.get("license"),
                    repository_url=found.get("repository_url"), software=ref,
                    sources=[raw.source(f"registries/{ecosystem}.json", name)],
                )
                packages.append(package)
                package_refs.append(package.id)
        vendor = entry.get("vendor")
        vendor_ref = f"org:{vendor}" if vendor and vendor in orgs.records else None
        software.append(Software(
            id=ref, name=entry["name"], aliases=entry.get("aliases", []), kind=entry["kind"],
            vendor=vendor_ref, homepage=entry.get("homepage"), product_term=product_term,
            repositories=repos, packages=package_refs,
            mentioned_in=sorted(mentioned_in.get(ref, set())),
            sources=[curation_source("software.yaml")],
        ))
    return software, packages


# --- Experiences and event -------------------------------------------------------------


def build_experiences(raw: RawData, venues: dict[str, Venue]) -> list[Experience]:
    explore = raw.load("rainfocus/pages/explore.json")
    catalog = raw.load("rainfocus/pages/sessioncatalog.json")
    explore_ids = {c["id"] for c in pages.experiences(explore, {"data": {"pageData": {}}})}
    curation = {"venues": {k: {"aliases": [v.name]} for k, v in venues.items()}}
    experiences = []
    for card in pages.experiences(explore, catalog):
        venue_key = None
        if card["location"]:
            venue_key = match_venue(card["location"], curation) or next(
                (k for k, v in venues.items() if card["location"] in v.name), None)
        page = "explore" if card["id"] in explore_ids else "sessioncatalog"
        experiences.append(Experience(
            id=f"experience:{card['id']}", name=card["name"], description=card["description"],
            category=card["category"], schedule=card["schedule"], location=card["location"],
            venue=f"venue:{venue_key}" if venue_key else None, action=card["action"],
            action_url=card["action_url"], image_url=card.get("image_url"),
            sources=[raw.source(f"rainfocus/pages/{page}.json")],
        ))
    return experiences


def build_event(raw: RawData, organizer: OrgRecord, session_days: set[str],
                featured: list[str]) -> Event:
    home = raw.text("site/home.html")
    data = pages.json_ld_event(home)
    year = int(data["startDate"][:4])
    days = pages.home_agenda(home, year)
    known = {d["id"] for d in days}
    first = min((d["date"] for d in days), default=data["startDate"][:10])
    last = max((d["date"] for d in days), default=data["endDate"][:10])
    for day in sorted(session_days - known):
        day_date = day.removeprefix("day:")
        label = ("Pre-event" if day_date < first else "Post-event" if day_date > last
                 else "Additional programming")
        days.append({"id": day, "date": day_date, "label": label,
                     "access": None, "agenda": []})
    days.sort(key=lambda d: d["date"])
    offer = data.get("offers") or {}
    price = float(offer["price"]) if offer.get("price") else None
    return Event(
        id=EVENT_ID, name=f"{data['name']} {year}", series=data["name"], edition=str(year),
        organizer=organizer.id, start=data["startDate"], end=data["endDate"],
        timezone=TIMEZONE, attendance_modes=["in_person", "virtual"],
        venue="venue:fort-mason-center", url=f"{SITE_URL}/", description=data["description"],
        days=days,  # pyright: ignore[reportArgumentType]
        offers=pages.pricing_offers(raw.text("site/pricing.html"), price,  # pyright: ignore[reportArgumentType]
                                    offer.get("priceCurrency", "USD")),
        tour_stops=pages.tour_stops(raw.text("site/on-the-road.html"), year),  # pyright: ignore[reportArgumentType]
        featured_speakers=featured,
        highlights=pages.home_highlights(home, SITE_URL, year),  # pyright: ignore[reportArgumentType]
        testimonials=pages.home_testimonials(home),
        sources=[raw.source("site/home.html"), raw.source("site/pricing.html"),
                 raw.source("site/on-the-road.html")],
    )
