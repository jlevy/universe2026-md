"""Inferred interests: normalization, the sensitive-tag rule, weighting and confidence."""

from __future__ import annotations

from universe_kb.interests import MAX_INTERESTS, Signal, infer_interests, interest_key
from universe_kb.models import Evidence

SESSION = Evidence(url="https://events.test/s/1", ref="session:s1")
REPO = Evidence(url="https://github.com/ada/engine", ref="repo:ada/engine")


def test_interest_key_merges_spellings_and_drops_sensitive_and_generic_tags() -> None:
    assert {interest_key(t) for t in ("#OpenSource", "open-source", "oss")} == {"open source"}
    assert interest_key("k8s") == interest_key("Kubernetes") == "kubernetes"
    # Community and identity tags say who someone is, not what they work on.
    for tag in ("#WomenInTech", "blacktechtwitter", "#Pride", "MentalHealthAwareness"):
        assert interest_key(tag) is None
    # Event, self-promotion and too-broad tags.
    for tag in ("#GitHubUniverse", "100DaysOfCode", "hiring", "github", "x"):
        assert interest_key(tag) is None
    # A professional domain is not a health inference.
    assert interest_key("healthcare") == "healthcare"


def test_infer_interests_weights_bases_and_rates_confidence() -> None:
    other_repo = Evidence(url="https://github.com/ada/wasm-engine", ref="repo:ada/wasm-engine")
    signals = [
        Signal("session_facets", "Security", SESSION, target="term:topics/security"),
        Signal("github_repositories", "security", REPO),
        Signal("github_repositories", "Rust", REPO),
        Signal("github_repositories", "rust", other_repo),
        Signal("github_repositories", "wasm", other_repo),
        Signal("github_repositories", "WomenWhoCode", REPO),
    ]

    claims = infer_interests(signals)

    assert [(c.label, c.basis, c.sources, c.confidence, c.weight, c.target) for c in claims] == [
        ("Security", "session_facets", ["session_facets", "github_repositories"], "high", 1.0,
         "term:topics/security"),
        ("Rust", "github_repositories", ["github_repositories"], "medium", 0.8, None),
        ("wasm", "github_repositories", ["github_repositories"], "low", 0.4, None)]
    # Evidence is kept once per sighting place.
    assert claims[0].evidence == [SESSION, REPO]
    assert claims[1].evidence == [REPO, other_repo]


def test_evidence_that_names_a_sensitive_attribute_supports_no_interest() -> None:
    adhd = Evidence(url="https://github.com/octo/i-have-adhd", ref="repo:octo/i-have-adhd")
    assert infer_interests([Signal("github_repositories", "productivity", adhd)]) == []


def test_infer_interests_keeps_the_strongest_few() -> None:
    signals = [Signal("github_repositories", f"topic{i:02d}", REPO) for i in range(30)]
    assert len(infer_interests(signals)) == MAX_INTERESTS
    assert infer_interests([]) == []


def test_taxonomy_glosses_and_spellings_merge_under_one_name() -> None:
    signals = [Signal("session_facets", label, SESSION) for label in (
        "Artificial Intelligence (AI)", "AI (Agentic AI, Generative AI, Models)", "AI")]
    signals += [Signal("session_facets", "Copilot", SESSION),
                Signal("github_repositories", "github-copilot", REPO)]

    assert [(c.label, c.confidence) for c in infer_interests(signals)] == [
        ("AI", "medium"), ("GitHub Copilot", "high")]
