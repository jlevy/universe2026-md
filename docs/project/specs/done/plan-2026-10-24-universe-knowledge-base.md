# Feature: GitHub Universe Knowledge Base, Complete and Website-Ready

**Date:** 2026-10-24 (last updated 2026-10-24, 04:00 PDT)

**Author:** Claude Code, working autonomously for Joshua Levy

**Status:** Implemented; technical debt remains (see Technical Debt)

> In this repository the records are in `kb/`, and the pipeline (`src/universe_kb/`,
> `raw/`, `curation/`, `synthesis/`, `schemas/` and `tests/`) is in `pipeline/`. Counts
> are as of the 2026-10-24 build; where this document and the data policy differ, the
> policy and the architecture doc describe the current design.

## Overview

Turn GitHub Universe into the most comprehensive knowledge graph we can build from
reasonable sources, in organized softschema formats, with all free text kept in the
artifacts. Someone should be able to build an entire new website, or any other UI around
the conference, from this data alone.

The spike in `pipeline/` already crawls the official site and attendee portal, models
sessions, people, organizations, accounts, websites and profiles, and validates every
artifact.
This plan covers the autonomous run to fill in everything else and validate it.
The research doc
([research-2026-10-23-universe-knowledge-graph.md](../../research/research-2026-10-23-universe-knowledge-graph.md))
records the sources and the data model.

The user’s instructions, in order:

- Expand profile development for each person and allow adding attendees and other
  people.
- Model GitHub, X, LinkedIn accounts, personal websites and current company affiliations
  for each person.
- Run autonomously, collect as much reasonable information as possible, include any
  other information, and include brief bios of each person.
- Use Bright Data to get LinkedIn data and all available data on the speakers; map it
  out and test it.
- Do not ask for further confirmations; track questions and technical debt in sub-beads
  and in this spec.
- Aim for the most comprehensive knowledge graph, with all free text, sufficient to
  build a new website or UI; fill it in and validate it in one run.

## Goals

- Every piece of public conference content is an artifact: event, days and agenda,
  sessions with full abstracts, people, organizations, sponsors, rooms, venues,
  experiences, taxonomy with glossary text, FAQ, ticket tiers, tour stops, site and
  portal page text, and media (photos, logos, tiles, banners).
- Everyone involved is a person with accounts, websites, affiliations, a developed
  profile, and a brief bio, each fact with evidence.
- Past editions (2023 to 2025) are in the graph, so returning speakers have a talk
  history.
- Every artifact validates against its compiled schema and Pydantic model, the graph has
  no dangling references, and tests pass.

## Non-Goals

- Private data, logins, or anything a person has not published.
  Attendees enter only from their own public posts or curation.
- Paid runs beyond what was approved, or a paid LLM API. Brief bios are written by
  Claude subagents from cited evidence, not by a paid API.
- A website itself. The goal is data a website can be built from.

## Design

### Layers

| Layer | Sources | Paid | Status |
| --- | --- | --- | --- |
| Official | githubuniverse.com pages, RainFocus portal pages and widget API | No | Done |
| Past editions | RainFocus catalogs for universe25, universe24, universe23 | No | Done |
| Free enrichment | GitHub GraphQL, Bluesky AppView, Mastodon instance APIs, personal homepages and feeds, npm, PyPI, crates.io, Go proxy | No | Done |
| Paid enrichment | Bright Data: LinkedIn profiles and companies, X profiles with posts | Yes, with approval | Done |
| Synthesis | Brief bios written by Claude subagents from evidence bundles | No | Done: all 591 people, none stale |

### Website-Readiness Checklist

A site builder needs these, each with stable IDs, display text and image URLs:

- [x] Event: name, dates, timezone, venue, description, days with agenda
- [x] Ticket tiers with inclusions; on-the-road tour stops with registration links
- [x] Sessions: title, full abstract, times, room, speakers with roles, all facets,
  hosts, registration links, related sessions, tile image
- [x] Taxonomy: facets and terms with glossary descriptions and durations (filters)
- [x] Rooms and venues with capacity and parent venue
- [x] Experiences with schedule, location, call to action and link
- [x] FAQ with Markdown answers and links
- [x] Sponsors by tier with summary, link, logo, booth
- [x] Organizations: description (LinkedIn, sponsor listing, GitHub or homepage) and
  logo, with industry, size, headquarters and founding year where LinkedIn has them
- [x] People: name, title, affiliations, bio, photo, accounts, websites
- [x] People: LinkedIn and X profile details, education, credentials, recent writing
- [x] People: brief bio for everyone (591, in `synthesis/brief-bios.yaml`)
- [x] Site and portal page text as content entities (hero copy, section headings,
  “convince your boss” template, explore page group intros), so a site can reuse them
- [x] Media inventory: every image URL with what it depicts and where it is used
  (`kb/media.yaml`, 1,432 images)
- [x] Past editions: sessions and speakers for 2023 to 2025, linked to current people
  (364 sessions; 85 people spoke at more than one edition)
- [x] Side events from the repository’s research (all 17 were already catalog sessions)
- [x] Search text: `kb/_search/documents.jsonl` has a document per entity, glossary term
  and FAQ entry, and `kb/_graph/coverage.json` reports field coverage

## Implementation Plan

Each phase was tracked as a bead under one epic.

### Phase 1: Commit and Collect

- [x] Commit the people model and push

