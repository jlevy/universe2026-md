---
type: is
id: is-01m5qvw4xpke4ab566p0dgzhp9
title: "PR #5 Qodo 2 (https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488122): the completed KB plan points at pipeline/ and kb/, which land in later layers"
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
created_at: 2026-10-24T21:08:10.293Z
updated_at: 2026-10-24T21:14:01.065Z
started_at: 2026-10-24T21:08:19.839Z
---
Severity: Medium (Qodo: Remediation recommended; Bug, Correctness). Review: https://github.com/jlevy/universe2026-md/pull/5#pullrequestreview-5639988396. PR: jlevy/universe2026-md#5. Comment: https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488122. Files: docs/project/specs/done/plan-2026-10-24-universe-knowledge-base.md:7-17 (Status: Implemented; records in kb/, pipeline in pipeline/) and docs/README.md:36-42. Finding: at this layer neither pipeline/ nor kb/ exists, so the plan's build and validation instructions cannot be run until the later stack layers land. Qodo's suggested fix: say the implementation depends on later layers, or defer the completed-plan claim and index entry.

## Notes

Disposition: deferred to the pipeline and KB layers of this stack. Valid at this layer: docs/project/specs/done/plan-2026-10-24-universe-knowledge-base.md:7-17 and docs/README.md describe pipeline/ and kb/, which this PR does not contain. The PR body already says these docs describe the pipeline (pipeline/) and KB (kb/) that land in the next layers, and the paths and commands are still being built there, so no doc edit here. Waits on: u26-2xaq (crawl, enrichment and build pipeline) and u26-uff0 (built KB) landing; then check the plan's paths, commands and counts against what landed (including the people and attendee counts, which differ between docs: 591 people with 13 attendees in the knowledge-graph research and data-quality review, 590 in the deeper-enrichment plan) and close.
