---
type: is
id: is-01m5qvs2mspkhrswvt2sqqs91b
title: "PR #7 W2: plan Non-Goals 'Sensitive inferences, which no source may be used to infer or store' reads against the verbatim self-written bio rule"
kind: bug
status: closed
priority: 2
version: 6
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvrnjs3fk2bn4m19jzjwrb
hold: null
hold_until: null
created_at: 2026-10-24T21:06:29.656Z
updated_at: 2026-10-24T21:10:30.645Z
started_at: 2026-10-24T21:06:36.669Z
closed_at: 2026-10-24T21:10:30.644Z
close_reason: "fixed on PR #5 (docs/research-and-plans) in commit 'docs: align the plan's sensitive-attribute non-goal with the data policy': docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md Non-Goals now reads 'Added sensitive attributes, which the kb never adds, derives or infers from any source; only text a person wrote about themselves and published, kept verbatim, may state one:' with the list unchanged. Confirmed by grep (old wording gone) and flowmark -w 88 -s --smartquotes --check (pass)."
resolution: null
duplicate_of: null
---
Severity: Low (wording). Raised by the addressing agent at the coordinator's request, on PR jlevy/universe2026-md#7 (review context https://github.com/jlevy/universe2026-md/pull/7#issuecomment-6389465958). Location: docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:72-76 (Non-Goals). 'Which no source may be used to infer or store' sits awkwardly against docs/data-policy.md:58-65 and :107-108, which keep self-written public bio text verbatim even when it states a sensitive attribute; the policy forbids adding, deriving or inferring such attributes, not storing a person's own verbatim text. Owning layer: lines 72-76 come from commit 'docs: add research, architecture and plans for the dataset' on PR #5 (docs/research-and-plans), not from PR #7's diff, so the fix lands on PR #5. Related: u26-u4kq (PR #3 Qodo 1, escalated) may change the verbatim-bio rule; the new wording should follow its outcome.

## Notes

Disposition: deferred to PR #5 (docs/research-and-plans), the layer that owns plan lines 72-76 (commit 'docs: add research, architecture and plans for the dataset'). Waits on the coordinator landing the wording on PR #5 and restacking, and on the outcome of u26-u4kq (PR #3 Qodo 1, escalated), which may change the verbatim-bio rule. Proposed wording for line 72, if the verbatim rule stands: '- **Added sensitive attributes**, which the kb never adds, derives or infers from any source; only text a person wrote about themselves and published, kept verbatim, may state one:' (list items unchanged).
