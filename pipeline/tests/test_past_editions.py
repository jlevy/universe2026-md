"""
Past editions' catalogs and returning speakers: attribute spellings mapped to this
edition's facets, test rows dropped, identity keys read from speaker records, and how the
people index merges a speaker or attendee into someone already known.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from universe_kb.build import (
    Catalog,
    RawData,
    canonicalize_attributes,
    catalog_items,
    clean_name,
    listing_keys,
    normalize_names,
)
from universe_kb.people import PeopleIndex, handle_keys, identity_keys, names_compatible

CATALOG = Catalog("universe23", "2023", "editions/universe23", current=False)


def edition_raw(root: Path, attributes: list[str], items: list[dict[str, Any]]) -> RawData:
    """A raw directory holding one past edition's attribute list and session rows."""
    edition = root / CATALOG.prefix
    edition.mkdir(parents=True)
    (edition / "attributes.json").write_text(
        json.dumps({"attributes": [{"name": name} for name in attributes]}))
    (edition / "sessions.json").write_text(json.dumps({"items": items}))
    return RawData(root, {})


def test_canonicalize_attributes_maps_session_track_only_without_a_track_attribute(
        tmp_path: Path) -> None:
    def renamed(attributes: list[str], root: Path) -> list[str]:
        items = [{"attributevalues": [{"attribute": name, "value": "v"} for name in (
            "Session Type", "Session Track", "Target Audience", "Day")]}]
        canonicalize_attributes(edition_raw(root, attributes, []), CATALOG, items)
        return [value["attribute"] for value in items[0]["attributevalues"]]

    # 2023 calls its tracks "Session Track".
    assert renamed(["Session Type", "Session Track", "Target Audience", "Day"],
                   tmp_path / "2023") == ["Session type", "Track", "Target audience", "Day"]
    # Later catalogs have "Track", and "Session Track" holds track combinations.
    assert renamed(["Session Type", "Track", "Session Track", "Target Audience", "Day"],
                   tmp_path / "2024") == ["Session type", "Session Track", "Target audience",
                                          "Day"]


def test_catalog_items_drop_test_records_unscheduled_rows_and_test_speakers(
        tmp_path: Path) -> None:
    slot = [{"utcStartTime": "2023/11/08 17:00:00"}]
    raw = edition_raw(tmp_path, [], [
        {"title": "Opening keynote", "times": slot},
        {"title": "Rehearsal", "times": slot, "testRecord": True},
        {"title": "Unscheduled", "times": []},
        {"title": "Never scheduled"},
        {"title": "Test Speaker Session", "times": slot},
        {"title": "Testing at scale", "times": slot},
    ])

    assert [item["title"] for item in catalog_items(raw, CATALOG)] == [
        "Opening keynote", "Testing at scale"]


def test_listing_keys_read_each_account_field_of_a_speaker_record() -> None:
    assert listing_keys({
        "linkedIn": "linkedin.com/in/ada-lovelace/", "twitter": "@AdaL",
        "attributevalues": [{"attribute": "GitHub Handle", "value": "https://github.com/AdaL"},
                            {"attribute": "Bluesky", "value": "@Ada.bsky.social"}],
    }) == {"gh:adal", "acct:linkedin/in/ada-lovelace", "acct:x/adal",
           "acct:bluesky/ada.bsky.social"}
    # Without the top-level fields, the record's custom attributes are read instead.
    assert listing_keys({"attributevalues": [
        {"attribute": "LinkedIn", "value": "https://www.linkedin.com/in/grace/"},
        {"attribute": "X (Twitter)", "value": "https://twitter.com/GraceH"},
        {"attribute": "GitHub Handle", "value": "N/A"}]}) == {
        "acct:linkedin/in/grace", "acct:x/graceh"}
    # A managed enterprise login cannot be looked up, so it is not an identity key.
    assert listing_keys({"attributevalues": [
        {"attribute": "GitHub Handle", "value": "jdoe_acme"}]}) == set()


