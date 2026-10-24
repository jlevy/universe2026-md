---
type: is
id: is-01m5qvmbf06nqa53ve2s911ebj
title: "PR #4 Qodo 3 (https://github.com/jlevy/universe2026-md/pull/4#discussion_r4368483005): compliance rules omit the generated-text requirements"
kind: bug
status: closed
priority: 2
version: 3
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvm0q7v5dw9e24seyw57xk
hold: null
hold_until: null
created_at: 2026-10-24T21:03:54.847Z
updated_at: 2026-10-24T21:07:31.469Z
started_at: 2026-10-24T21:04:00.766Z
closed_at: 2026-10-24T21:07:31.465Z
close_reason: "fixed on setup/qodo in 'chore: check generated text in the Qodo compliance rules': new rule 7 flags model-written bios or summaries that do not cite their sources, say more than them, stray from professional facts, or do not record the model and an input hash. Confirmed: a TOML parse plus policy-coverage check of compliance_user_guidelines against docs/data-policy.md failed on this item before the commit and passes after. Wording matches jlevy/paraverse#4."
resolution: null
duplicate_of: null
---
Severity: Medium. PR #4, review https://github.com/jlevy/universe2026-md/pull/4#pullrequestreview-5639977183, comment https://github.com/jlevy/universe2026-md/pull/4#discussion_r4368483005 . File: .pr_agent.toml:26-32. docs/data-policy.md:74-82 (Generated Text) requires model-written bios and summaries to cite and stay within their sources, keep to professional facts without speculation, and record the model and an input hash; no compliance rule checks any of this. Suggested fix: add a generated-text rule.
