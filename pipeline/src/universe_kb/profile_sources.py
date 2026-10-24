"""
Apply enrichment snapshots to people: LinkedIn and X details from Bright Data, Mastodon
profiles, recent writing from website feeds, and attendees found on Mastodon hashtag
timelines.

Every function reads one raw snapshot and writes into the account registry, the people,
or a per-person dictionary of profile sections that the build attaches to profiles. Each
fact keeps the profile URL or post it came from.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from universe_kb.ids import registrable_domain
from universe_kb.models import (
    Activity,
    AffiliatedPage,
    Affiliation,
    Credential,
    EducationEntry,
    Evidence,
    OrgDescription,
    OrgUpdate,
    Patent,
    Person,
    Position,
    Publication,
    Source,
    WritingItem,
)
from universe_kb.people import (
    AccountRegistry,
    catalog_x_mismatch,
    other_profile,
    rejected_link_fingerprint,
    social_account_id,
    website_id,
)
from universe_kb.policy import says_attending
from universe_kb.sensitive import is_sensitive
from universe_kb.web import classify_social_url

if TYPE_CHECKING:
    from universe_kb.build import OrgIndex, RawData

MAX_WRITING = 10
QUOTE_LIMIT = 280
# Recent LinkedIn posts kept per organization.
ORG_UPDATES = 5


@dataclass
class ProfileExtras:
    experience: list[Position] = field(default_factory=list)
    education: list[EducationEntry] = field(default_factory=list)
    credentials: list[Credential] = field(default_factory=list)
    spoken_languages: list[str] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)
    writing: list[WritingItem] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)
    patents: list[Patent] = field(default_factory=list)


# Granted US patents are numbered below this; larger "US" numbers people list are
# application serials ("US 18930687"), which Google Patents does not address that way.
US_GRANTED_LIMIT = 13_000_000


def patent_url(number: str | None) -> str | None:
    """Google Patents for a listed number: "US 9286046" gives .../patent/US9286046."""
    compact = re.sub(r"[\s,/-]", "", number or "").upper()
    match = re.fullmatch(r"([A-Z]{2})(\d{5,})([A-Z]\d?)?", compact)
    if not match or (match[1] == "US" and int(match[2]) >= US_GRANTED_LIMIT):
        return None
    return f"https://patents.google.com/patent/{compact}"


def _http(url: Any) -> str | None:
    return url if isinstance(url, str) and url.startswith(("http://", "https://")) else None


def _seconds(value: Any) -> str | None:
    if not isinstance(value, str) or "T" not in value:
        return None
    return re.sub(r"\.\d+(?=Z|[+-])", "", value)


def _text(value: Any) -> str | None:
    return " ".join(value.split()) if isinstance(value, str) and value.strip() else None


def _items(record: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """List entries of a scraped record; the scraper leaves nulls in some lists."""
    value = record.get(key)
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _accounts_on(registry: AccountRegistry, platform: str) -> dict[str, Any]:
    return {r.account.url.rstrip("/").lower(): r for r in registry.accounts.values()
            if r.account.platform == platform}


def _first_record(entry: dict[str, Any] | None) -> dict[str, Any] | None:
    records = (entry or {}).get("records") or []
    good = [r for r in records if not r.get("error") and not r.get("error_code")
            and not r.get("warning_code")]
    return good[0] if good else None


def _corroborated_link(url: str, person: Person, registry: AccountRegistry) -> bool:
    classified = classify_social_url(url) or other_profile(url)
    if classified and classified[0] == "github":
        login = classified[1].lower()
        return person.github == f"gh:{login}" or bool(
            registry.github_claims.get(person.id, {}).get(login, set()) - {"linkedin_profile"})
    if classified:
        account = registry.accounts.get(social_account_id(*classified))
        return bool(account and account.owner == person.id
                    and set(account.account.link_basis) - {"linkedin_profile"})
    site = registry.websites.get(website_id(url))
    return bool(site and site.owner == person.id
                and set(site.website.link_basis) - {"linkedin_profile"})


def fill_linkedin(raw: RawData, registry: AccountRegistry, people: dict[str, Person],
                  orgs: OrgIndex) -> dict[str, ProfileExtras]:
    """
    LinkedIn profile details. The public profile reliably gives the current company,
    and often an about section, education, honors, certifications, spoken languages,
    volunteering, projects and articles; the experience list is usually hidden.
    """
    extras: dict[str, ProfileExtras] = defaultdict(ProfileExtras)
    if not raw.has("brightdata/linkedin_profiles.json"):
        return extras
    data = raw.load("brightdata/linkedin_profiles.json")
    accounts = _accounts_on(registry, "linkedin")
    for input_url, entry in data.items():
        record = _first_record(entry)
        holder = accounts.get(input_url.rstrip("/").lower())
        if not record or not holder or not holder.owner.startswith("person:"):
            continue
        person = people.get(holder.owner)
        if person is None:
            continue
        account = holder.account
        source = raw.source("brightdata/linkedin_profiles.json", entry["snapshot_id"],
                            url=account.url)
        evidence = Evidence(url=account.url, observed_at=_seconds(record.get("timestamp")))
        account.display_name = _text(record.get("name"))
        account.headline = _text(record.get("position"))
        account.bio = (record.get("about") or "").strip() or None
        account.location = _text(record.get("location") or record.get("city"))
        account.followers = record.get("followers")
        account.connections = record.get("connections")
        if not record.get("default_avatar"):
            account.avatar_url = _http(record.get("avatar"))
        account.banner_url = _http(record.get("banner_image"))
        account.details_fetched = True
        account.sources.append(source)

        company = record.get("current_company") or {}
        name = _text(company.get("name") or record.get("current_company_name"))
        # The scraper sometimes fills the company with the headline ("AI @ GITHUB x MSFT /
        # … Top Influencer"); that names no organization.
        if name and (len(name) > 60 or any(m in name for m in ("|", " @ ", "×", " / "))):
            name = None
        if name and name.lower() not in orgs.none:
            org = orgs.ensure(name, "affiliation", source)
            if not any(a.organization == org.id and a.basis == "linkedin"
                       for a in person.affiliations):
                person.affiliations.append(Affiliation(
                    organization=org.id, title=headline_title(account.headline), current=True,
                    basis="linkedin", label=name, evidence=[evidence]))
            company_id = company.get("company_id") or record.get("current_company_company_id")
            if company_id and not str(company_id).isdigit():
                registry.add_social("linkedin", f"company/{company_id}", org.id,
                                    "linkedin_profile", source)

        # Bio links also advertise employers, products and other people's work.
        # Add provenance only when another source already ties the link to this owner.
        for item in _items(record, "bio_links"):
            url = _http(item.get("link"))
            if url and _corroborated_link(url, person, registry):
                registry.add_url(url, person.id, "linkedin_profile", source)

        found = extras[person.id]
        for item in _items(record, "experience"):
            org_name = _text(item.get("company") or item.get("subtitle")) or ""
            end = _text(item.get("end_date"))
            existing = orgs.get(org_name) if org_name else None
            found.experience.append(Position(
                organization=org_name or "Unknown",
                organization_ref=existing.id if existing else None,
                title=_text(item.get("title")), start=_text(item.get("start_date")), end=end,
                current=end is None or end.lower() == "present",
                description=(item.get("description") or "").strip() or None,
                evidence=evidence))
        for item in _items(record, "education"):
            school = _text(item.get("title"))
            if not school:
                continue
            existing = orgs.get(school)
            found.education.append(EducationEntry(
                school=school, school_ref=existing.id if existing else None,
                degree=_text(item.get("degree")), field_of_study=_text(item.get("field")),
                start_year=_text(item.get("start_year")), end_year=_text(item.get("end_year")),
                evidence=evidence))
        for item in _items(record, "publications"):
            if _text(item.get("title")):
                found.publications.append(Publication(
                    title=_text(item["title"]) or "", venue=_text(item.get("subtitle")),
                    date=_text(item.get("date")),
                    description=(item.get("description") or "").strip() or None,
                    url=_http(item.get("url") or item.get("link")), evidence=evidence))
        for item in _items(record, "patents"):
            if _text(item.get("title")):
                number = _text(item.get("patents_id"))
                found.patents.append(Patent(
                    title=_text(item["title"]) or "", number=number,
                    date=_text(item.get("date_issued")),
                    description=(item.get("description") or "").strip() or None,
                    url=patent_url(number), evidence=evidence))
        for item in _items(record, "honors_and_awards"):
            if _text(item.get("title")):
                found.credentials.append(Credential(
                    kind="honor", title=_text(item["title"]) or "",
                    issuer=_text(item.get("publication")), date=_text(item.get("date")),
                    description=(item.get("description") or "").strip() or None,
                    evidence=evidence))
        for item in _items(record, "certifications"):
            if _text(item.get("title")):
                issuer = _text(item.get("subtitle"))
                meta = _text(item.get("meta")) or ""
                issued, expires = (re.search(rf"{word} (\w+ \d{{4}})", meta)
                                   for word in ("Issued", "Expires"))
                credential_id = re.search(r"Credential ID (\S+)", meta)
                found.credentials.append(Credential(
                    kind="certification", title=_text(item["title"]) or "",
                    issuer=None if issuer == "-" else issuer,
                    date=issued[1] if issued else None, expires=expires[1] if expires else None,
                    credential_id=_text(str(item.get("credential_id") or "") or None)
                    or (credential_id[1] if credential_id else None),
                    url=_homepage(_http(item.get("credential_url"))), evidence=evidence))
        found.spoken_languages = [t for t in (_text(i.get("title"))
                                              for i in _items(record, "languages")) if t]
        for kind, key in (("volunteering", "volunteer_experience"), ("project", "projects"),
                          ("course", "courses"), ("organization", "organizations")):
            for item in _items(record, key):
                title = _text(item.get("title") or item.get("cause") or item.get("name"))
                if not title:
                    continue
                detail = " · ".join(t for t in (_text(item.get(k)) for k in (
                    "subtitle", "cause", "duration", "description", "info", "start_date",
                    "end_date", "meta")) if t and t not in {title, "-"})
                found.activities.append(Activity(
                    kind=kind,  # pyright: ignore[reportArgumentType]
                    title=title, detail=detail or None, evidence=evidence))
        for post in _items(record, "posts"):
            url = _http(post.get("link"))
            title = _text(post.get("title"))
            if url and title:
                found.writing.append(WritingItem(
                    title=title, url=url, published=_text(post.get("created_at")),
                    channel="linkedin", summary=_text(post.get("attribution"))))
    return extras


def fill_x(raw: RawData, registry: AccountRegistry,
           people: dict[str, Person] | None = None) -> None:
    """X profile details; the profile's own website link is an identity claim."""
    if not raw.has("brightdata/x_profiles.json"):
        return
    data = raw.load("brightdata/x_profiles.json")
    accounts = _accounts_on(registry, "x")
    for input_url, entry in data.items():
        record = _first_record(entry)
        holder = accounts.get(input_url.rstrip("/").lower())
        if not record or not holder:
            continue
        account = holder.account
        display_name = _text(record.get("profile_name") or record.get("name"))
        created_at = _seconds(record.get("date_joined"))
        person = (people or {}).get(holder.owner)
        if person and catalog_x_mismatch(account, person, display_name, created_at):
            registry.rejected_hashes.add(rejected_link_fingerprint(holder.owner, account.id))
            registry.accounts.pop(account.id, None)
            continue
        source = raw.source("brightdata/x_profiles.json", entry["snapshot_id"], url=account.url)
        account.display_name = display_name or account.display_name
        account.bio = (record.get("biography") or "").strip() or None
        account.location = _text(record.get("location"))
        account.website = _http(record.get("external_link"))
        account.followers = record.get("followers")
        account.following = record.get("following")
        account.posts_count = record.get("posts_count")
        account.verified = record.get("is_verified")
        account.avatar_url = _http(record.get("profile_image_link"))
        account.banner_url = _http(record.get("banner_image"))
        account.created_at = _seconds(record.get("date_joined"))
        account.details_fetched = True
        account.sources.append(source)
        if account.website:
            registry.add_url(account.website, holder.owner, "x_profile", source)


