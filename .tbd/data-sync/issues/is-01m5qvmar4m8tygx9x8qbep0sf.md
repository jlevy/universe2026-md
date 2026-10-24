---
type: is
id: is-01m5qvmar4m8tygx9x8qbep0sf
title: "PR #4 Qodo 1 (https://github.com/jlevy/universe2026-md/pull/4#discussion_r4368483001): compliance rules omit unstated attendance"
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
created_at: 2026-10-24T21:03:54.115Z
updated_at: 2026-10-24T21:07:30.525Z
started_at: 2026-10-24T21:04:00.083Z
closed_at: 2026-10-24T21:07:30.520Z
close_reason: "fixed on setup/qodo in 'chore: flag unstated attendance in the Qodo compliance rules': new rule 5 flags attendance someone has not stated publicly (a like, a follow or another person's post is not enough; official-agenda speakers are allowed). Confirmed: a TOML parse plus policy-coverage check of compliance_user_guidelines against docs/data-policy.md failed on this item before the commit and passes after. Wording matches jlevy/paraverse#4."
resolution: null
duplicate_of: null
---
Severity: Medium (Qodo 'Remediation recommended'). PR #4, review https://github.com/jlevy/universe2026-md/pull/4#pullrequestreview-5639977183, comment https://github.com/jlevy/universe2026-md/pull/4#discussion_r4368483001 . File: .pr_agent.toml:26-27 (compliance_user_guidelines). docs/data-policy.md:66-67 forbids listing someone as attending unless they said so publicly (a like, a follow or another person's post is not enough); no compliance rule flags it. Suggested fix: add a rule for unstated attendance.
