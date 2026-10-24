"""
People, their accounts and websites, and their developed profiles.

Three pieces, used by the build in this order:

- `AccountRegistry` turns every sighting of an account or website into one entity with a
  stable ID and the set of ways it was tied to its owner (`link_basis`). An account two
  owners claim is kept for the first and logged, never silently reassigned.
- `PeopleIndex` resolves identity across sources. People merge when any account key
  matches (GitHub, X, LinkedIn, Bluesky, website); a bare name match merges only when the
  new record also claims to speak, because two attendees can share a name.
- `build_profile` assembles a person's developed profile from what the knowledge base
  already knows, citing evidence for every claim and listing what is still unknown.
"""

from __future__ import annotations

import hashlib
import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from universe_kb.bluesky import normalize_handle
from universe_kb.ids import registrable_domain, slugify
from universe_kb.models import (
    Claim,
    Evidence,
    OpenSourceWork,
    Person,
    Profile,
    Repository,
    Session,
    SocialAccount,
    Source,
    Website,
)
from universe_kb.policy import EXCLUDED_PLATFORMS, excluded_platform, exclusion_fingerprint
from universe_kb.web import classify_social_url

log = logging.getLogger(__name__)

# GitHub's `socialAccounts.provider` values, mapped to our platforms.
GITHUB_PROVIDERS = {
    "TWITTER": "x", "LINKEDIN": "linkedin", "BLUESKY": "bluesky", "MASTODON": "mastodon",
    "YOUTUBE": "youtube", "INSTAGRAM": "instagram", "THREADS": "threads",
}
# Domains that are never a person's own website.
NOT_PERSONAL_DOMAINS = {
    "github.com", "microsoft.com", "linkedin.com", "x.com", "twitter.com", "facebook.com",
    "youtube.com", "instagram.com", "threads.net", "threads.com", "tiktok.com", "google.com",
    "bsky.app", "reddit.com", "linktr.ee",
    # Feed readers: a subscription link names someone else's feed, not a website.
    "feedly.com", "inoreader.com",
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    # The conference's own site, which speakers link to announce a talk.
    "githubuniverse.com",
}
BLOG_HOSTS = {"medium.com", "dev.to", "hashnode.dev", "substack.com", "blogspot.com"}
# Profile pages on sites without a dedicated platform; they are accounts, not websites.
OTHER_PROFILE_HOSTS = {"twitch.tv", "news.ycombinator.com", "credly.com", "dribbble.com",
                       "behance.net", "stackoverflow.com", "kaggle.com", "huggingface.co",
                       "npmjs.com", "pypi.org", "sessionize.com", "speakerdeck.com",
                       "slideshare.net", "about.me"}
RECOGNITIONS = {
    "Microsoft MVP": r"\bMicrosoft MVP\b|\b\d+x MVP\b|\bMVP\b(?=.{0,40}\bMicrosoft\b)",
    "GitHub Star": r"\bGitHub Stars?\b",
    "Google Developer Expert": r"\bGoogle Developer Expert\b|\bGDE\b",
    "AWS Hero": r"\bAWS (?:Community |Serverless |Container |DevTools )?Hero\b",
    "Docker Captain": r"\bDocker Captain\b",
    "Java Champion": r"\bJava Champion\b",
    "GitHub Campus Expert": r"\bGitHub Campus Expert\b",
    "Microsoft Regional Director": r"\bRegional Director\b",
    "CNCF Ambassador": r"\bCNCF Ambassador\b",
}
MAX_LANGUAGES = 5
# Other query keys can select distinct records and must remain part of identity.
TRACKING_QUERY_KEYS = {"gclid", "fbclid", "msclkid"}


def _tracking_query_key(key: str) -> bool:
    return key.casefold().startswith("utm_") or key.casefold() in TRACKING_QUERY_KEYS


def canonical_website_url(url: str) -> str:
    """Remove known campaign parameters and fragments, preserving query-addressed records."""
    parts = urlparse(url if "://" in url else f"https://{url}")
    # Some sources start a tracking parameter with a second question mark.
    query = re.sub(r"\?(?=([^?&#=]+)=)",
                   lambda match: "&" if _tracking_query_key(match[1]) else "?", parts.query)
    query = urlencode([(key, value) for key, value in parse_qsl(query, keep_blank_values=True)
                       if not _tracking_query_key(key)])
    return urlunparse(parts._replace(query=query, fragment=""))


