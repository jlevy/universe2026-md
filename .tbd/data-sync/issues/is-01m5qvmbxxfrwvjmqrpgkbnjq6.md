---
type: is
id: is-01m5qvmbxxfrwvjmqrpgkbnjq6
title: "PR #4 Qodo 4 (https://github.com/jlevy/universe2026-md/pull/4#discussion_r4368483007): scraped-profile rule omits scraper bookkeeping"
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
created_at: 2026-10-24T21:03:55.318Z
updated_at: 2026-10-24T21:07:32.103Z
started_at: 2026-10-24T21:04:01.125Z
closed_at: 2026-10-24T21:07:32.101Z
close_reason: "fixed on setup/qodo in 'chore: flag scraper bookkeeping in the Qodo compliance rules': rule 4 now also flags scraper bookkeeping that describes no one. Confirmed: a TOML parse plus policy-coverage check of compliance_user_guidelines against docs/data-policy.md failed on this item before the commit and passes after. jlevy/paraverse#4 has the same gap in its rule 4 (its policy has the same sentence); reported to the coordinator for propagation."
resolution: null
duplicate_of: null
---
Severity: Medium. PR #4, review https://github.com/jlevy/universe2026-md/pull/4#pullrequestreview-5639977183, comment https://github.com/jlevy/universe2026-md/pull/4#discussion_r4368483007 . File: .pr_agent.toml:33-34 (rule 4). docs/data-policy.md:54-57 requires stripping scraper bookkeeping that describes no one, along with other people's data; the rule flags only data about other people. Suggested fix: extend the scraped-profile rule to scraper bookkeeping.