def fill_mastodon(raw: RawData, registry: AccountRegistry) -> None:
    """Mastodon profile details; links the server verified (rel=me) corroborate identity."""
    if not raw.has("mastodon/profiles.json"):
        return
    profiles = raw.load("mastodon/profiles.json")
    for holder in list(registry.accounts.values()):
        account = holder.account
        profile = profiles.get(account.handle.lower()) if account.platform == "mastodon" else None
        if not profile:
            continue
        source = raw.source("mastodon/profiles.json", account.handle, url=profile.get("url"))
        account.display_name = profile.get("display_name") or None
        account.bio = profile.get("bio") or None
        account.followers = profile.get("followers")
        account.following = profile.get("following")
        account.posts_count = profile.get("statuses")
        account.created_at = profile.get("created_at")
        account.avatar_url = _http(profile.get("avatar"))
        account.details_fetched = True
        account.sources.append(source)
        for item in profile.get("fields") or []:
            if item.get("verified_at") and _http(item.get("url")):
                registry.add_url(item["url"], holder.owner, "mastodon_verified", source)


def writing_from_feeds(raw: RawData, registry: AccountRegistry) -> dict[str, list[WritingItem]]:
    """Recent posts from each person's own website feeds, keyed by owner."""
    if not raw.has("feeds/feeds.json") or not raw.has("websites/homepages.json"):
        return {}
    feeds = raw.load("feeds/feeds.json")
    owners_of_feed: dict[str, set[str]] = defaultdict(set)
    for url, page in raw.load("websites/homepages.json").items():
        site = registry.websites.get(website_id(url if "://" in url else f"https://{url}"))
        if site:
            for feed in page.get("feeds") or []:
                # WordPress comment feeds (`/comments/feed/`, `?feed=comments-rss2`) hold
                # other people's comments, not the owner's writing.
                if "comments" not in feed.lower():
                    owners_of_feed[feed].add(site.owner)
    writing: dict[str, list[WritingItem]] = defaultdict(list)
    for feed_url, result in feeds.items():
        owners = owners_of_feed.get(feed_url, set())
        if len(owners) != 1 or result.get("error"):
            continue
        owner = next(iter(owners))
        for item in result.get("items") or []:
            if _http(item.get("url")) and _text(item.get("title")):
                writing[owner].append(WritingItem(
                    title=_text(item["title"]) or "", url=item["url"],
                    published=item.get("published"), channel="blog"))
    return writing