- [x] Bright Data LinkedIn and X profiles for current people; X profiles include up to
  100 recent posts, so no separate posts run was needed

- [x] GitHub depth: profile README, contributions, repositories contributed to

- [x] Mastodon profiles and verified links

- [x] Recent writing from website feeds

- [x] Organization profiles: descriptions, homepages, official accounts

- [x] Attendee discovery from Mastodon hashtag timelines

### Phase 2: Fill In

- [x] Past editions built and linked
- [x] Side events
- [x] Packages people publish, from their repositories: 448 repositories read, 228
  declared packages, 131 verified on npm, PyPI, crates.io or the Go proxy
- [x] Site and portal pages as content entities, and a media inventory
- [x] Brief bios for every person, in four rounds (`synthesis/README.md`)

### Phase 3: Validate and Report

- [x] Website-readiness audit against the checklist above
- [x] Data-quality review round 2
- [x] Research doc, README and tests updated
- [x] A report on the run

### Phase 4: Extra Coverage

- [x] GitHub accounts that people link from their own LinkedIn, X, Mastodon or homepage,
  for speakers whose listing named none (people with GitHub 28% to 30%)
- [x] Titles and feeds of every person’s website, wherever it was linked from (website
  titles 29% to 76% of 244 sites); employer pages are marked `company` and left out of
  bio evidence
- [x] Second enrichment pass over every account, website and repository in the kb :
  people with GitHub 32%, 146 packages, Bluesky and Mastodon details for accounts found
  late

## Testing Strategy

- `universe-kb validate` checks every artifact against its compiled JSON Schema and its
  Pydantic model; the build also re-validates every model before writing.
- The graph export fails the build on any edge to a missing entity.
- `pytest` covers parsers against the saved snapshot, ID and identity rules, and an
  end-to-end build into a temporary directory.
- An independent reviewer subagent compares the kb against raw data after each large
  addition.

## Rollout Plan

Work was committed as each bead finished.
No force-push.

## Paid Runs

| Run | Datasets | Inputs |
| --- | --- | --- |
| Test | LinkedIn profiles, X profiles | 4 + 3 |
| 1 | LinkedIn profiles, X profiles for 2026 people | 175 + 108 |
| 2 | LinkedIn and X for past speakers; LinkedIn company pages | 326 + 146 + 195 |

## Open Questions

None open.

## Technical Debt

Tracked as beads labeled `tech-debt`, and as open work in
[the KB hardening plan](../active/plan-2026-10-24-kb-hardening.md).

- `raw/` is large (past editions add 6.9 MB) and grows with each collection; consider
  compact JSON or Git LFS.
- `build.py` is over 1,400 lines; split people, sessions and organizations into modules.
- `Node.text()` joins inline text with spaces; the glossary works around the space it
  leaves before punctuation.
- Mastodon accounts whose handle domain differs from their server need WebFinger.
- Contracts changed in place at `v1` before any consumer existed; bump the version once
  something depends on them.
- A speaker who gave a company account as their GitHub handle is linked but flagged
  `unconfirmed`, not moved to the company.
- Some people have two accounts on one platform (an old and a new LinkedIn slug).
- Bright Data’s X profile records include posts for only 60 of 243 accounts, ending
  2025-11-15, so no 2026 X post is participation evidence yet.
- A homepage that advertises a podcast network’s feed credits other shows’ episodes as
  the person’s writing.
- `job_title` from a past listing can still be paired with a newer employer by a
  careless consumer; a derived `current_title` would make this harder to get wrong.
- Free text is untrusted: one Mastodon profile found via the hashtag says “Ignore all
  previous instructions…”. Hashtag posters’ profile text no longer becomes `Person.bio`,
  but every bio, README, post and page text is public data that consumers, especially
  LLM-based ones, must treat as data.

## Decision Log

- 2026-10-24: Past editions’ speakers become people with participations in those
  editions; past-only speakers are included, since the knowledge base covers the
  conference series.
- 2026-10-24: Bluesky post search needs a login, so attendee discovery uses public
  Mastodon hashtag timelines instead.
- 2026-10-24: Bright Data records about other people (“people also viewed”, similar
  profiles, likes, recommendation text) are dropped before saving.
- 2026-10-24: Brief bios are Claude-written from per-person evidence bundles and stored
  with the bundle hash, so a stale bio is detectable.
- 2026-10-24: WordPress comment feeds are skipped; their items are other people’s
  comments, not the site owner’s writing.
- 2026-10-24: A package counts only when its registry entry exists and points back to
  the repository it was declared in.
- 2026-10-24: Catalog names in directory form (“Doe, Jane”) are reordered and stripped
  of team codes; what no rule can tell goes in `curation/people.yaml` as `names`
  (renames) or `rejected_links` (wrong links).
- 2026-10-24: `Person.job_title` stays as the listing gave it, and `listed_for` names
  that listing’s event, since a past edition’s title may no longer be current.
  Person pages show a title only beside the organization it was given for.
- 2026-10-24: The bundle that bios are written from was left as is, even though it shows
  an organization twice when one source gives a title and another does not; changing its
  format would mark about 170 sound bios stale.

## References

- [Research doc](../../research/research-2026-10-23-universe-knowledge-graph.md)
- [Architecture: conference knowledge base](../../architecture/arch-2026-10-24-conference-kb.md)
- `pipeline/README.md`

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
