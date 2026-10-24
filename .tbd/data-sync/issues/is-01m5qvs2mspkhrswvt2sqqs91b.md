---
type: is
id: is-01m5qvs2mspkhrswvt2sqqs91b
title: "PR #7 W2: plan Non-Goals 'Sensitive inferences, which no source may be used to infer or store' reads against the verbatim self-written bio rule"
kind: bug
status: in_progress
priority: 2
version: 2
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvrnjs3fk2bn4m19jzjwrb
hold: null
hold_until: null
created_at: 2026-10-24T21:06:29.656Z
updated_at: 2026-10-24T21:06:36.671Z
started_at: 2026-10-24T21:06:36.669Z
---
Severity: Low (wording). Raised by the addressing agent at the coordinator's request, on PR jlevy/universe2026-md#7 (review context https://github.com/jlevy/universe2026-md/pull/7#issuecomment-6389465958). Location: docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:72-76 (Non-Goals). 'Which no source may be used to infer or store' sits awkwardly against docs/data-policy.md:58-65 and :107-108, which keep self-written public bio text verbatim even when it states a sensitive attribute; the policy forbids adding, deriving or inferring such attributes, not storing a person's own verbatim text. Owning layer: lines 72-76 come from commit 'docs: add research, architecture and plans for the dataset' on PR #5 (docs/research-and-plans), not from PR #7's diff, so the fix lands on PR #5. Related: u26-u4kq (PR #3 Qodo 1, escalated) may change the verbatim-bio rule; the new wording should follow its outcome.