def test_register_is_idempotent_and_rejects_conflicting_owners() -> None:
    index = PeopleIndex()
    ada_x = identity_keys({"x": "AdaL"})
    index.register("person:ada-lovelace", "Ada Lovelace", ada_x)
    # Registering again as the person gains accounts must not list the name twice,
    # or a unique speaker would stop resolving by name.
    index.register("person:ada-lovelace", "Ada Lovelace", ada_x | {"gh:ada"})
    index.register("person:someone-else", "Someone Else", ada_x)

    assert index.resolve("Ada Lovelace", set(), claims_speaking=True) == "person:ada-lovelace"
    assert index.resolve("A. Lovelace", {"gh:ada"}, claims_speaking=False) == (
        "person:ada-lovelace")
    assert index.resolve("Someone", ada_x, claims_speaking=False) is None


def test_handle_keys_give_the_user_part_of_handle_platforms() -> None:
    assert [handle_keys(key) for key in (
        "gh:gracehopper", "acct:x/gracehopper", "acct:threads/gracehopper",
        "acct:mastodon/gracehopper@hachyderm.io", "acct:bluesky/gracehopper.bsky.social",
    )] == [["handle:gracehopper"]] * 5
    # LinkedIn slugs and websites are not handles people reuse elsewhere.
    assert handle_keys("acct:linkedin/in/gracehopper") == []
    assert handle_keys("site:gracehopper.net") == []
    # A custom-domain Bluesky handle names a domain; "babbage.social" is not user "babbage".
    assert handle_keys("acct:bluesky/babbage.social") == []
    assert handle_keys("acct:bluesky/ada.lovelace.dev") == []


def test_same_handle_on_another_platform_merges_only_when_names_agree() -> None:
    index = PeopleIndex()
    index.register("person:grace-hopper", "Grace Hopper", identity_keys({"x": "gracehopper"}))
    index.register("person:jane-smith", "Jane Smith", identity_keys({"github": "jdoe"}))

    assert index.resolve("gracehopper", identity_keys({"mastodon": "gracehopper@hachyderm.io"}),
                         claims_speaking=False) == "person:grace-hopper"
    assert index.resolve("Grace", identity_keys({"bluesky": "gracehopper.bsky.social"}),
                         claims_speaking=False) == "person:grace-hopper"
    assert index.resolve("jdoe", identity_keys({"mastodon": "jdoe@mastodon.social"}),
                         claims_speaking=False) is None
    # Four letters are too few to count as part of a longer name.
    assert not names_compatible("Jess", "Grace Hopper")
    assert index.resolve("Grace Hopper", identity_keys({"linkedin": "in/gracehopper"}),
                         claims_speaking=False) is None


def test_names_without_ascii_letters_are_not_all_compatible() -> None:
    assert not names_compatible("李雷", "王芳")


def test_clean_name_reorders_directory_style_names() -> None:
    assert clean_name("Hopper, Joe") == ("Joe Hopper", "Joe", "Hopper")
    assert clean_name("Babbage, Daniel A.") == ("Daniel A. Babbage", "Daniel A.", "Babbage")
    assert clean_name("Turing, Jerome (ITDV XD) - AF") == ("Jerome Turing", "Jerome",
                                                            "Turing")
    # Nicknames, suffixes and ordinary names stay as listed.
    assert clean_name("Mary (Min) Lee") == ("Mary (Min) Lee", None, None)
    assert clean_name("Martin Luther King, Jr.") == ("Martin Luther King, Jr.", None, None)
    assert clean_name("Ada Lovelace") == ("Ada Lovelace", None, None)


def test_normalize_names_applies_rules_then_curated_renames() -> None:
    items = [{"participants": [
        {"fullName": "Hopper, Joe", "firstName": "Hopper,", "lastName": "Joe"},
        {"fullName": "MV Karan", "firstName": "MV", "lastName": "Karan"},
        {"fullName": "Ada Lovelace", "firstName": "Ada", "lastName": "Lovelace"}]}]

    normalize_names(items, {"MV Karan": "Karan M V"})

    assert [(p["fullName"], p["firstName"], p["lastName"], p.get("globalFullName"))
            for p in items[0]["participants"]] == [
        ("Joe Hopper", "Joe", "Hopper", "Joe Hopper"),
        ("Karan M V", "Karan M", "V", "Karan M V"),
        ("Ada Lovelace", "Ada", "Lovelace", None)]
