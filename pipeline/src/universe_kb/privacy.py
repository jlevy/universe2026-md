"""
Contact details stay out of everything committed: the knowledge base, the raw snapshot,
the synthesis and the tests.

People and organizations publish email addresses and phone numbers in profile READMEs,
bios, company pages and posts, but the knowledge base is about what people do, not how
to reach them. The build and the raw sanitizer redact both from free text, and
`findings` scans any directory so a test can prove none slipped through.

Identifiers are left alone: a Mastodon handle (`user@host`) looks like an email but is
an account ID, and URLs, typed references and Git remotes (`git@github.com:owner/repo`)
are not free text. `findings` also accepts the reserved example domains tests use
(`ada@example.com`) and phone numbers reserved for fiction (`555-0123`).
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

# An address not preceded by "@", so "@user@host" Mastodon mentions do not match, and not
# a Git remote or an image scale suffix ("logo@2x.png").
EMAIL = re.compile(
    r"(?<![@\w.+-])(?!git@)[\w.+-]+@[\w-]+(?:\.[\w-]+)*"
    r"\.(?!(?:png|jpe?g|gif|svg|webp|avif|pdf|ya?ml|md|jsonl?)\b)[A-Za-z]{2,}(?![\w-])")
# An address written out to dodge scrapers: "ada at example dot com", "ada [at] example
# [dot] com", "ada(at)example.com". A bare " at " needs a spelled-out " dot " too, so
# "meet at github.com" is not an address.
OBFUSCATED_EMAIL = re.compile(
    r"(?<![\w.+-])[\w.+-]+\s*[\[({<]\s*at\s*[\])}>]\s*[\w-]+"
    r"(?:\s*(?:[\[({<]\s*dot\s*[\])}>]|\.|\s+dot\s+)\s*[\w-]+)*"
    r"|(?<![\w.+-])[\w.+-]+\s+at\s+[\w-]+(?:\s+dot\s+[\w-]+)+",
    re.IGNORECASE,
)
# A spaced @ can identify an obfuscated work address even without a public suffix.
SPACED_EMAIL = re.compile(
    r"(?<![@\w.+-])(?P<local>[\w.+-]+)[ \t]*@[ \t]+"
    r"[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}(?![\w-]|\.[\w-])"
)
ROLE_LABELS = {"engineer", "engineering", "developer", "relations", "devrel", "advocate",
               "founder", "co-founder", "ceo", "cto", "lead", "head", "manager", "director",
               "researcher", "maintainer", "contributor", "architect", "programmer",
               "builder", "evangelist", "consultant", "designer", "internship"}
# A bare company name is also used for job affiliations ("Engineer @ Acme").
# Without a suffix, require explicit contact context rather than erasing those bios.
BARE_LABELED_EMAIL = re.compile(
    r"(?P<label>\b(?:e-?mail|contact)\s*:?\s*)"
    r"(?P<email>[\w.+-]+(?:[ \t]+@[ \t]*|[ \t]*@[ \t]+)"
    r"[\w-]+(?:\.[\w-]+)*)(?![\w@-]|\.[\w-])",
    re.IGNORECASE,
)
# North American numbers, and international ones written with a leading "+".
PHONE = re.compile(
    r"(?<![\w.])(?:\+\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?![\w-]|\.\d)"
    r"|(?<![\w.+])\+\d{1,3}(?:[\s.-]?\(?\d{1,5}\)?){2,6}(?![\w-]|\.\d)")
TEL_PHONE = re.compile(r"\btel:\s*\+?\d[\d(). -]{5,}\d(?:;ext=\d+)?", re.IGNORECASE)
MIN_PHONE_DIGITS = 7
EMAIL_REDACTED = "[email removed]"
PHONE_REDACTED = "[phone removed]"
# Keys whose values are identifiers, not free text.
ID_KEYS = {"id", "handle", "record_id", "url", "owner", "entity", "login", "snapshot",
           "input_sha256", "person", "profile", "organization", "repository", "acct",
           "did", "link", "post_url", "final_url", "requested_url", "repository_url",
           "filename", "nameWithOwner"}
REF = re.compile(
    r"(?:person|profile|org|event|session|room|venue|day|facet|term|experience|software|page|"
    r"repo|pkg|gh|acct|site):[^\s<>]+"
)
URL_LIKE = re.compile(
    r"(?:https?|git(?:\+https|\+ssh)?|ssh)://[^\s<>]+"
    r"|git@[^\s<>]+",
    re.IGNORECASE,
)
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".jsonl", ".html", ".py", ".txt", ".toml"}
# Domains reserved for examples (RFC 2606 and RFC 6761); no one can be reached there.
RESERVED_DOMAIN = re.compile(r"(?:^|\.)(?:example|test|invalid|localhost)$"
                             r"|^example\.(?:com|net|org)$", re.IGNORECASE)
# Numbers reserved for fiction: 555-0100 to 555-0199 in North America, and London's
# 020 7946 0000 to 0999.
FICTIONAL_PHONE = re.compile(r"555[\s.)-]*01\d\d|20[\s.)-]*7946[\s.-]*0\d{3}")
MASTODON_HOST = re.compile(r"https?://([a-z0-9.-]+\.[a-z]{2,})/@\w"
                           r"|acct:mastodon/[^@\s]+@([a-z0-9.-]+\.[a-z]{2,})", re.IGNORECASE)


# A street address in free text: a number and a street name, a German-style street and
# number, or a post office box. Organizations' imprints and "contact us" blocks carry them.
STREET_ADDRESS = re.compile(
    r"\b\d{1,5}[A-Za-z]?\s+(?:[A-Z][\w'.-]*\s+){1,4}(?:Street|St|Avenue|Ave|Road|Rd"
    r"|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl|Court|Ct|Parkway|Pkwy)\b\.?"
    r"|\b[A-ZÄÖÜ][\wäöüß-]*(?:straße|strasse|weg|gasse|platz|allee)\s+\d{1,4}[a-z]?\b"
    r"|\bP\.?\s?O\.?\s?Box\s+\d+",
)
ADDRESS_REDACTED = "[address removed]"


def redact_addresses(text: str) -> str:
    """Street addresses in free text about a person or organization; venues keep theirs."""
    return STREET_ADDRESS.sub(ADDRESS_REDACTED, text)


def _phones(text: str) -> list[str]:
    return [m.group(0) for m in [*PHONE.finditer(text), *TEL_PHONE.finditer(text)]
            if sum(c.isdigit() for c in m.group(0)) >= MIN_PHONE_DIGITS]


def _contact_text(text: str) -> str:
    """Normalize only contact punctuation entities, preserving the rest of the HTML."""
    text = re.sub(r"&#(?:0*64|x0*40);|&commat;", "@", text, flags=re.I)
    return re.sub(r"&#(?:0*46|x0*2e);|&period;", ".", text, flags=re.I)


def _explicit_contact(text: str, start: int) -> bool:
    prefix = text[max(0, start - 100):start].rsplit("\n", 1)[-1]
    return bool(re.search(r"\b(?:e-?mail|mailto|contact|reach\s+me|write\s+to)\b[^\n@]{0,40}$",
                          prefix, re.IGNORECASE))


def _spaced_contact(text: str, match: re.Match[str]) -> bool:
    return match["local"].casefold() not in ROLE_LABELS or _explicit_contact(text, match.start())


def redact(text: str) -> str:
    text = _contact_text(text)
    text = BARE_LABELED_EMAIL.sub(lambda m: m["label"] + EMAIL_REDACTED, text)
    text = SPACED_EMAIL.sub(
        lambda m: EMAIL_REDACTED if _spaced_contact(text, m) else m.group(0), text)
    text = OBFUSCATED_EMAIL.sub(EMAIL_REDACTED, EMAIL.sub(EMAIL_REDACTED, text))
    for number in _phones(text):
        text = text.replace(number, PHONE_REDACTED)
    return text


def is_identifier(key: str | None, value: str) -> bool:
    if re.match(r"^(?:mailto|tel):", value, re.IGNORECASE):
        return False
    return key in ID_KEYS or bool(REF.fullmatch(value)) or bool(URL_LIKE.fullmatch(value))


def redact_payload(value: Any, key: str | None = None) -> Any:
    """A copy of a payload with contact details removed from its free text."""
    if isinstance(value, dict):
        return {k: redact_payload(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_payload(v, key) for v in value]
    if isinstance(value, str) and not is_identifier(key, value):
        return redact(value)
    return value


# Large Mastodon servers, on top of those the scanned data itself shows to be Mastodon.
KNOWN_MASTODON = {"mastodon.social", "mastodon.online", "mas.to", "fosstodon.org",
                  "hachyderm.io", "infosec.exchange", "techhub.social", "indieweb.social"}
# A user name before one of these hosts is a Git remote's (`git+https://ada@github.com/…`).
GIT_HOSTS = {"github.com", "gitlab.com", "bitbucket.org"}


def email_kind(address: str, mastodon_hosts: set[str]) -> str:
    """
    "mastodon" for a handle on a Mastodon server, "git" for a Git remote's user name,
    "example" for a reserved example domain, and "address" for anything that may reach
    someone.
    """
    host = address.rsplit("@", 1)[-1].lower()
    if host in mastodon_hosts | KNOWN_MASTODON:
        return "mastodon"
    if host in GIT_HOSTS:
        return "git"
    if RESERVED_DOMAIN.search(host):
        return "example"
    return "address"


def _deobfuscate(text: str) -> str:
    """`ada at example dot com` as `ada@example.com`, so it can be classified."""
    text = re.sub(r"\s*@\s*", "@", _contact_text(text))
    text = re.sub(r"\s*[\[({<]\s*at\s*[\])}>]\s*|\s+at\s+", "@", text, flags=re.IGNORECASE)
    return re.sub(r"\s*[\[({<]\s*dot\s*[\])}>]\s*|\s+dot\s+", ".", text, flags=re.IGNORECASE)


def _strings(value: Any, key: str | None = None) -> Iterable[str]:
    """The free-text strings in parsed data: not dict keys, identifiers or URLs."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield from _strings(v, k)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item, key)
    elif isinstance(value, str) and not is_identifier(key, value):
        yield value


