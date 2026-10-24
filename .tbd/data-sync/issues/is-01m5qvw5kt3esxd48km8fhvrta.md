---
type: is
id: is-01m5qvw5kt3esxd48km8fhvrta
title: "PR #5 Qodo 4 (https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488133): Phase 3 runs G2 (priority 5) before the data-policy decision the plan requires"
kind: bug
status: closed
priority: 2
version: 4
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvvbg15jk7fs2w0tbxdcds
hold: null
hold_until: null
created_at: 2026-10-24T21:08:11.001Z
updated_at: 2026-10-24T21:13:46.076Z
started_at: 2026-10-24T21:08:20.532Z
closed_at: 2026-10-24T21:13:46.073Z
close_reason: "Disposition: fixed (as suggested). Commit 'docs: hold G2 and the outside-company datasets for a policy decision'. plan-2026-10-24-deeper-enrichment-sources.md Phase 3 now runs priorities 1 to 4 and 6; priority 5 (G2) and the Crunchbase, Glassdoor and Owler rows, including their three-input tests, wait on a new open question about outside organization facts; the Paid runs question now asks for 1 to 4 and 6. Confirmed by grep ('priorities 1 to 6' no longer appears) and flowmark -w 88 -s --smartquotes --check (pass)."
resolution: null
duplicate_of: null
---
Severity: Medium (Qodo: Remediation recommended; Bug, Correctness). Review: https://github.com/jlevy/universe2026-md/pull/5#pullrequestreview-5639988396. PR: jlevy/universe2026-md#5. Comment: https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488133. Files: docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:181-193 (table B priority 5 is G2; G2, Crunchbase, Glassdoor and Owler need a policy decision before any run) and :326-332 (Phase 3: run priorities 1 to 6). docs/data-policy.md takes organization facts from an organization's own public pages. Finding: the paid-run step schedules G2 without making it conditional on that policy decision. Qodo's suggested fix: remove G2 from the unconditional run and add the policy decision as a prerequisite.

## Notes

Disposition: fixed (as suggested). Commit 'docs: hold G2 and the outside-company datasets for a policy decision'. plan-2026-10-24-deeper-enrichment-sources.md Phase 3 now runs priorities 1 to 4 and 6; priority 5 (G2) and the Crunchbase, Glassdoor and Owler rows, including their three-input tests, wait on a new open question about outside organization facts; the Paid runs question now asks for 1 to 4 and 6. Confirmed by grep ('priorities 1 to 6' no longer appears) and flowmark -w 88 -s --smartquotes --check (pass).
