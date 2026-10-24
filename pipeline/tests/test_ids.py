from __future__ import annotations

from universe_kb.ids import (
    normalize_org_name,
    org_key,
    parse_github_handle,
    registrable_domain,
    social_url,
)


def test_parse_github_handle_accepts_the_shapes_speakers_typed() -> None:
    assert parse_github_handle("octocat") == ("octocat", "candidate")
    assert parse_github_handle("  @octocat ") == ("octocat", "candidate")
    assert parse_github_handle("https://github.com/AdaGit") == ("AdaGit", "candidate")
    assert parse_github_handle("https://github.com/ada-l/") == ("ada-l", "candidate")
    assert parse_github_handle("github.com/octocat") == ("octocat", "candidate")


def test_parse_github_handle_separates_absent_managed_and_invalid() -> None:
    for empty in [None, "", "   ", "N/A", "n/a", "none", "-"]:
        assert parse_github_handle(empty) == (None, "absent")

    # Enterprise Managed User logins are kept, but cannot be looked up publicly.
    assert parse_github_handle("jmcintosh_micron") == ("jmcintosh_micron", "enterprise_managed")
    assert parse_github_handle("8249235_upsemu") == ("8249235_upsemu", "enterprise_managed")

    for junk in ["John Smith", "-octocat", "octo--cat", "a" * 40,
                 "https://www.linkedin.com/in/octocat"]:
        assert parse_github_handle(junk) == (None, "invalid")


def test_normalize_org_name_strips_legal_suffixes() -> None:
    assert normalize_org_name("Postman, Inc.") == "Postman"
    assert org_key("Postman, Inc.") == org_key("Postman") == "postman"
    assert normalize_org_name("Micron Technology Inc.") == "Micron Technology"
    assert org_key("Micron Technology Inc.") == org_key("Micron Technology")
    assert normalize_org_name("Fiserv Inc") == "Fiserv"
    assert normalize_org_name("  Acme   Holdings Co., Ltd. ") == "Acme Holdings"

    # Commas and parentheticals that are not legal suffixes are left for curation.
    assert normalize_org_name("Processing Foundation, University of Southern California") == (
        "Processing Foundation, University of Southern California")
    assert normalize_org_name("Advanced Micro Devices (AMD)") == "Advanced Micro Devices (AMD)"


def test_normalize_org_name_keeps_ampersand_company() -> None:
    assert normalize_org_name("Levi Strauss & Co.") == "Levi Strauss & Co."


def test_social_url_builds_canonical_profile_urls() -> None:
    assert social_url("x", "@adalovelace") == "https://x.com/adalovelace"
    assert social_url("x", "twitter.com/adalovelace") == "https://x.com/adalovelace"
    assert social_url("x", "www.x.com/adalovelace/") == "https://x.com/adalovelace"

    assert social_url("bluesky", "@babbage.dev") == "https://bsky.app/profile/babbage.dev"
    assert social_url("bluesky", "bsky.app/profile/grace.social") == (
        "https://bsky.app/profile/grace.social")

    assert social_url("linkedin", "gracehopper") == "https://www.linkedin.com/in/gracehopper"
    assert social_url("linkedin", "linkedin.com/in/gracehopper") == (
        "https://linkedin.com/in/gracehopper")

    # Full URLs are already profile links and pass through untouched.
    assert social_url("linkedin", "https://uk.linkedin.com/in/alanturing") == (
        "https://uk.linkedin.com/in/alanturing")

    for empty in [None, "", "NA", "N/A"]:
        assert social_url("bluesky", empty) is None


def test_registrable_domain() -> None:
    assert registrable_domain("https://www.postman.com/") == "postman.com"
    assert registrable_domain("docs.github.com/en") == "github.com"
    assert registrable_domain("https://WWW.Example.COM:8080/path") == "example.com"
    assert registrable_domain("localhost") is None
    assert registrable_domain(None) is None


def test_social_urls_reject_placeholders_credentials_and_malformed_profiles() -> None:
    assert social_url("linkedin", "in/ada-lovelace") == "https://www.linkedin.com/in/ada-lovelace"
    for value in ("M/A", "m", "in", "https://linkedin.com/in/in", "mailto:ada@example.org",
                  "https://user:password" + "@linkedin.com/in/ada", "https://linkedin.com/in/m"):
        assert social_url("linkedin", value) is None