def hashtag_records(raw: RawData) -> list[dict[str, Any]]:
    """
    People who posted with a GitHub Universe hashtag and said they will be there, as
    importable self_reported attendees. A tagged post that does not say so adds no one:
    using a hashtag is not attending, and some posts say the opposite. Bot accounts are
    skipped.
    """
    if not raw.has("mastodon/hashtags.json"):
        return []
    by_account: dict[str, dict[str, Any]] = {}
    for timeline in raw.load("mastodon/hashtags.json").values():
        for post in timeline.get("posts") or []:
            account = post.get("account") or {}
            acct = (account.get("acct") or "").lower()
            if not acct or account.get("bot"):
                continue
            text = post.get("text") or ""
            record = by_account.setdefault(acct, {
                "source": "mastodon_hashtag",
                "snapshot": "mastodon/hashtags.json",
                "record_id": post.get("url") or post.get("id"),
                # Strip custom emoji shortcodes (":verified:") from display names.
                "name": " ".join(re.sub(r":[A-Za-z0-9_]+:", " ",
                                        account.get("display_name") or "").split())
                or acct.split("@")[0],
                # A hashtag poster's profile text is not an event bio, and it is untrusted
                # (one tagged profile carries a prompt-injection line), so it stays off
                # the person.
                "accounts": {"mastodon": acct},
                "participation": {"role": "attendee", "status": "candidate", "evidence": []},
                "interests": [],
                "inclusion_basis": "public_self_report",
            })
            evidence = {"url": post.get("url"), "quote": text[:QUOTE_LIMIT],
                        "observed_at": post.get("created_at")}
            if evidence not in record["participation"]["evidence"]:
                record["participation"]["evidence"].append(evidence)
            if says_attending(text):
                record["participation"]["status"] = "self_reported"
    return [r for r in by_account.values() if r["participation"]["status"] == "self_reported"]


