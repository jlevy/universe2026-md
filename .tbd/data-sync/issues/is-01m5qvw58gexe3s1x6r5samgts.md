---
type: is
id: is-01m5qvw58gexe3s1x6r5samgts
title: "PR #5 Qodo 3 (https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488127): recording metadata from a time-limited, Git-ignored YouTube API cache breaks the offline rebuild"
kind: bug
status: open
priority: 2
version: 3
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvvbg15jk7fs2w0tbxdcds
hold: null
hold_until: null
created_at: 2026-10-24T21:08:10.639Z
updated_at: 2026-10-24T21:14:02.047Z
started_at: 2026-10-24T21:08:20.215Z
---
Severity: Medium (Qodo: Remediation recommended; Bug, Correctness). Review: https://github.com/jlevy/universe2026-md/pull/5#pullrequestreview-5639988396. PR: jlevy/universe2026-md#5. Comment: https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488127. Files: docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:266-276 (Terms That Clash With a Git Snapshot: YouTube API data refreshed or deleted within 30 days; raw responses in a Git-ignored cache) and :302-303 (Phase 2: YouTube Data API playlist metadata into Session.recording). Related: docs/project/architecture/arch-2026-10-24-conference-kb.md:58-59 (Reproducible: the KB rebuilds from raw/, curation/ and synthesis/ with no network access). Finding: a rebuild from committed inputs cannot reproduce Session.recording once the cache is refreshed or deleted. Qodo's suggested fix: use a retainable source for recording links and metadata, or change the build and publication design to refresh and remove time-limited API data.

## Notes

Disposition: deferred (waits on a design decision for the pipeline layer). Valid: plan-2026-10-24-deeper-enrichment-sources.md keeps YouTube API responses in a Git-ignored cache (30-day refresh-or-delete terms) while arch-2026-10-24-conference-kb.md requires an offline rebuild from raw/, curation/ and synthesis/, so a fresh clone cannot re-derive Session.recording. Commit 'docs: record the offline-rebuild question for time-limited sources' makes the tension explicit in the plan (Terms That Clash With a Git Snapshot), gates Phase 2's recordings on it, and adds an open question with the survey's two options (refresh those fields on every build, or keep only video URLs GitHub also publishes elsewhere); flowmark --check passes. Waits on: the owner's choice between those options and the pipeline work that implements it (u26-2xaq, Phase 2 recordings). Close when the plan records the decision and the build follows it.