def _file_strings(path: Path, text: str) -> Iterable[str]:
    if path.suffix == ".json":
        yield from _strings(json.loads(text))
    elif path.suffix == ".jsonl":
        for line in text.splitlines():
            yield from _strings(json.loads(line))
    elif path.suffix in {".yaml", ".yml"} or (path.suffix == ".md" and text.startswith("---\n")):
        front, _, body = text.removeprefix("---\n").partition("\n---\n")
        yield from _strings(yaml.load(front if path.suffix == ".md" else text,
                                      Loader=yaml.CSafeLoader))
        if path.suffix == ".md":
            yield body
    else:
        yield text


def _files(roots: Iterable[Path]) -> list[Path]:
    paths: list[Path] = []
    for root in roots:
        candidates = [root] if root.is_file() else sorted(root.rglob("*"))
        paths += [p for p in candidates if p.is_file() and p.suffix in TEXT_SUFFIXES]
    return paths


def mastodon_hosts(texts: Iterable[str]) -> set[str]:
    """Servers that some profile URL or account ID in `texts` shows to be Mastodon."""
    hosts: set[str] = set()
    for text in texts:
        hosts.update((a or b).lower() for a, b in MASTODON_HOST.findall(text))
    return hosts


def scan_text(text: str, hosts: set[str] | None = None) -> list[tuple[str, str]]:
    """Classified contact-like strings, including obfuscated and HTML-encoded forms."""
    text = _contact_text(text)
    hosts = mastodon_hosts([text]) if hosts is None else hosts
    def classified(address: str, start: int) -> str:
        kind = email_kind(_deobfuscate(address), hosts)
        return "address" if kind in {"git", "mastodon"} and _explicit_contact(text, start) else kind

    found = [(classified(m.group(0), m.start()), m.group(0)) for m in EMAIL.finditer(text)]
    found += [(classified(m.group(0), m.start()), m.group(0))
              for m in OBFUSCATED_EMAIL.finditer(text)]
    found += [(classified(m.group(0), m.start()), m.group(0))
              for m in SPACED_EMAIL.finditer(text) if _spaced_contact(text, m)]
    found += [(classified(m["email"], m.start("email")), m["email"])
              for m in BARE_LABELED_EMAIL.finditer(text)]
    found += [("example" if FICTIONAL_PHONE.search(m) else "phone", m) for m in _phones(text)]
    return found


def contact_findings(text: str) -> list[tuple[str, str]]:
    """Reachable contact details in one free-text value; safe for bio validation."""
    return [f for f in scan_text(text) if f[0] in {"address", "phone"}]


def scan(roots: Iterable[Path]) -> list[tuple[str, str, str]]:
    """(path, kind, match) for every email-like string or phone number under `roots`."""
    files = {path: path.read_text(errors="replace") for path in _files(roots)}
    hosts = mastodon_hosts(files.values())
    return [
        (str(path), kind, match)
        for path, text in files.items()
        for string in _file_strings(path, text)
        for kind, match in scan_text(string, hosts)
    ]


def findings(*roots: Path) -> list[tuple[str, str, str]]:
    """(path, kind, match) for every email address or phone number that may reach someone."""
    return [f for f in scan(roots) if f[1] in {"address", "phone"}]
