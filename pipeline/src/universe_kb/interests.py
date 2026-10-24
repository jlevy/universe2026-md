"""
Inferred interests: what a person's own public activity says they care about.

Two kinds of signal, strongest first: the topics of sessions they chose to speak on, and
the topics of repositories they own, pin or contribute to. Each interest is one claim
naming every basis that supports it, a weight relative to the person's strongest
interest, and up to three pieces of evidence.

Tags that would reveal identity, health, faith or politics are never interests: a
community tag like `womenintech` says something about who a person is, not what they
work on, and the knowledge base does not infer that. Neither label nor evidence may
state one. Event and generic tags are dropped too.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field

from universe_kb.models import Claim, Evidence
from universe_kb.sensitive import is_sensitive

BASIS_WEIGHTS = {
    "session_facets": 3.0,
    "github_repositories": 2.0,
}
MAX_INTERESTS = 12
MAX_EVIDENCE = 3

# Identity, health, faith and politics: never inferred from tags.
SENSITIVE = re.compile(
    r"women|girls|female|black|latin|hispanic|asian|indigenous|lgbt|queer|pride|trans\b"
    r"|disab|neurodiver|adhd|autis|mental|faith|christian|muslim|jewish|church"
    r"|vote|election|politic|immigra|refugee|veteran|mom|dad|parent",
    re.IGNORECASE)
# Events, self-promotion and words too broad to say anything.
GENERIC = {
    "githubuniverse", "githubuniverse2026", "githubuniverse26", "ghuniverse", "universe",
    "msbuild", "githubsatellite", "hacktoberfest", "100daysofcode", "newprofilepic",
    "livingthedream", "community", "developer", "developers", "github", "microsoft",
    "hiring", "jobs", "job", "giveaway", "awesome", "awesome-list", "list", "tech",
    "technology", "programming", "coding", "code", "software", "news", "conference",
}
# Spellings of the same interest, keyed by normalized form.
SYNONYMS = {
    "ai": "ai", "artificial intelligence": "ai", "genai": "generative ai",
    "generative ai": "generative ai", "llm": "llms", "llms": "llms",
    "large language models": "llms", "ml": "machine learning",
    "machine learning": "machine learning", "machinelearning": "machine learning",
    "opensource": "open source", "open source": "open source", "oss": "open source",
    "js": "javascript", "ts": "typescript", "k8s": "kubernetes",
    "devsecops": "devsecops", "appsec": "application security", "infosec": "security",
    "cybersecurity": "security", "a11y": "accessibility", "dotnet": ".net", "net": ".net",
    "reactjs": "react", "vuejs": "vue", "nodejs": "node.js", "node": "node.js",
    "githubcopilot": "github copilot", "copilot": "github copilot",
    "githubactions": "github actions", "actions": "github actions",
    "ai: agents": "ai agents", "agentic ai": "ai agents", "agents": "ai agents",
    "ai agents": "ai agents", "advanced security": "github advanced security",
    "ghas": "github advanced security", "codespaces": "github codespaces",
    "vs code": "vs code", "vscode": "vs code", "visual studio code": "vs code",
}
# How merged interests are shown, for keys whose spellings differ.
DISPLAY = {
    "ai": "AI", "generative ai": "Generative AI", "llms": "LLMs", "ai agents": "AI agents",
    "machine learning": "Machine learning", "open source": "Open source",
    "github copilot": "GitHub Copilot", "github actions": "GitHub Actions",
    "github advanced security": "GitHub Advanced Security",
    "github codespaces": "GitHub Codespaces", "vs code": "VS Code", "kubernetes": "Kubernetes",
    "javascript": "JavaScript", "typescript": "TypeScript", "react": "React", "vue": "Vue",
    "node.js": "Node.js", ".net": ".NET", "security": "Security",
    "application security": "Application security", "accessibility": "Accessibility",
}


def interest_key(label: str) -> str | None:
    """The normalized form an interest is merged on, or None for a tag to drop."""
    text = label.strip().lstrip("#")
    if not text or SENSITIVE.search(text) or is_sensitive(text):
        return None
    # Taxonomies gloss a term in parentheses ("Artificial Intelligence (AI)").
    text = re.sub(r"\s*\([^)]*\)", "", text) or text
    key = re.sub(r"[\s_-]+", " ", text.lower()).strip()
    key = SYNONYMS.get(key, SYNONYMS.get(key.replace(" ", ""), key))
    if key.replace(" ", "") in GENERIC or key in GENERIC or len(key) < 2:
        return None
    return key


@dataclass
class Signal:
    """One sighting of an interest: its basis, the label as seen, and where."""

    basis: str
    label: str
    evidence: Evidence
    target: str | None = None


@dataclass
class _Interest:
    labels: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    evidence: list[Evidence] = field(default_factory=list)
    target: str | None = None


def infer_interests(signals: list[Signal]) -> list[Claim]:
    """
    Merge signals into weighted interest claims. A basis counts with diminishing returns
    (1 + log2 of its sightings), so one prolific source does not drown the rest.
    """
    merged: dict[str, _Interest] = defaultdict(_Interest)
    for signal in signals:
        key = interest_key(signal.label)
        evidence = f"{signal.evidence.quote or ''} {signal.evidence.url or ''}"
        if key is None or is_sensitive(evidence):
            continue
        interest = merged[key]
        interest.labels[signal.label.lstrip("#")] += 1
        interest.counts[signal.basis] += 1
        interest.target = interest.target or signal.target
        if len(interest.evidence) < MAX_EVIDENCE and signal.evidence not in interest.evidence:
            interest.evidence.append(signal.evidence)
    scores = {key: sum(BASIS_WEIGHTS[b] * (1 + math.log2(n)) for b, n in i.counts.items())
              for key, i in merged.items()}
    top = sorted(scores, key=lambda k: (-scores[k], k))[:MAX_INTERESTS]
    if not top:
        return []
    best = scores[top[0]]
    claims = []
    for key in top:
        interest = merged[key]
        bases = sorted(interest.counts, key=lambda b: -BASIS_WEIGHTS[b])
        sightings = sum(interest.counts.values())
        confidence = ("high" if len(bases) >= 2 else "medium" if sightings >= 2 else "low")
        # A canonical name for merged spellings, else the label as most often seen.
        label = DISPLAY.get(key) or max(
            interest.labels, key=lambda lab: (interest.labels[lab], lab[:1].isupper()))
        claims.append(Claim(
            label=label, target=interest.target, basis=bases[0],  # pyright: ignore[reportArgumentType]
            confidence=confidence, weight=round(scores[key] / best, 2),
            sources=bases,  # pyright: ignore[reportArgumentType]
            evidence=interest.evidence))
    return claims
