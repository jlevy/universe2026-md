---
type: is
id: is-01m5qvw5kt3esxd48km8fhvrta
title: "PR #5 Qodo 4 (https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488133): Phase 3 runs G2 (priority 5) before the data-policy decision the plan requires"
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
created_at: 2026-10-24T21:08:11.001Z
updated_at: 2026-10-24T21:08:20.533Z
started_at: 2026-10-24T21:08:20.532Z
---
Severity: Medium (Qodo: Remediation recommended; Bug, Correctness). Review: https://github.com/jlevy/universe2026-md/pull/5#pullrequestreview-5639988396. PR: jlevy/universe2026-md#5. Comment: https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488133. Files: docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:181-193 (table B priority 5 is G2; G2, Crunchbase, Glassdoor and Owler need a policy decision before any run) and :326-332 (Phase 3: run priorities 1 to 6). docs/data-policy.md takes organization facts from an organization's own public pages. Finding: the paid-run step schedules G2 without making it conditional on that policy decision. Qodo's suggested fix: remove G2 from the unconditional run and add the policy decision as a prerequisite.