# Words that mark a post as being about work: software, building, shipping and talking
# about it. A post with none of them is treated as personal and not shown.
WORK = re.compile(
    r"\b(?:AI|LLMs?|agents?|agentic|copilot|github|git|code|coding|coder|developers?|devs?"
    r"|engineer(?:s|ing)?|software|open[ -]?source|OSS|APIs?|SDKs?|CLI|repos?|repository"
    r"|releases?|released|launch(?:ed|es|ing)?|ship(?:ped|ping|s)?|deploy\w*|cloud|kubernetes"
    r"|k8s|docker|containers?|python|rust|javascript|typescript|java|golang|\.NET|security"
    r"|vulnerabilit\w+|devops|platform|infrastructure|database|models?|machine learning"
    r"|ML|product|startup|talks?|keynote|conference|meetup|workshop|webinar|podcast"
    r"|livestream|blog|newsletter|article|paper|docs|documentation|tutorial|course|demo"
    r"|hackathon|build(?:ing|s)?|features?|bugs?|pull requests?|PRs?|commits?|programming"
    r"|tech|data|automation|testing|accessibility|a11y|design system|UX|web|app|apps"
    r"|framework|library|compiler|terminal|editor|IDE|VS ?Code|Universe)\b",
    re.IGNORECASE)
