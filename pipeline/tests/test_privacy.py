"""
Contact details are redacted from free text, identifiers are left alone, and `findings`
proves that nothing committed can reach anyone.
"""

from __future__ import annotations

import json
from pathlib import Path

from universe_kb.privacy import findings, redact, redact_payload

PIPELINE_DIR = Path(__file__).resolve().parents[1]


def test_redact_removes_emails_and_phones_but_not_mastodon_mentions() -> None:
    assert redact("Write to ada@example.com or call (415) 555-0123.") == (
        "Write to [email removed] or call [phone removed].")
    assert redact("Imprint: +44 20 7946 0123, WhatsApp +44 (0)20 7946 0456") == (
        "Imprint: [phone removed], WhatsApp [phone removed]")
    assert redact("Follow @ada@hachyderm.io; see US 9286046; 2024-10-29; logo@2x.png") == (
        "Follow @ada@hachyderm.io; see US 9286046; 2024-10-29; logo@2x.png")


def test_redact_payload_skips_identifiers_refs_and_urls() -> None:
    payload = {"id": "acct:mastodon/ada@hachyderm.io", "handle": "ada@hachyderm.io",
               "record_id": "ada@hachyderm.io", "url": "https://hachyderm.io/@ada",
               "repository_url": "git+ssh://git@github.com/ada/engine.git",
               "owner": "person:ada", "bio": "Mail ada@example.com",
               "pinned": ["repo:ada/engine"], "readme": {"text": "+1 415 555 0123"}}

    assert redact_payload(payload) == {**payload, "bio": "Mail [email removed]",
                                       "readme": {"text": "[phone removed]"}}


def test_findings_report_reachable_contacts_in_any_committed_file(tmp_path: Path) -> None:
    # Built from parts, so this file holds no reachable address of its own.
    address, phone = "@".join(["ada.lovelace", "mail.co"]), "+49 30 " + "1234 5678"
    (tmp_path / "accounts").mkdir()
    (tmp_path / "accounts" / "ada.yaml").write_text(
        "github_account:\n  id: gh:ada\n  record_id: ada@hachyderm.io\n"
        f"  profile_readme: Reach me at {address}\n")
    (tmp_path / "raw.json").write_text(json.dumps({"ada@hachyderm.io": {
        "acct": "ada@hachyderm.io", "url": "https://hachyderm.io/@ada",
        "about": f"Call {phone}, or see git@github.com:ada/engine.git"}}))
    (tmp_path / "notes.md").write_text("Examples: ada@example.com, (415) 555-0123.\n")

    assert sorted((Path(path).name, kind, match) for path, kind, match in findings(tmp_path)) == [
        ("ada.yaml", "address", address), ("raw.json", "phone", phone)]


def test_committed_inputs_hold_no_contact_details() -> None:
    roots = [PIPELINE_DIR / name for name in ("raw", "curation", "synthesis", "tests", "src")]
    assert findings(*roots) == []


def test_label_and_mailto_text_do_not_bypass_redaction_or_scanning(tmp_path: Path) -> None:
    from universe_kb.policy import person_text, sanitize_raw

    address = "@".join(["ada", "mail.co"])
    for value in [
        f"contact:{address}",
        f"mailto:{address}",
        f"https://example.org/ Contact: {address}",
    ]:
        assert address not in person_text(value)
        assert address not in sanitize_raw("unknown.json", {"bio": value})["bio"]
        (tmp_path / "record.json").write_text(json.dumps({"bio": value}))
        assert findings(tmp_path)
    assert redact_payload({"owner": "person:ada", "id": "acct:mastodon/ada@hachyderm.io"}) == {
        "owner": "person:ada",
        "id": "acct:mastodon/ada@hachyderm.io",
    }


def test_spaced_and_encoded_email_forms_are_redacted_and_detected(tmp_path: Path) -> None:
    domain = "mail" + ".co"
    forms = [
        "Email: ada " + "@ github",
        "ada @ " + domain,
        "ada " + "[at]github",
        "ada(at)" + domain,
        "ada at mail " + "dot co",
        "ada&#64;" + domain,
    ]
    for text in forms:
        assert redact(text).endswith("[email removed]")
        (tmp_path / "record.json").write_text(json.dumps({"bio": text}))
        assert findings(tmp_path)
    assert redact("Follow @ada@hachyderm.io and see logo@2x.png") == (
        "Follow @ada@hachyderm.io and see logo@2x.png"
    )


def test_spaced_role_affiliations_are_not_assumed_to_be_contacts() -> None:
    assert redact("Engineer @ Acme; DevRel @ GitHub") == "Engineer @ Acme; DevRel @ GitHub"


def test_mentions_dotted_affiliations_and_sentence_periods_are_preserved() -> None:
    for text in ("Developer Relations @opensource.example.org", "Engineer @ acme.example.org",
                 "I work @GitHub. Opinions are mine.", "Follow @ada.example.org"):
        assert redact(text) == text


def test_explicit_email_context_overrides_account_host_exemptions() -> None:
    from universe_kb.privacy import contact_findings

    for host in ("github.com", "mastodon.social"):
        address = "@".join(["synthetic-user", host])
        assert contact_findings("Email: " + address)
        assert contact_findings("Contact: " + address)
    assert not contact_findings("@ada@mastodon.social")
    assert not contact_findings("git@github.com:ada/engine.git")


def test_tel_uris_are_contacts_but_numeric_urls_are_not() -> None:
    from universe_kb.privacy import contact_findings

    telephone = "tel:" + "2028675309"
    for text in (telephone, f'<a href="{telephone}">Call</a>'):
        assert contact_findings(text)
        assert "2028675309" not in redact(text)
    assert redact_payload({"url": telephone}) == {"url": "[phone removed]"}
    url = "https://example.org/2028675309"
    assert redact(url) == url and not contact_findings(url)


def test_explicit_spaced_emails_accept_sentence_and_separator_boundaries() -> None:
    from universe_kb.privacy import contact_findings

    for value in ("synthetic-user @company" + ".com", "synthetic-user @ company" + ".com"):
        for ending in ("", ".", ",", ";"):
            text = "Email: " + value + ending
            assert contact_findings(text)
            assert "synthetic-user" not in redact(text)
