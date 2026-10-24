# Feature: Knowledge Base Hardening

**Date:** 2026-10-24 (last updated 2026-10-24)

**Author:** Joshua Levy, with LLM assistance

**Status:** Draft

## Overview

The GitHub Universe knowledge base (KB) builds end to end into a valid, connected set of
softschema artifacts.
This plan collects the known KB work that would make it more reliable and more accurate,
and ready for a second conference: the next steps in
[the knowledge graph research](../../research/research-2026-10-23-universe-knowledge-graph.md#next-steps),
the technical debt in
[the KB plan](../done/plan-2026-10-24-universe-knowledge-base.md#technical-debt), and
the fixes in
[the data-quality review](../../research/review-2026-10-24-universe-kb-data-quality.md).

Graph work (claim weighting, path de-duplication, search boosts, ID namespacing and
hosting) is planned in Paraverse, which loads this KB into FalkorDB:
[the graph catalog and hardening plan](https://github.com/jlevy/paraverse/blob/main/docs/project/specs/active/plan-2026-10-24-graph-catalog-and-hardening.md).
New data sources are in
[plan-2026-10-24-deeper-enrichment-sources.md](plan-2026-10-24-deeper-enrichment-sources.md).

## Goals

- Catch regressions automatically: in CI, in re-crawl diffs and in the review checks.
- Fix the people-data and organization-data defects that need no new sources.
- Prepare the code and the contracts for a second conference.

## Non-Goals

- New sources or paid collection.
- Changes to what the data policy allows.
- Graph and browser changes, which belong to Paraverse.

## Background

The current design is described in
[arch-2026-10-24-conference-kb.md](../../architecture/arch-2026-10-24-conference-kb.md),
whose Known Limitations section is the source of several items here.

## Design

### Approach

Each item is small and independent and can land as its own pull request.
Data fixes follow the pattern in the data-quality review: curate the cases found, add a
build rule for the class, and keep the review check as a regression guard.

### Components

`pipeline/`: crawler, build, curation and tests.

## Implementation Plan

### Phase 1: Checks and Data Fixes

- [ ] Run CI on the pipeline: `universe-kb schemas --check`, `universe-kb validate`,
  `pytest`, `ruff` and `basedpyright`.
- [ ] Re-crawl on a schedule and diff each run: use the manifest’s hashes to see which
  sources changed, and report added, removed and changed sessions, speakers, rooms,
  sponsors, accounts and affiliations.
  Run `bio-bundles` after each build so new and stale bios are rewritten.
- [ ] Scan free text for instruction-like lines and flag them, so consumers can see
  where untrusted text needs extra care.
- [ ] List the `linkedin_details` and `x_details` gaps only for accounts whose details
  were not collected.
- [ ] Add a derived `current_title`, so no consumer pairs an old title with a newer
  employer.
- [ ] Keep person IDs stable when a catalog is reordered, by checking new IDs against
  the previous KB build through the RainFocus `userRef` kept in `sources`.
- [ ] Record when a Bluesky domain was assumed for a bare handle.
- [ ] Propose GitHub accounts for past-only speakers from a search by name and employer,
  as curation candidates that a maintainer confirms; never link them automatically.
- [ ] Resolve Mastodon handles whose domain differs from their server through WebFinger.
- [ ] Move company user accounts that speakers gave as their GitHub handle to the
  organization.
- [ ] Stop crediting a podcast network’s feed, linked from a person’s homepage, as that
  person’s writing.
- [ ] Work through the open findings in the data-quality review: curation for the cases
  found and build rules for each class.
- [ ] Add LLM-assisted mention extraction beside the gazetteer: a new `Mention.method`
  value, a character-offset evidence span, a confidence and a review flag; propose new
  gazetteer entries from accepted results; and scan sponsor summaries and experience
  descriptions too.
- [ ] Match sponsors to GitHub organizations with a public-suffix list, so domains such
  as `.co.uk` compare correctly.
- [ ] Split `build.py` into people, sessions and organizations modules.
- [ ] Keep `raw/` small as it grows: compact JSON, or Git LFS for the largest files.
- [ ] Fix the HTML text joiner that leaves a space before punctuation, and remove the
  glossary’s workaround.

### Phase 2: A Second Conference

- [ ] Parameterize the edition constants, so a new edition becomes current without code
  changes, and point the `sponsors` edge, the FAQ and the media index at their own
  edition.
- [ ] Move the conference-independent modules (models, artifacts, graph export, search,
  schemas, IDs, snapshot, rendering, people, profile sources, bios, and the web,
  Bluesky, Mastodon, feed and Bright Data clients) into a shared package, and keep
  per-conference crawling, page parsing and curation in each conference’s project.
- [ ] Move the contracts toward `enforced` once several crawls show which fields are
  always present: make them required, close top-level shapes, and record the change in
  the contract version.

## Testing Strategy

- Each data fix adds a test against the saved snapshot and keeps its review check.
- CI runs every project’s lint and tests on each pull request.

## Rollout Plan

Each item lands as its own pull request, or a few related items together.
Pull requests that change data carry the data policy’s review checklist.

## Open Questions

- Which re-crawl schedule fits: daily before an event and weekly after, or on demand?
- Should flagged instruction-like text be removed from the KB, or kept and marked?

## References

- [Architecture: conference knowledge base](../../architecture/arch-2026-10-24-conference-kb.md)
- [Research: GitHub Universe knowledge graph](../../research/research-2026-10-23-universe-knowledge-graph.md)
- [Review: KB data quality](../../research/review-2026-10-24-universe-kb-data-quality.md)
- [KB plan](../done/plan-2026-10-24-universe-knowledge-base.md)
- [Data policy](../../../data-policy.md)

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