def _id_part(text: str) -> str:
    return re.sub(r"[^a-z0-9._@+/-]+", "-", text.lower()).strip("-./") or "x"


def social_account_id(platform: str, handle: str) -> str:
    return f"acct:{platform}/{_id_part(handle)}"


def website_id(url: str) -> str:
    parts = urlparse(canonical_website_url(url))
    host = (parts.hostname or "").removeprefix("www.")
    # Hash meaningful queries so case and punctuation cannot collapse distinct records.
    query = f"/query-{hashlib.sha256(parts.query.encode()).hexdigest()}" if parts.query else ""
    return f"site:{_id_part(host + parts.path.rstrip('/'))}{query}"


def other_profile(url: str) -> tuple[str, str] | None:
    """A profile page on a site in `OTHER_PROFILE_HOSTS`, as ("other", host/path)."""
    parts = urlparse(url if "://" in url else f"https://{url}")
    host = (parts.hostname or "").removeprefix("www.")
    if host not in OTHER_PROFILE_HOSTS or (parts.path.strip("/") == "" and not parts.query):
        return None
    query = f"?{parts.query}" if parts.query else ""
    return "other", f"{host}{parts.path.rstrip('/')}{query}"


def canonical_profile_url(platform: str, handle: str) -> str:
    bases = {
        "x": "https://x.com/{}", "linkedin": "https://www.linkedin.com/{}",
        "bluesky": "https://bsky.app/profile/{}", "youtube": "https://www.youtube.com/{}",
        "instagram": "https://www.instagram.com/{}", "threads": "https://www.threads.net/@{}",
    }
    if platform == "mastodon" and "@" in handle:
        user, _, host = handle.partition("@")
        return f"https://{host}/@{user}"
    return bases.get(platform, "https://{}").format(handle)


def website_kind(url: str, owner: str) -> str:
    host = (urlparse(url).hostname or "").removeprefix("www.")
    if any(host == h or host.endswith(f".{h}") for h in BLOG_HOSTS) or "blog" in url.lower():
        return "blog"
    return "personal" if owner.startswith("person:") else "company"


def rejected_link_fingerprint(owner: str, account: str) -> str:
    """A pseudonymous owner/link-pair key; known pairs can be dictionary-tested."""
    return exclusion_fingerprint(f"{owner.strip().casefold()}\0{account.strip().casefold()}")


def source_record_fingerprint(snapshot: str, record_id: str) -> str:
    """A bounded source-record rejection key, independent of claimed person identity."""
    relative = snapshot.strip().removeprefix("raw/").strip("/")
    return exclusion_fingerprint(f"catalog:{relative}\0{record_id.strip()}")


def filter_catalog_people(items: list[dict[str, Any]], snapshot: str,
                          rejected_sources: set[str]) -> None:
    """
    Remove unreviewed source records before identity, affiliation or media extraction.
    A rejection applies only to this catalog record, including future snapshots of it;
    independent records about either person remain available to establish identity.
    """
    if any(not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
           for digest in rejected_sources):
        raise ValueError("Rejected sources must be lowercase sha256 fingerprints")
    for item in items:
        item["participants"] = [p for p in item.get("participants") or []
                                if not p.get("testRecord")
                                and source_record_fingerprint(snapshot, p["userRef"])
                                not in rejected_sources]


def catalog_x_mismatch(account: SocialAccount, person: Person,
                       display_name: str | None, created_at: str | None) -> bool:
    """
    A catalog-only X link cannot establish identity after the handle is reassigned.
    Independent current profile links take precedence over this conservative check.
    """
    if account.platform != "x" or set(account.link_basis) != {"event_listing"}:
        return False
    years = []
    for source in account.sources:
        match = re.search(r"/editions/universe(\d{2})/", source.snapshot or "")
        if match:
            years.append(2000 + int(match.group(1)))
        elif "rainfocus/" in (source.snapshot or ""):
            match = re.search(r"20\d{2}", person.listed_for or "")
            if match:
                years.append(int(match.group()))
    created = re.search(r"20\d{2}", created_at or "")
    if created and years and int(created.group()) > max(years):
        return True
    expected = {t for t in slugify(person.name).split("-") if len(t) > 1}
    observed = {t for t in slugify(display_name or "").split("-") if len(t) > 1}
    return bool(expected and observed and not expected & observed)


