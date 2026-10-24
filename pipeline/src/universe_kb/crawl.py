"""
Crawl the official GitHub Universe sources into `raw/`.

Two systems hold the official data:

- **githubuniverse.com** is a static Next.js export with four pages: the home page
  (agenda, featured speakers, highlights), pricing, the on-the-road tour and a
  "convince your boss" template. It has no sitemap or robots.txt.
- **RainFocus** runs the attendee portal at `reg.githubuniverse.com`. Its pages are a
  single-page app whose content comes from `flow/loadPage`, and its catalogs come from
  the widget API at `events.githubuniverse.com/api`. Each catalog widget authenticates
  with a public widget token and API profile token that `loadPage` returns under
  `widgetConf`, so nothing here is a secret and nothing needs a login.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from universe_kb.snapshot import Fetcher, Snapshot

log = logging.getLogger(__name__)

SITE_URL = "https://githubuniverse.com"
PORTAL_URL = "https://reg.githubuniverse.com"
EDITION = "universe26"
# The portal passes its workflow name as `workflowApiToken`; it identifies, not authorizes.
WORKFLOW_TOKEN = f"github.{EDITION}.attendee-portal"
TIMEZONE = "America/Los_Angeles"

SITE_PAGES = {"home": "/", "pricing": "/pricing", "on-the-road": "/on-the-road",
              "convince": "/convince"}
PORTAL_PAGES = ["sessioncatalog", "speakers", "sponsors", "explore", "universe-faq"]
# Fields the sponsor API returns but the public page never shows: staff contact details.
PRIVATE_EXHIBITOR_FIELDS = {"phone", "email"}


@dataclass(frozen=True)
class Widget:
    host: str
    widget_token: str
    profile_token: str

    def headers(self) -> dict[str, str]:
        return {
            "rfWidgetId": self.widget_token,
            "rfApiProfileId": self.profile_token,
            "Origin": PORTAL_URL,
            "Referer": f"{PORTAL_URL}/",
        }

    def url(self, endpoint: str) -> str:
        return f"https://{self.host}/api/{endpoint}"


def widget_from_page(page: dict[str, Any]) -> Widget:
    data = page["data"]
    conf = data.get("widgetConf") or {}
    if not conf.get("widgetToken") or not conf.get("apiProfileToken"):
        raise ValueError("page has no catalog widget configuration")
    return Widget(data["eventsUrl"], conf["widgetToken"], conf["apiProfileToken"])


def crawl(snapshot: Snapshot, fetcher: Fetcher) -> None:
    for name, path in SITE_PAGES.items():
        url = f"{SITE_URL}{path}"
        snapshot.save_text(f"site/{name}.html", fetcher.text(url), url=url)

    pages: dict[str, dict[str, Any]] = {}
    for page_uri in PORTAL_PAGES:
        url = f"{PORTAL_URL}/flow/loadPage"
        page = fetcher.json(
            "GET",
            url,
            params={"pageUri": page_uri, "overrideShowDate": "false",
                    "workflowApiToken": WORKFLOW_TOKEN},
        )
        # A per-response CSRF token: useless later and noisy in diffs.
        page.get("data", {}).pop("rfcsrf", None)
        pages[page_uri] = page
        snapshot.save_json(f"rainfocus/pages/{page_uri}.json", page,
                           url=f"{url}?pageUri={page_uri}")

    catalog = widget_from_page(pages["sessioncatalog"])
    crawl_sessions(snapshot, fetcher, catalog)
    sponsors = widget_from_page(pages["sponsors"])
    crawl_exhibitors(snapshot, fetcher, sponsors)
    snapshot.write_manifest()


def crawl_sessions(snapshot: Snapshot, fetcher: Fetcher, widget: Widget,
                   prefix: str = "rainfocus") -> None:
    config = fetcher.json("POST", widget.url("widgetConfig"), headers=widget.headers(), form={})
    component = config["config"]["componentConfigs"][0]
    snapshot.save_json(f"{prefix}/session-widget.json", component,
                       url=widget.url("widgetConfig"), method="POST")

    attributes = fetcher.json("POST", widget.url("attributes"), headers=widget.headers(), form={})
    snapshot.save_json(f"{prefix}/attributes.json", attributes,
                       url=widget.url("attributes"), method="POST")

    rooms = fetcher.json("POST", widget.url("rooms"), headers=widget.headers(), form={})
    snapshot.save_json(f"{prefix}/rooms.json", rooms, url=widget.url("rooms"), method="POST")

    form = {"type": "session", "browserTimezone": TIMEZONE, "catalogDisplay": "list"}
    if component.get("dataSetFilterCode"):
        form["tab.allsessions"] = component["dataSetFilterCode"]
    items: list[dict[str, Any]] = []
    total: int | None = None
    while total is None or len(items) < total:
        page = fetcher.json("POST", widget.url("sessions"), headers=widget.headers(),
                            form={**form, "from": str(len(items))})
        # The first page wraps results in `sectionList`; later pages return them flat.
        section = page["sectionList"][0] if "sectionList" in page else page
        batch = section.get("items") or []
        total = int(section.get("total") or page.get("totalSearchItems") or 0)
        if not batch:
            break
        items.extend(batch)
        log.info("sessions: %s of %s", len(items), total)
    if total is not None and len(items) < total:
        raise RuntimeError(f"session catalog stopped at {len(items)} of {total} items")
    drop_unpublished_sessions(items)
    snapshot.save_json(f"{prefix}/sessions.json", {"total": total, "items": items},
                       url=widget.url("sessions"), method="POST")


# Earlier editions whose catalogs RainFocus still serves (2022 and before return errors).
PAST_EDITIONS = ["universe25", "universe24", "universe23"]


def crawl_past_editions(snapshot: Snapshot, fetcher: Fetcher,
                        editions: list[str] = PAST_EDITIONS) -> dict[str, int]:
    """Snapshot each past edition's catalog page and sessions under `editions/<edition>/`."""
    counts = {}
    for edition in editions:
        url = f"{PORTAL_URL}/flow/loadPage"
        page = fetcher.json("GET", url, params={
            "pageUri": "sessioncatalog", "overrideShowDate": "false",
            "workflowApiToken": f"github.{edition}.attendee-portal"})
        page.get("data", {}).pop("rfcsrf", None)
        snapshot.save_json(f"editions/{edition}/pages/sessioncatalog.json", page,
                           url=f"{url}?pageUri=sessioncatalog&edition={edition}")
        crawl_sessions(snapshot, fetcher, widget_from_page(page), prefix=f"editions/{edition}")
        counts[edition] = len(snapshot.load_json(f"editions/{edition}/sessions.json")["items"])
    snapshot.write_manifest()
    return counts


