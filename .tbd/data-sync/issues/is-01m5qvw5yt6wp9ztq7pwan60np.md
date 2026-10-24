---
type: is
id: is-01m5qvw5yt6wp9ztq7pwan60np
title: "PR #5 Qodo 5 (https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488143): survey joins archived Universe speakers to people by name, edition and company, outside the plan's linking rule"
kind: bug
status: in_progress
priority: 2
version: 2
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvvbg15jk7fs2w0tbxdcds
hold: null
hold_until: null
created_at: 2026-10-24T21:08:11.353Z
updated_at: 2026-10-24T21:08:20.867Z
started_at: 2026-10-24T21:08:20.866Z
---
Severity: Medium (Qodo: Remediation recommended; Bug, Correctness). Review: https://github.com/jlevy/universe2026-md/pull/5#pullrequestreview-5639988396. PR: jlevy/universe2026-md#5. Comment: https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488143. Files: docs/project/research/research-2026-10-24-enrichment-sources-survey.md:62-64 (Wayback row: Universe pages joined to kb people by name plus edition plus company) and docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:102-113 (Linking Rule: a record from a new source attaches only by a listed account, a back-link or curator confirmation). Related: docs/project/architecture/arch-2026-10-24-conference-kb.md:513-551 (Identity Resolution: past-edition catalogs merge by key, then a unique name for a speaking claim) and :917-919 (known limitation: merging by name across editions). Finding: the archive join can assign an archived listing to an existing person on a name match. Qodo's suggested fix: treat name, edition and company as a candidate only, and link after an account, back-link or curator confirms it.
