"""
Parsers against the committed `raw/` snapshot. Expected values are what a reader sees on
githubuniverse.com and the attendee portal at the time of the snapshot.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from universe_kb import pages

RAW_DIR = Path(__file__).resolve().parents[1] / "raw"
YEAR = 2026


def site_page(name: str) -> str:
    return (RAW_DIR / "site" / name).read_text()


def portal_page(name: str) -> dict[str, Any]:
    return json.loads((RAW_DIR / "rainfocus" / "pages" / name).read_text())


def test_home_agenda_days() -> None:
    days = pages.home_agenda(site_page("home.html"), YEAR)

    assert [(d["id"], d["label"], d["access"]) for d in days] == [
        ("day:2026-10-27", "Day 0", "invitation only"),
        ("day:2026-10-28", "Day 1", None),
        ("day:2026-10-29", "Day 2", None),
        ("day:2026-10-30", "Day 3", "separate ticket required"),
    ]
    assert [[(i["start"], i["end"], i["title"]) for i in d["agenda"]] for d in days] == [
        [("08:00", "17:00", "All programming is by invitation only")],
        [("07:30", None, "Doors open at Fort Mason Center"),
         ("09:00", None, "Keynote"),
         ("10:00", "17:30", "Breakout sessions & all experiences open"),
         ("18:00", None, "Sponsored evening events")],
        [("08:00", None, "Doors open at Fort Mason Center"),
         ("09:00", "14:00", "Breakout sessions & all experiences open"),
         ("14:00", None, "Closing keynote"),
         ("15:00", None, "Campus closes")],
        [("08:00", "16:00", "Day of Learning at GitHub HQ")],
    ]


def test_home_featured_speakers_are_clean_name_org_pairs() -> None:
    assert pages.home_featured_speakers(site_page("home.html")) == [
        ("Jenny Patchen", "Levi Strauss & Co."),
        ("Cameron Hamilton", "Alliance AI"),
        ("Angie Jones", "Agentic AI Foundation"),
        ("Franck Nijhof", "Open Home Foundation"),
        ("Julio Arruda", "GFT Technologies"),
        ("Bea Mendez Gandica", "Nuevo Foundation"),
        ("John Maeda", "Microsoft"),
        ("Kent C. Dodds", "kody.codes"),
    ]


def test_pricing_in_person_is_sold_out_at_the_json_ld_price() -> None:
    offer = pages.json_ld_event(site_page("home.html"))["offers"]
    assert (offer["price"], offer["priceCurrency"]) == ("1399", "USD")

    offers = pages.pricing_offers(site_page("pricing.html"), float(offer["price"]),
                                  offer["priceCurrency"])

    assert [(o["id"], o["price"], o["currency"], o["availability"]) for o in offers] == [
        ("virtual", 0.0, "USD", "available"),
        ("in-person", 1399.0, "USD", "sold_out"),
        ("universe-on-the-road", 0.0, "USD", "application_required"),
    ]
    in_person = offers[1]
    assert "A programmable badge" in in_person["includes"]
    assert in_person["summary"].startswith("Join in person")


def test_tour_stops() -> None:
    stops = pages.tour_stops(site_page("on-the-road.html"), YEAR)

    assert [(s["city"], s["country"], s["date"], s["registration"]) for s in stops] == [
        ("Sydney", "Australia", "2026-11-17", "open"),
        ("Toronto", "Canada", "2026-11-18", "open"),
        ("Paris", "France", "2026-11-30", "open"),
        ("Bengaluru", "India", "2026-12-01", "closed"),
        ("São Paulo", "Brazil", "2026-12-01", "open"),
        ("Madrid", "Spain", "2026-12-03", "open"),
        ("London", "UK", "2026-12-08", "open"),
        ("Munich", "Germany", "2026-12-10", "open"),
    ]
    assert stops[4]["id"] == "sao-paulo"
    assert stops[3]["venue_name"] == "Conrad Bengaluru"
    # A closed stop must not keep a registration link.
    for stop in stops:
        assert (stop["url"] is None) == (stop["registration"] == "closed")


def test_experiences_grouped_by_explore_section() -> None:
    cards = pages.experiences(portal_page("explore.json"), portal_page("sessioncatalog.json"))

    groups: dict[str | None, list[str]] = {}
    for card in cards:
        groups.setdefault(card["category"], []).append(card["id"])
    assert groups == {
        "learn": ["github-central", "expert-center"],
        "connect": ["discussions-lounge", "level-up-lounge", "open-source-records"],
        "experiment": ["hack-your-badge", "the-makerspace", "after-hours-events", "the-shop",
                       "wellness-lounge"],
        # Catalog tiles have no Explore section.
        None: ["curated-agendas"],
    }

    central = cards[0]
    assert central["name"] == "GitHub central"
    assert central["schedule"] == "Oct 28 10am–5pm; Oct 29 11am–5pm"
    assert central["location"] == "Festival Pavilion"
    expert = cards[1]
    assert (expert["schedule"], expert["location"], expert["action"]) == (
        "Oct 28-29", "Gateway Pavilion", "Book an appointment")
    assert expert["action_url"] == (
        "https://reg.githubuniverse.com/flow/github/universe26/expertcenter/")


def test_faq_entries_are_markdown_without_html() -> None:
    entries = pages.faq_entries(portal_page("universe-faq.json"))

    assert len(entries) == 14
    assert entries[0]["question"] == "Where and when is Universe?"
    assert entries[-1]["question"] == "Have a specific question that you didn’t find here?"
    for entry in entries:
        assert entry["answer"]
        assert "<" not in entry["question"] + entry["answer"]


def test_catalog_glossary_terms_and_durations() -> None:
    entries = pages.catalog_glossary(portal_page("sessioncatalog.json"))

    groups: dict[str, list[str]] = {}
    for entry in entries:
        groups.setdefault(entry["group"], []).append(entry["label"])
    assert groups == {
        "sessiontype": ["Main stage", "Breakout session", "Workshop", "Sandbox session",
                        "Ship & Tell", "Product demo", "Panel discussion", "Fireside chat",
                        "Discussions lounge", "Session after party"],
        "level": ["Level 100 – Introductory", "Level 200 – Intermediate", "Level 300 – Advanced"],
        "deliveryformat": ["In-person", "Livestream", "Recorded", "On-demand", "AI summary"],
    }
    # Durations come from the heading, e.g. "Breakout session (40 minutes)".
    assert {e["label"]: e["duration_minutes"] for e in entries if e["duration_minutes"]} == {
        "Breakout session": 40, "Workshop": 90, "Sandbox session": 45, "Ship & Tell": 15,
        "Product demo": 15, "Panel discussion": 40, "Fireside chat": 40}
    for entry in entries:
        assert entry["description"]
        assert "<" not in entry["description"]


def test_catalog_glossary_keeps_punctuation_after_a_link() -> None:
    entries = pages.catalog_glossary(portal_page("sessioncatalog.json"))

    workshop = next(e for e in entries if e["label"] == "Workshop")
    assert workshop["description"].endswith("add to your registration in the Attendee Portal.")