UNIVERSE_MENTION = re.compile(r"GitHub\s?Universe|#GHUniverse", re.IGNORECASE)
# Posts about this edition, not past ones.
UNIVERSE_WINDOW = ("2026-08-01", "2026-11-30")


def x_posts(raw: RawData, registry: AccountRegistry
            ) -> tuple[dict[str, list[WritingItem]], dict[str, list[Evidence]]]:
    """
    From each X profile's recent posts: the person's latest original posts (not replies
    or reposts) as recent writing, and their posts about this year's Universe as
    participation evidence.
    """
    writing: dict[str, list[WritingItem]] = defaultdict(list)
    universe: dict[str, list[Evidence]] = defaultdict(list)
    if not raw.has("brightdata/x_profiles.json"):
        return writing, universe
    accounts = _accounts_on(registry, "x")
    for input_url, entry in raw.load("brightdata/x_profiles.json").items():
        record = _first_record(entry)
        holder = accounts.get(input_url.rstrip("/").lower())
        if not record or not holder:
            continue
        posts = sorted(record.get("posts") or [], key=lambda p: p.get("date_posted") or "",
                       reverse=True)
        for post in posts:
            text = (post.get("description") or "").strip()
            url = _http(post.get("post_url"))
            if not text or not url:
                continue
            published = _seconds(post.get("date_posted"))
            day = (published or "")[:10]
            if UNIVERSE_MENTION.search(text) and UNIVERSE_WINDOW[0] <= day <= UNIVERSE_WINDOW[1]:
                universe[holder.owner].append(
                    Evidence(url=url, quote=text[:QUOTE_LIMIT], observed_at=published))
            # Recent writing is the person's own words about their work: no replies, no
            # posts that tag other people, nothing personal and nothing that states a
            # sensitive attribute.
            own = not re.search(r"(?<![\w.])@\w", text) and not text.startswith("RT ")
            if (own and WORK.search(text) and not is_sensitive(text)
                    and len(writing[holder.owner]) < MAX_WRITING):
                writing[holder.owner].append(WritingItem(
                    title=text[:QUOTE_LIMIT], url=url, published=published, channel="x"))
    return writing, universe