def _web_url(url: str) -> str | None:
    value = url.strip()
    if not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", value):
        value = f"https://{value}"
    try:
        parts = urlparse(value)
        _ = parts.port
    except ValueError:
        return None
    if (parts.scheme not in {"http", "https"} or not parts.hostname
            or parts.username is not None or any(ch.isspace() for ch in value)):
        return None
    return value


# --- Accounts and websites -------------------------------------------------------------


@dataclass
class AccountRecord:
    account: SocialAccount
    owner: str


@dataclass
class WebsiteRecord:
    website: Website
    owner: str


@dataclass
class AccountRegistry:
    accounts: dict[str, AccountRecord] = field(default_factory=dict)
    websites: dict[str, WebsiteRecord] = field(default_factory=dict)
    conflicts: list[str] = field(default_factory=list)
    # (owner, account or website ID) links that curation says are wrong.
    rejected: set[tuple[str, str]] = field(default_factory=set)
    rejected_hashes: set[str] = field(default_factory=set)
    # GitHub logins an owner links from another profile, with each link's basis. The
    # build adopts one as the owner's GitHub account when the listing gave none.
    github_claims: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    # Accounts left out because their platform is personal by default, by platform.
    excluded: dict[str, set[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if any(not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
               for digest in self.rejected_hashes):
            raise ValueError("Rejected link pairs must be lowercase sha256 fingerprints")

    def add_social(self, platform: str, handle: str, owner: str, basis: str,
                   source: Source, url: str | None = None) -> str | None:
        account_id = social_account_id(platform, handle)
        personal = (platform if platform in EXCLUDED_PLATFORMS
                    else excluded_platform(url or canonical_profile_url(platform, handle)))
        if personal:
            self.excluded.setdefault(personal, set()).add(account_id)
            return None
        if ((owner, account_id) in self.rejected
                or rejected_link_fingerprint(owner, account_id) in self.rejected_hashes):
            return None
        record = self.accounts.get(account_id)
        if record is None:
            account = SocialAccount(
                id=account_id, platform=platform,  # pyright: ignore[reportArgumentType]
                handle=handle, url=url or canonical_profile_url(platform, handle),
                owner=owner, link_basis=[basis],  # pyright: ignore[reportArgumentType]
                sources=[source],
            )
            self.accounts[account_id] = AccountRecord(account, owner)
            return account_id
        if record.owner != owner:
            self.conflicts.append(f"{account_id} claimed by {record.owner} and {owner}")
            log.warning("account %s claimed by %s and %s; keeping the first",
                        account_id, record.owner, owner)
            return None
        if basis not in record.account.link_basis:
            record.account.link_basis.append(basis)  # pyright: ignore[reportArgumentType]
        if source not in record.account.sources:
            record.account.sources.append(source)
        return account_id

    def claim_github(self, login: str, owner: str, basis: str) -> None:
        self.github_claims.setdefault(owner, {}).setdefault(login.lower(), set()).add(basis)

    def github_claimants(self) -> dict[str, set[str]]:
        """All claimants, including claims rejected earlier in this build."""
        claimants: dict[str, set[str]] = {}
        for owner, claims in self.github_claims.items():
            for login in claims:
                claimants.setdefault(login.lower(), set()).add(owner)
        return claimants

    def add_url(self, url: str, owner: str, basis: str, source: Source) -> str | None:
        """Add a URL as an account if it is a profile page, otherwise as a website."""
        normalized = _web_url(url)
        if normalized is None:
            return None
        url = normalized
        classified = classify_social_url(url) or other_profile(url)
        personal = excluded_platform(url)
        if personal:
            key = social_account_id(*classified) if classified else url.strip().lower()
            self.excluded.setdefault(personal, set()).add(key)
            return None
        if classified:
            platform, handle = classified
            if platform == "github":
                self.claim_github(handle, owner, basis)
                return None
            full = url if "://" in url else f"https://{url}"
            return self.add_social(platform, handle, owner, basis, source,
                                   url=full if platform == "other" else None)
        return self.add_website(url, owner, basis, source)

    def add_website(self, url: str, owner: str, basis: str, source: Source) -> str | None:
        normalized = _web_url(url)
        if normalized is None:
            return None
        url = canonical_website_url(normalized)
        # "https://ada@example.com/" is an email address turned into a link, not a site.
        if registrable_domain(url) in NOT_PERSONAL_DOMAINS or "@" in urlparse(url).netloc:
            return None
        site_id = website_id(url)
        if ((owner, site_id) in self.rejected
                or rejected_link_fingerprint(owner, site_id) in self.rejected_hashes):
            return None
        record = self.websites.get(site_id)
        if record is None:
            website = Website(
                id=site_id, url=url,
                kind=website_kind(url, owner),  # pyright: ignore[reportArgumentType]
                owner=owner, link_basis=[basis],  # pyright: ignore[reportArgumentType]
                fetch_status="not_fetched", sources=[source],
            )
            self.websites[site_id] = WebsiteRecord(website, owner)
            return site_id
        if record.owner != owner:
            self.conflicts.append(f"{site_id} claimed by {record.owner} and {owner}")
            return None
        if basis not in record.website.link_basis:
            record.website.link_basis.append(basis)  # pyright: ignore[reportArgumentType]
        return site_id

    def owned_by(self, owner: str) -> tuple[list[str], list[str]]:
        accounts = sorted(i for i, r in self.accounts.items() if r.owner == owner)
        websites = sorted(i for i, r in self.websites.items() if r.owner == owner)
        return accounts, websites


def github_social_links(node: dict[str, Any]) -> list[tuple[str, str]]:
    """(platform-or-'website', url) pairs a GitHub user profile declares."""
    links = []
    for social in (node.get("socialAccounts") or {}).get("nodes") or []:
        provider, url = social.get("provider"), social.get("url")
        if not url:
            continue
        links.append((GITHUB_PROVIDERS.get(provider, "website"), url))
    if node.get("twitterUsername"):
        links.append(("x", f"https://x.com/{node['twitterUsername']}"))
    if node.get("websiteUrl"):
        links.append(("website", node["websiteUrl"]))
    return links


def bluesky_handle(raw: str | None) -> str | None:
    handle, _assumed = normalize_handle(raw)
    return handle


# --- Identity --------------------------------------------------------------------------


def identity_keys(accounts: dict[str, str | None]) -> set[str]:
    """Keys that identify a person across sources, from platform -> handle or URL."""
    keys = set()
    for platform, value in accounts.items():
        if not value:
            continue
        if platform == "website":
            profile = other_profile(value)
            if profile:
                keys.add(social_account_id(*profile))
            else:
                keys.add(website_id(value if "://" in value else f"https://{value}"))
            continue
        if platform == "bluesky":
            handle = bluesky_handle(value)
            if handle:
                keys.add(social_account_id("bluesky", handle))
            continue
        if platform == "github":
            keys.add(f"gh:{value.lower()}")
            continue
        url = value if "://" in value else canonical_profile_url(platform, value.lstrip("@"))
        classified = classify_social_url(url)
        if classified:
            keys.add(social_account_id(*classified))
    return keys


@dataclass
class PeopleIndex:
    by_key: dict[str, set[str]] = field(default_factory=dict)
    by_name: dict[str, list[str]] = field(default_factory=dict)

    names: dict[str, str] = field(default_factory=dict)

    def register(self, person_id: str, name: str, keys: set[str]) -> None:
        """Safe to call again as a person gains accounts; each person is listed once."""
        for key in keys:
            self.by_key.setdefault(key, set()).add(person_id)
            for handle in handle_keys(key):
                self.by_key.setdefault(handle, set()).add(person_id)
        self.names[person_id] = name
        named = self.by_name.setdefault(slugify(name), [])
        if person_id not in named:
            named.append(person_id)

    def resolve(self, name: str, keys: set[str], *, claims_speaking: bool) -> str | None:
        matched = {person for key in keys for person in self.by_key.get(key, set())}
        if matched:
            return next(iter(matched)) if len(matched) == 1 else None
        # The same handle on another platform is the same person only when the names
        # agree too. Keep all owners so registration order cannot hide a collision.
        matched = {person for key in keys for handle in handle_keys(key)
                   for person in self.by_key.get(handle, set())
                   if names_compatible(name, self.names.get(person, ""))}
        if matched:
            return next(iter(matched)) if len(matched) == 1 else None
        named = self.by_name.get(slugify(name), [])
        if claims_speaking and len(named) == 1:
            return named[0]
        return None


def handle_keys(key: str) -> list[str]:
    """`handle:<user>` keys for an account key's user part, for cross-platform matching."""
    platform, _, rest = key.partition(":")
    if platform == "gh":
        return [f"handle:{rest}"]
    if platform != "acct":
        return []
    kind, _, handle = rest.partition("/")
    if kind in {"x", "instagram", "threads"}:
        return [f"handle:{handle}"]
    if kind == "mastodon":
        return [f"handle:{handle.split('@')[0]}"]
    if kind == "bluesky":
        # A custom-domain handle ("martin.social") names a domain, not a user name.
        user, _, domain = handle.partition(".")
        return [f"handle:{user}"] if domain == "bsky.social" else []
    return []


def _name_key(name: str) -> str:
    key = slugify(name).replace("-", "")
    # slugify returns "x" when nothing ASCII is left ("李雷"); compare the characters.
    return key if key != "x" or "x" in name.lower() else "".join(name.casefold().split())


def names_compatible(first: str, second: str) -> bool:
    a, b = _name_key(first), _name_key(second)
    return bool(a) and (a == b or (len(a) >= 5 and (a in b or b in a)))


# --- Profiles --------------------------------------------------------------------------


def _quote(text: str, match: re.Match[str], width: int = 80) -> str:
    start = max(0, text.rfind(".", 0, match.start()) + 1)
    end = text.find(".", match.end())
    sentence = text[start: end + 1 if end != -1 else len(text)].strip()
    return sentence if len(sentence) <= 2 * width else text[max(0, match.start() - width):
                                                          match.end() + width].strip()


def recognition_claims(texts: list[tuple[str, str, str | None]]) -> list[Claim]:
    """Recognition programs named in text, from (basis, text, url) triples."""
    claims: dict[str, Claim] = {}
    for basis, text, url in texts:
        for label, pattern in RECOGNITIONS.items():
            match = re.search(pattern, text)
            # "former Microsoft MVP", "MVP (retired)" and "Ambassador alum" are history.
            if match and (re.search(r"\b(former|formerly|ex-|past)\s*$",
                                    text[:match.start()][-20:], re.IGNORECASE)
                          or re.match(r"\s*\(?(retired|alum|alumni|alumna|emeritus)\b",
                                      text[match.end():match.end() + 15], re.IGNORECASE)):
                continue
            if match and label not in claims:
                claims[label] = Claim(
                    label=label, basis=basis,  # pyright: ignore[reportArgumentType]
                    confidence="high" if basis in {"bio", "github_profile"} else "medium",
                    evidence=[Evidence(url=url, quote=_quote(text, match))])
    return list(claims.values())


def build_profile(
    person: Person,
    sessions: dict[str, Session],
    term_labels: dict[str, str],
    software_names: dict[str, str],
    product_software: dict[str, str],
    github_node: dict[str, Any] | None,
    repositories: dict[str, Repository],
    bluesky: dict[str, Any] | None,
    org_names: dict[str, str],
    sources: list[Source],
    detailed: frozenset[str] = frozenset(),
) -> Profile:
    """
    A person's developed profile. `detailed` names the platforms whose account details
    were collected; an account without them is a `*_details` gap.
    """
    talks = [s.session for s in person.sessions]
    my_sessions = [sessions[t] for t in talks if t in sessions]

    topic_sessions: dict[str, list[str]] = {}
    product_sessions: dict[str, list[str]] = {}
    for session in my_sessions:
        for topic in session.facets.topics:
            topic_sessions.setdefault(topic, []).append(session.id)
        for product in session.facets.products:
            product_sessions.setdefault(product, []).append(session.id)
    expertise = [
        Claim(label=term_labels.get(term, term), target=term, basis="session_facets",
              confidence="high" if len(ids) > 1 else "medium",
              evidence=[Evidence(ref=i) for i in ids])
        for term, ids in sorted(topic_sessions.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]

    technologies: dict[str, Claim] = {}
    for mention in person.mentions:
        if mention.target.startswith("software:"):
            technologies[mention.target] = Claim(
                label=software_names.get(mention.target, mention.text), target=mention.target,
                basis="bio", confidence="high",
                evidence=[Evidence(ref=person.id, quote=mention.text)])
    for session in my_sessions:
        for mention in session.mentions:
            if mention.target.startswith("software:") and mention.target not in technologies:
                technologies[mention.target] = Claim(
                    label=software_names.get(mention.target, mention.text),
                    target=mention.target, basis="session_text", confidence="medium",
                    evidence=[Evidence(ref=session.id, quote=mention.text)])
    for product, ids in product_sessions.items():
        target = product_software.get(product)
        if target and target not in technologies:
            technologies[target] = Claim(
                label=software_names.get(target, term_labels.get(product, product)),
                target=target, basis="session_facets", confidence="medium",
                evidence=[Evidence(ref=i) for i in ids])

    own_repos = [repositories[r] for r in _person_repos(github_node) if r in repositories]
    owner_login = ((github_node or {}).get("login") or "").lower()
    languages = Counter(r.primary_language for r in own_repos
                        if r.primary_language and r.owner_login.lower() == owner_login)
    programming_languages = [
        Claim(label=language, basis="github_repositories",
              confidence="high" if count > 1 else "medium",
              evidence=[Evidence(ref=r.id) for r in own_repos if r.primary_language == language])
        for language, count in languages.most_common(MAX_LANGUAGES)
    ]
    login = ((github_node or {}).get("login") or "").lower()
    # A pinned repository can be someone else's; only owned ones are "owner".
    open_source = [
        OpenSourceWork(repository=r.id,
                       relation="owner" if r.owner_login.lower() == login else "pinned",
                       stars=r.stars, primary_language=r.primary_language)
        for r in sorted(own_repos, key=lambda r: -r.stars)
    ]
    contributed = [repositories[r] for r in _contributed(github_node) if r in repositories]
    open_source += [
        OpenSourceWork(repository=r.id, relation="contributor", stars=r.stars,
                       primary_language=r.primary_language)
        for r in contributed if r.id not in {w.repository for w in open_source}
    ]

    texts: list[tuple[str, str, str | None]] = []
    if person.bio:
        texts.append(("bio", person.bio, None))
    if github_node and github_node.get("bio"):
        texts.append(("github_profile", github_node["bio"], github_node.get("url")))
    if bluesky and bluesky.get("description"):
        texts.append(("bluesky_profile", bluesky["description"], None))
    recognitions = recognition_claims(texts)

    current = [a for a in person.affiliations if a.current]
    seen_roles: set[str] = set()
    current_roles = []
    for affiliation in current:
        org = org_names.get(affiliation.organization, affiliation.organization)
        line = f"{affiliation.title} at {org}" if affiliation.title else org
        if org not in seen_roles:
            seen_roles.add(org)
            current_roles.append(line)
    headline = current_roles[0] if current_roles else (
        (github_node or {}).get("bio") or (bluesky or {}).get("description") or None)

    platforms = {a.split(":", 1)[1].split("/", 1)[0] for a in person.accounts
                 if a.startswith("acct:")}
    gaps = [label for label, missing in (
        ("github_account", person.github is None),
        ("linkedin_account", "linkedin" not in platforms),
        ("x_account", "x" not in platforms),
        ("website", not person.websites),
        ("current_affiliation", not current),
        ("bio", not person.bio),
        ("photo", not person.photo_url),
        ("linkedin_details", "linkedin" in platforms and "linkedin" not in detailed),
        ("x_details", "x" in platforms and "x" not in detailed),
    ) if missing]

    return Profile(
        id=person.id.replace("person:", "profile:", 1), person=person.id,
        headline=(headline or "").strip().split("\n")[0][:200] or None,
        location=(github_node or {}).get("location") or None,
        current_roles=current_roles, expertise=expertise,
        technologies=sorted(technologies.values(), key=lambda c: c.label.lower()),
        programming_languages=programming_languages, recognitions=recognitions,
        open_source=open_source, talks=talks, gaps=gaps,
        sources=sources,
    )


def _pinned(node: dict[str, Any] | None) -> list[str]:
    nodes = ((node or {}).get("pinnedItems") or {}).get("nodes") or []
    return [f"repo:{r['nameWithOwner'].lower()}" for r in nodes if r]


def _contributed(node: dict[str, Any] | None) -> list[str]:
    nodes = ((node or {}).get("repositoriesContributedTo") or {}).get("nodes") or []
    return [f"repo:{r['nameWithOwner'].lower()}" for r in nodes if r]


def _person_repos(node: dict[str, Any] | None) -> list[str]:
    owned = ((node or {}).get("repositories") or {}).get("nodes") or []
    return list(dict.fromkeys(_pinned(node) + [f"repo:{r['nameWithOwner'].lower()}"
                                               for r in owned if r]))
