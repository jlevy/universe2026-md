"""
`build_pages` against the committed `raw/` snapshot: the organizer's own copy for every
saved page, in reading order, without navigation chrome. Expected text is what a reader
sees on githubuniverse.com and the attendee portal at the time of the snapshot.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

import pytest

from universe_kb.models import Page, PageSection
from universe_kb.site_content import build_pages

RAW_DIR = Path(__file__).resolve().parents[1] / "raw"

EXPLORE_CARDS = [
    "GitHub-central", "expert-center", "discussions-lounge", "level-up-lounge",
    "open-source-records", "hack-your-badge", "the-makerspace", "after-hours-events",
    "the-shop", "wellness-lounge",
]


@cache
def pages() -> dict[str, Page]:
    manifest = json.loads((RAW_DIR / "manifest.json").read_text())["files"]
    return {page.id: page for page in build_pages(RAW_DIR, manifest)}


def section(page_id: str, heading: str) -> PageSection:
    return next(s for s in pages()[page_id].sections if s.heading == heading)


def test_every_saved_page_is_a_valid_page_without_chrome() -> None:
    found = pages()

    assert list(found) == [
        "page:githubuniverse.com/home", "page:githubuniverse.com/pricing",
        "page:githubuniverse.com/on-the-road", "page:githubuniverse.com/convince",
        "page:attendee-portal/sessioncatalog", "page:attendee-portal/speakers",
        "page:attendee-portal/sponsors", "page:attendee-portal/explore",
        "page:attendee-portal/universe-faq",
    ]
    # Portal pages are named as the site navigation names them.
    assert [p.title for p in found.values() if p.site == "attendee-portal"] == [
        "Sessions", "Speakers", "Sponsors", "Explore", "FAQs"]
    for page in found.values():
        Page.model_validate(page.model_dump())
        (source,) = page.sources
        assert source.snapshot and (RAW_DIR.parent / source.snapshot).is_file()
        assert source.retrieved_at
        # The sponsors page is only a catalog widget, with no copy of its own.
        assert page.sections or page.id == "page:attendee-portal/sponsors"
        dumped = json.dumps(page.model_dump(), ensure_ascii=False)
        for chrome in ["Try GitHub free", "GitHub on LinkedIn", "Skip to content", "Jump to"]:
            assert chrome not in dumped
        for image in (i for s in page.sections for i in s.images):
            assert image.url.startswith("https://") and not image.url.endswith(".svg")


def test_home_sections_follow_reading_order() -> None:
    sections = pages()["page:githubuniverse.com/home"].sections

    assert [s.heading for s in sections] == [
        None, "stay-tuned/",
        "Discover the latest at GitHub’s flagship developer event uniting humans, agents, "
        "and the world’s code to build what’s next.",
        None, "Universe is where builders become orchestrators",
        "dev.experience()", "dev.learn()", "dev.connect()",
        "save-your-seat/", "virtual/", "What's included", "in-person/", "What's included",
        "universe-on-the-road/", "What's included", "featured-speakers/",
        "agenda/", "oct27_day0", "oct28_day1", "oct29_day2", "oct30_day3",
        None, "2025-highlights/",
    ]
    testimonials, highlights = sections[-2:]
    assert (testimonials.text or "").count("attendee:\n\n> ") == 3
    assert (highlights.text or "").startswith(
        "Opening Keynote\n\nJoin us for the opening keynote, where we'll kick things off")


def test_convince_letter_is_kept_verbatim() -> None:
    intro, subject, message = pages()["page:githubuniverse.com/convince"].sections

    assert intro.heading == "Convince your boss"
    assert "Once you replace everything in **[BOLD]** with" in (intro.text or "")
    assert [(c.label, c.url) for c in intro.calls_to_action] == [
        ("Download PDF", "https://githubuniverse.com/registration/convince-your-boss.pdf")]
    assert (subject.heading, subject.text) == (
        "Subject", "Investing in growth: Request to attend GitHub Universe 2026")
    letter = message.text or ""
    assert letter.startswith("Hi **[MANAGER’S NAME]**,\n\nI’d like to request your approval")
    assert "\n- Hotel: **[add cost per night]** (plus taxes, subject to availability)\n" in letter
    assert "\n\nIf we purchase four or more passes, we’ll receive 20% off" in letter
    assert letter.endswith("Best Regards,\n**[YOUR NAME]**\n**[Your title / team]**")


def test_pricing_keeps_each_tier_with_its_inclusions() -> None:
    sections = pages()["page:githubuniverse.com/pricing"].sections
    headings = [s.heading for s in sections]

    tiers = {}
    for tier in ["virtual/", "in-person/", "universe-on-the-road/"]:
        offer, included = sections[headings.index(tier)], sections[headings.index(tier) + 1]
        assert included.heading == "What's included"
        price = (offer.text or "").split("\n\n")[-1]
        items = [line for line in (included.text or "").split("\n") if line.startswith("- ")]
        tiers[tier] = (price, len(items), [c.label for c in offer.calls_to_action])
    assert tiers == {
        "virtual/": ("free", 3, ["Save your virtual seat"]),
        "in-person/": ("sold-out!", 7, ["Get notified"]),
        "universe-on-the-road/": ("free* *application required to attend", 5,
                                  ["Find your city"]),
    }


def test_explore_keeps_group_intros_and_every_card() -> None:
    sections = pages()["page:attendee-portal/explore"].sections
    by_heading = {s.heading: s for s in sections}

    for group, intro in [("learn-and-build/", "Build your skills and explore"),
                         ("connect-and-grow/", "Chat with open source experts"),
                         ("experiment-and-play/", "Whether you’re swapping stories")]:
        assert (by_heading[group].text or "").startswith(intro)
    assert [s.heading for s in sections if s.heading in EXPLORE_CARDS] == EXPLORE_CARDS
    for card in EXPLORE_CARDS:
        when_where, description = (by_heading[card].text or "").split("\n\n")
        assert when_where.startswith("Oct 28-29 | ") and description
        assert len(by_heading[card].images) == 1


@pytest.mark.parametrize(("page_id", "heading", "text"), [
    # Screen-reader eyebrow kept once; the compact responsive copy is dropped.
    ("page:githubuniverse.com/home", "stay-tuned/",
     "october 28–29 / san francisco, CA in-person & virtual"),
    ("page:githubuniverse.com/home", "dev.connect()",
     "Meet collaborators, open source maintainers, and leaders you’ll stay connected to "
     "long after Universe ends."),
    # The date before the city heading belongs to its card; a disabled button is a status.
    ("page:githubuniverse.com/on-the-road", "bengaluru/",
     "dec 1\n\nConrad Bengaluru, India\n\nAt capacity - registration closed"),
    ("page:attendee-portal/universe-faq", "Where and when is Universe?",
     "Universe will take place on October 28 - 29, 2026 at [Fort Mason Center for Arts & "
     "Culture](https://fortmason.org/) in San Francisco, CA. Broadcast times and schedule "
     "will be announced in September."),
    ("page:attendee-portal/speakers", "speakers/", None),
])
def test_section_text(page_id: str, heading: str, text: str | None) -> None:
    assert section(page_id, heading).text == text