def headline_title(headline: str | None) -> str | None:
    """
    The job title in a LinkedIn headline: "Senior Software Engineer @GitHub | Speaker"
    gives "Senior Software Engineer".
    """
    if not headline:
        return None
    first = re.split(r"\s+[|•·]\s+", headline)[0]
    return re.sub(r"\s+(?:@|at\s+@?)\S.*$", "", first).strip() or None


def _homepage(url: str | None) -> str | None:
    """A company's website without campaign tracking parameters."""
    if not url:
        return None
    base, _, query = url.partition("?")
    kept = "&".join(p for p in query.split("&") if p and not p.startswith(("utm_", "trk")))
    return f"{base}?{kept}" if kept else base


@dataclass
class OrgDetails:
    descriptions: list[OrgDescription] = field(default_factory=list)
    tagline: str | None = None
    industry: str | None = None
    size: str | None = None
    headquarters: str | None = None
    founded: str | None = None
    specialties: list[str] = field(default_factory=list)
    logo_url: str | None = None
    website: str | None = None
    locations: list[str] = field(default_factory=list)
    updates: list[OrgUpdate] = field(default_factory=list)
    affiliated: list[AffiliatedPage] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)

    def add(self, text: Any, basis: str) -> None:
        cleaned = (text or "").strip() if isinstance(text, str) else ""
        if cleaned and all(d.text != cleaned for d in self.descriptions):
            self.descriptions.append(OrgDescription(
                text=cleaned, basis=basis))  # pyright: ignore[reportArgumentType]


def _join(value: Any) -> str | None:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if v) or None
    return _text(value) if isinstance(value, str) else (str(value) if value else None)