def drop_unpublished_sessions(items: list[dict[str, Any]]) -> int:
    """
    Each speaker record lists all of that speaker's sessions, including unpublished
    internal ones (rehearsals, tech checks) the public catalog never shows. Keep only
    published sessions. Returns how many entries were dropped.
    """
    dropped = 0
    for item in items:
        for participant in item.get("participants") or []:
            sessions = participant.get("session") or []
            kept = [s for s in sessions if str(s.get("published")).lower() == "true"]
            dropped += len(sessions) - len(kept)
            participant["session"] = kept
    return dropped


def sanitize_saved_sessions(snapshot: Snapshot) -> int:
    """Apply `drop_unpublished_sessions` to a snapshot saved before that rule existed."""
    rel_path = "rainfocus/sessions.json"
    data = snapshot.load_json(rel_path)
    dropped = drop_unpublished_sessions(data["items"])
    if dropped:
        snapshot.rewrite_json(rel_path, data)
    return dropped


def crawl_exhibitors(snapshot: Snapshot, fetcher: Fetcher, widget: Widget) -> None:
    result = fetcher.json("POST", widget.url("exhibitors"), headers=widget.headers(),
                          form={"type": "exhibitor", "catalogDisplay": "grid"})
    sections = result.get("sectionList") or [result]
    for section in sections:
        for item in section.get("items") or []:
            for key in PRIVATE_EXHIBITOR_FIELDS:
                item.pop(key, None)
    snapshot.save_json("rainfocus/exhibitors.json", result,
                       url=widget.url("exhibitors"), method="POST")
