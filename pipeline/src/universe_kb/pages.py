"""
Parsers for the content pages: the githubuniverse.com home, pricing and tour pages, and
the RainFocus Explore, catalog and FAQ pages.

Each parser returns plain dicts shaped like the matching model fields. They depend on
page markup that GitHub can change at any time, so tests pin them to the saved snapshot
and the build fails loudly when a section disappears.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from universe_kb.html_tree import Node, html_to_markdown, parse_html
from universe_kb.ids import slugify

COUNTRY_REGIONS = {
    "Australia": "asia-pacific", "India": "asia-pacific", "Japan": "asia-pacific",
    "Singapore": "asia-pacific", "Canada": "americas", "Brazil": "americas",
    "United States": "americas", "Mexico": "americas", "France": "emea", "Spain": "emea",
    "UK": "emea", "Germany": "emea", "Netherlands": "emea",
}


class PageChanged(RuntimeError):
    """A page no longer has a section the parser relies on."""


def _require(node: Node | None, what: str) -> Node:
    if node is None:
        raise PageChanged(f"page section not found: {what}")
    return node


def _clock(text: str) -> str:
    return datetime.strptime(text.strip().upper().replace(".", ""), "%I:%M %p").strftime("%H:%M")


def _time_range(text: str) -> tuple[str | None, str | None]:
    parts = [p for p in re.split(r"\s*[–-]\s*", text) if p.strip()]
    if not parts:
        return None, None
    return _clock(parts[0]), _clock(parts[1]) if len(parts) > 1 else None


def _section_after_heading(root: Node, heading: str) -> Node:
    """The `<section>` that contains a heading whose text starts with `heading`."""
    for node in root.find_all():
        if node.tag in {"h2", "h3"} and node.text().startswith(heading):
            parent = node.parent
            while parent is not None and parent.tag != "section":
                parent = parent.parent
            return _require(parent, f"section for {heading}")
    raise PageChanged(f"heading not found: {heading}")


def json_ld_event(html: str) -> dict[str, Any]:
    for block in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html,
                            re.S):
        data = json.loads(block)
        if data.get("@type") == "Event":
            return data
    raise PageChanged("no schema.org Event in page")


def home_agenda(html: str, year: int) -> list[dict[str, Any]]:
    section = _section_after_heading(parse_html(html), "agenda/")
    days = []
    for heading in section.find_all("h3"):
        match = re.match(r"([a-z]{3})(\d{1,2})_day(\d+)", heading.text().replace(" ", ""))
        if not match:
            continue
        month, day, number = match.groups()
        date = datetime.strptime(f"{month} {day} {year}", "%b %d %Y").date().isoformat()
        items = []
        day_list = _require(heading.parent, "agenda day").find("ol")
        for li in _require(day_list, "agenda items").find_all("li"):
            time_node = li.find("time")
            first_span = time_node.find("span") if time_node else None
            start, end = _time_range(first_span.text()) if first_span else (None, None)
            title = _require(li.find("div"), "agenda title").text()
            paragraph = li.find("p")
            description = paragraph.text() if paragraph else ""
            items.append({"start": start, "end": end, "title": title,
                          "description": description or None})
        text = " ".join(f"{i['title']} {i['description'] or ''}" for i in items).lower()
        access = ("invitation only" if "invitation only" in text
                  else "separate ticket required" if "separate ticket" in text else None)
        days.append({"id": f"day:{date}", "date": date, "label": f"Day {number}",
                     "access": access, "agenda": items})
    if not days:
        raise PageChanged("agenda has no days")
    return days


def home_featured_speakers(html: str) -> list[tuple[str, str]]:
    """(name, organization) pairs from the featured-speakers carousel."""
    section = _section_after_heading(parse_html(html), "featured-speakers/")
    pairs = []
    for button in section.find_all("button"):
        # The caption is rendered twice in nested spans; the innermost holds it once.
        captions = [s.text() for s in button.find_all("span")
                    if ", " in s.text() and not s.find("span")]
        caption = captions[0] if captions else None
        if caption:
            name, org = caption.split(", ", 1)
            pairs.append((name.strip(), org.strip()))
    return list(dict.fromkeys(pairs))


def home_testimonials(html: str) -> list[str]:
    return [q.text() for q in parse_html(html).find_all("blockquote") if q.text()]


def home_highlights(html: str, site_url: str, year: int) -> list[dict[str, Any]]:
    try:
        section = _section_after_heading(parse_html(html), f"{year}-highlights/")
    except PageChanged:
        return []
    media = []
    for button in section.find_all("button"):
        image = button.find("img")
        label = next((d.text() for d in button.find_all("div") if d.text().endswith(".mp4")),
                     None)
        if not image or not label or not image.attrs.get("src", "").startswith("/registration/"):
            continue
        title = label.removesuffix(".mp4").replace("_", " ")
        media.append({"kind": "video", "title": title, "url": None,
                      "thumbnail_url": f"{site_url}{image.attrs['src']}"})
    return media


def pricing_offers(html: str, in_person_price: float | None, currency: str) -> list[dict]:
    root = parse_html(html)
    offers = []
    for heading in root.find_all("h3"):
        key = heading.text().rstrip("/")
        if key not in {"virtual", "in-person", "universe-on-the-road"}:
            continue
        card = _require(heading.parent, "offer card").parent
        card = _require(card, "offer card")
        paragraphs = [p.text() for p in card.find_all("p")]
        price_text = paragraphs[1].lower() if len(paragraphs) > 1 else ""
        if "sold-out" in price_text:
            availability = "sold_out"
        elif "application" in price_text:
            availability = "application_required"
        else:
            availability = "available"
        free = price_text.startswith("free")
        offers.append({
            "id": key,
            "name": {"virtual": "Virtual", "in-person": "In person",
                     "universe-on-the-road": "Universe on the road"}[key],
            "price": 0.0 if free else in_person_price if key == "in-person" else None,
            "currency": currency,
            "availability": availability,
            "summary": paragraphs[0] if paragraphs else None,
            "includes": [li.text() for li in card.find_all("li")],
        })
    if not offers:
        raise PageChanged("pricing page has no offers")
    return offers


def tour_stops(html: str, year: int) -> list[dict[str, Any]]:
    stops = []
    for li in parse_html(html).find_all("li"):
        heading = li.find("h2")
        place = li.find("p")
        date_box = li.find("div")
        if not heading or not place or not date_box:
            continue
        month_day = [s.text() for s in date_box.find_all("span")]
        if len(month_day) < 2:
            continue
        city = heading.text().rstrip("/").strip()
        venue_name, _, country = place.text().rpartition(", ")
        link = heading.find("a") or li.find("a")
        closed = any("closed" in b.text().lower() for b in li.find_all("button"))
        date = datetime.strptime(f"{month_day[0]} {month_day[1]} {year}", "%b %d %Y")
        stops.append({
            "id": slugify(city),
            "city": city.replace("-", " ").title(),
            "country": country,
            "region": COUNTRY_REGIONS.get(country),
            "date": date.date().isoformat(),
            "venue_name": venue_name,
            "registration": "closed" if closed else "open",
            "url": link.attrs.get("href") if link and not closed else None,
        })
    if not stops:
        raise PageChanged("tour page has no stops")
    return stops


def _page_html(page: dict[str, Any]) -> str:
    """Concatenate a RainFocus page's HTML blocks in document order."""
    blocks: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "children" and isinstance(value, str):
                    blocks.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(page["data"]["pageData"])
    return "\n".join(blocks)


