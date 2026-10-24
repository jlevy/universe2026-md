---
type: is
id: is-01m5qvmb3zh6y4vgmbk25fm92n
title: "PR #4 Qodo 2 (https://github.com/jlevy/universe2026-md/pull/4#discussion_r4368483004): compliance rules omit personal accounts"
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
created_at: 2026-10-24T21:03:54.494Z
updated_at: 2026-10-24T21:07:30.947Z
started_at: 2026-10-24T21:04:00.416Z
closed_at: 2026-10-24T21:07:30.946Z
close_reason: "fixed on setup/qodo in 'chore: flag personal accounts in the Qodo compliance rules': new rule 6 flags accounts or pages unrelated to the person's professional work and names the allowed work accounts. Confirmed: a TOML parse plus policy-coverage check of compliance_user_guidelines against docs/data-policy.md failed on this item before the commit and passes after. Wording matches jlevy/paraverse#4."
resolution: null
duplicate_of: null
---
Severity: Medium. PR #4, review https://github.com/jlevy/universe2026-md/pull/4#pullrequestreview-5639977183, comment https://github.com/jlevy/universe2026-md/pull/4#discussion_r4368483004 . File: .pr_agent.toml:33-34 (rule 4). docs/data-policy.md:68 excludes accounts and pages unrelated to a person's professional work, even when public; the source rule flags only non-public sources. Suggested fix: extend the source rule to personal accounts.