def organization_details(raw: RawData, records: dict[str, Any], owners: dict[str, Any],
                         registry: AccountRegistry) -> dict[str, OrgDetails]:
    """
    What each organization says about itself: its LinkedIn company page, its sponsor
    listing, its GitHub organization and its homepage, in that order of preference.
    `records` maps organization keys to the build's organization records.
    """
    details: dict[str, OrgDetails] = defaultdict(OrgDetails)
    companies = (raw.load("brightdata/linkedin_companies.json")
                 if raw.has("brightdata/linkedin_companies.json") else {})
    accounts = _accounts_on(registry, "linkedin")
    candidates: dict[str, list[tuple[str, Any, dict[str, Any]]]] = defaultdict(list)
    for input_url, entry in sorted(companies.items()):
        holder = accounts.get(input_url.rstrip("/").lower())
        record = _first_record(entry)
        if not holder or not record or not holder.owner.startswith("org:"):
            continue
        organization = records.get(holder.owner.removeprefix("org:"))
        node = owners.get((organization.github_login or "").lower()) if organization else None
        expected = registrable_domain(organization.website or (node or {}).get("websiteUrl")
                                      or "") if organization else None
        actual = registrable_domain(record.get("website") or "")
        if expected and actual and expected != actual:
            registry.rejected_hashes.add(
                rejected_link_fingerprint(holder.owner, holder.account.id))
            registry.accounts.pop(holder.account.id, None)
            continue
        candidates[holder.owner].append((input_url, holder, record))
    selected = set()
    for owner, choices in candidates.items():
        organization = records.get(owner.removeprefix("org:"))
        pin = organization.linkedin if organization else None
        pinned = [c for c in choices if c[1].account.handle.lower() == f"company/{pin}".lower()]
        chosen = (pinned[0] if len(pinned) == 1 else None) if pin else (
            choices[0] if len(choices) == 1 else None)
        for input_url, holder, _ in choices:
            if chosen is not None and holder is chosen[1]:
                selected.add(input_url)
            else:
                registry.rejected_hashes.add(
                    rejected_link_fingerprint(holder.owner, holder.account.id))
                registry.accounts.pop(holder.account.id, None)
    for input_url, entry in companies.items():
        if input_url not in selected:
            continue
        record = _first_record(entry)
        holder = accounts.get(input_url.rstrip("/").lower())
        if not record or not holder or not holder.owner.startswith("org:"):
            continue
        found = details[holder.owner]
        found.add(record.get("about") or record.get("description"), "linkedin")
        found.tagline = _text(record.get("slogan"))
        found.industry = _join(record.get("industries"))
        size = _join(record.get("company_size"))
        found.size = f"LinkedIn size range: {size}" if size else None
        found.headquarters = _join(record.get("headquarters"))
        found.founded = _join(record.get("founded"))
        specialties = record.get("specialties")
        if isinstance(specialties, str):
            # "Security, Monitoring, and Observability": drop the list's final "and".
            specialties = [s.strip().removeprefix("and ").strip() for s in specialties.split(",")]
        found.specialties = [s for s in specialties or [] if isinstance(s, str) and s]
        found.logo_url = _http(record.get("logo")) or _http(record.get("image"))
        found.locations = [t for t in (_text(x) for x in record.get("formatted_locations") or [])
                           if t]
        posts = [u for u in record.get("updates") or [] if isinstance(u, dict)
                 and (u.get("text") or "").strip()]
        posts.sort(key=lambda u: u.get("date") or "", reverse=True)
        found.updates = [OrgUpdate(
            text=u["text"].strip(), date=_seconds(u.get("date")), url=_http(u.get("post_url")),
            likes=u.get("likes_count") if isinstance(u.get("likes_count"), int) else None)
            for u in posts[:ORG_UPDATES]]
        for page in record.get("affiliated") or []:
            if not isinstance(page, dict) or not _text(page.get("title")):
                continue
            url = _http(page.get("Links") or page.get("link"))
            url = url.split("?")[0] if url else None
            classified = classify_social_url(url) if url else None
            same = registry.accounts.get(social_account_id(*classified)) if classified else None
            found.affiliated.append(AffiliatedPage(
                name=_text(page["title"]) or "", industry=_text(page.get("subtitle")), url=url,
                organization=same.owner if same and same.owner.startswith("org:")
                and same.owner != holder.owner else None))
        account = holder.account
        account.display_name = _text(record.get("name"))
        account.bio = (record.get("about") or "").strip() or None
        account.followers = record.get("followers")
        account.website = _http(record.get("website"))
        found.website = _homepage(account.website)
        account.avatar_url = found.logo_url
        account.details_fetched = True
        source = raw.source("brightdata/linkedin_companies.json", entry["snapshot_id"],
                            url=account.url)
        account.sources.append(source)
        found.sources.append(source)

    homepages = (raw.load("websites/org-homepages.json")
                 if raw.has("websites/org-homepages.json") else {})
    for key, record in records.items():
        org_id = f"org:{key}"
        found = details[org_id]
        if record.sponsorship and record.sponsorship.summary:
            found.add(record.sponsorship.summary, "sponsor_listing")
        node = owners.get(record.github_login.lower()) if record.github_login else None
        if node:
            found.add(node.get("description"), "github")
            found.website = found.website or _homepage(_http(node.get("websiteUrl")))
        page = homepages.get(record.website) if record.website else None
        if page and page.get("status") == 200:
            found.add(page.get("description"), "website")
            found.logo_url = found.logo_url or _http((page.get("og") or {}).get("image"))
            found.sources.append(raw.source("websites/org-homepages.json", record.website,
                                            url=page.get("final_url") or record.website))
    return details