def _schedule_from_button(card: Node) -> str | None:
    for button in card.find_all("button"):
        raw = button.attrs.get("data-explore-add")
        if raw:
            days = json.loads(raw).get("days") or []
            return "; ".join(f"{d['day']} {d['start']}–{d['end']}" for d in days) or None
    return None


def _card_action(card: Node) -> tuple[str | None, str | None]:
    for element in card.find_all("a") + card.find_all("button"):
        label = element.text()
        if label:
            return label, element.attrs.get("href") or None
    return None, None


def experiences(explore: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """Explore-page cards (with their Learn/Connect/Experiment group) plus catalog tiles."""
    found: dict[str, dict[str, Any]] = {}
    category = None
    for node in parse_html(_page_html(explore)).iter():
        if node.tag == "div" and "universe-ca-hero" in node.classes:
            # Hero headings read "learn-and-build/", "connect-and-grow/", "experiment-and-play/".
            heading = node.find("h3")
            group = heading.text().split("-", 1)[0] if heading else ""
            category = group if group in {"learn", "connect", "experiment"} else None
        if node.tag == "div" and "universe-expl0re-card" in node.classes:
            found_card = _card(node, category, title_tag="h5")
            if found_card:
                found.setdefault(found_card["id"], found_card)
    for tile in parse_html(_page_html(catalog)).find_all("article", cls="tile"):
        found_card = _card(tile, None, title_tag="h5")
        if found_card and found_card["id"] not in found:
            found[found_card["id"]] = found_card
    if not found:
        raise PageChanged("no experience cards")
    return list(found.values())


def _card(card: Node, category: str | None, *, title_tag: str) -> dict[str, Any] | None:
    title = card.find(title_tag)
    if not title:
        return None
    slug = title.text()
    paragraphs = [p.text() for p in card.find_all("p") if p.text()]
    when_where = next((p for p in paragraphs if "|" in p or re.match(r"Oct\.? ", p)), None)
    description = next((p for p in paragraphs if p != when_where), "")
    when, _, where = (when_where or "").partition("|")
    action, action_url = _card_action(card)
    image = card.find("img")
    image_url = image.attrs.get("src") if image else None
    name = slug.replace("-", " ").strip()
    return {
        "id": slugify(slug),
        "name": name[:1].upper() + name[1:],
        "description": description,
        "category": category,
        "schedule": _schedule_from_button(card) or when.strip().replace("Oct.", "Oct") or None,
        "location": where.strip() or None,
        "action": action,
        "action_url": action_url,
        "image_url": image_url if image_url and image_url.startswith("http") else None,
    }


def faq_entries(page: dict[str, Any]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("question"), str) and isinstance(node.get("answer"), str):
                entries.append({"question": parse_html(node["question"]).text(),
                                "answer": html_to_markdown(node["answer"])})
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(page["data"]["pageData"])
    if not entries:
        raise PageChanged("FAQ page has no entries")
    return entries


def catalog_glossary(page: dict[str, Any]) -> list[dict[str, Any]]:
    """
    The catalog's glossary of session types, levels and delivery formats: one heading
    ("Breakout session (40 minutes)") and one paragraph per term.
    """
    entries = []
    for group in parse_html(_page_html(page)).find_all("div"):
        if "data-usi-trigger" not in group.attrs:
            continue
        heading = None
        for child in group.child_elements():
            if child.tag == "h4":
                heading = child.text()
            elif child.tag == "p" and heading:
                duration = re.search(r"\((\d+)\s*min", heading)
                label = re.sub(r"\s*\(.*?\)\s*$", "", heading).strip()
                entries.append({"group": group.attrs["data-usi-trigger"], "label": label,
                                "duration_minutes": int(duration.group(1)) if duration else None,
                                # Inline links leave a space before punctuation in text().
                                "description": re.sub(r"\s+([.,;:!?])", r"\1", child.text())})
                heading = None
    return entries
