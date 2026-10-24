from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest

from universe_kb import build as build_module
from universe_kb import pages
from universe_kb.build import OrgRecord, RawData, build, build_event

PIPELINE = Path(__file__).resolve().parents[1]


def test_current_build_drops_test_sessions_and_participants_before_entity_building(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_dir = tmp_path / "raw"
    (raw_dir / "rainfocus").mkdir(parents=True)
    (raw_dir / "manifest.json").write_text(json.dumps({"files": {}}))
    valid = {"userRef": "real-user", "fullName": "Example Speaker"}
    slot = [{"utcStartTime": "2026/10/28 17:00:00"}]
    (raw_dir / "rainfocus/sessions.json").write_text(json.dumps({"items": [
        {"title": "Valid session", "times": slot, "participants": [
            valid, {"userRef": "test-user", "fullName": "Test Person", "testRecord": True}]},
        {"title": "Test Speaker Session", "times": slot, "participants": [valid]},
        {"title": "Rehearsal", "times": slot, "testRecord": True},
        {"title": "Unscheduled", "times": []},
    ]}))

    class StopAfterSelection(Exception):
        pass

    def inspect_selection(_raw: RawData, _catalog: Any, items: list[dict[str, Any]]) -> None:
        assert [item["title"] for item in items] == ["Valid session"]
        assert items[0]["participants"] == [valid]
        raise StopAfterSelection

    monkeypatch.setattr(build_module, "canonicalize_attributes", inspect_selection)
    with pytest.raises(StopAfterSelection):
        build(raw_dir, PIPELINE / "curation", tmp_path / "kb", PIPELINE / "schemas")


def test_current_event_fringe_days_keep_their_temporal_meaning() -> None:
    raw_dir = PIPELINE / "raw"
    raw = RawData(raw_dir, json.loads((raw_dir / "manifest.json").read_text())["files"])
    event = build_event(raw, OrgRecord(key="github", name="GitHub"),
                        {"day:2026-10-26", "day:2026-10-31"}, [])
    labels = {day.date: day.label for day in event.days}
    assert labels["2026-10-26"] == "Pre-event"
    assert labels["2026-10-31"] == "Post-event"
    assert not event.highlights


def test_highlights_follow_their_explicit_edition_section() -> None:
    html = dedent('''
        <section><h2>2025-highlights/</h2><button>
          <img src="/registration/old.jpg"><div>opening_keynote.mp4</div>
        </button></section>
        <section><h2>2026-highlights/</h2><button>
          <img src="/registration/new.jpg"><div>current_keynote.mp4</div>
        </button></section>
    ''')
    assert pages.home_highlights(html, "https://example.com", 2026) == [{
        "kind": "video", "title": "current keynote", "url": None,
        "thumbnail_url": "https://example.com/registration/new.jpg"}]
    assert pages.home_highlights(html, "https://example.com", 2024) == []


@pytest.mark.parametrize("kind", ["User", "Organization"])
def test_github_build_filters_personal_music_from_unsanitized_readme(
    tmp_path: Path, kind: str,
) -> None:
    from universe_kb.models import Participation, Person

    raw = RawData(tmp_path, {"github/owners.json": {
        "url": "https://api.github.com/graphql", "retrieved_at": "2026-10-24T00:00:00Z"}})
    orgs = build_module.OrgIndex({"organizations": {}}, {})
    people = [Person(
        id="person:example", name="Example", github="gh:example",
        inclusion_basis="curated", github_resolution="resolved", sources=[],
        participations=[Participation(event="event:universe26", role="attendee",
                                      status="candidate")])]
    if kind == "Organization":
        people = []
        orgs.records["example"] = OrgRecord(
            key="example", name="Example", github_login="example")
    readme_key = "orgReadme" if kind == "Organization" else "userReadme"
    owners = {"example": {
        "login": "example", "__typename": kind, "url": "https://github.com/example",
        readme_key: {"object": {"text": (
            "Open-source projects and talks.\n\n"
            "[Listening](https://open.spotify.com/user/example)\n\n"
            "Documentation and professional writing.")}}}}
    accounts, _ = build_module.build_github(raw, owners, people, orgs)
    readme = accounts["gh:example"].profile_readme
    assert readme is not None
    assert "Open-source projects" in readme
    assert "Documentation and professional writing" in readme
    assert "spotify" not in readme
