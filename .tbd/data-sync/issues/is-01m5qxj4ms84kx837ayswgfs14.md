---
type: is
id: is-01m5qxj4ms84kx837ayswgfs14
title: Historical KB data-quality review O-4
kind: bug
status: closed
priority: 1
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qxfr4vqrasqe241q6mwftf
hold: null
hold_until: null
created_at: 2026-10-24T21:37:39.481Z
updated_at: 2026-10-24T21:52:59.592Z
started_at: 2026-10-24T21:40:38.923Z
closed_at: 2026-10-24T21:52:59.591Z
close_reason: "Fixed supported duplicates in 86da470dab5454d8233f8672160680c7a10c58ef: OrgIndex now preserves curated aliases and pins over mention-only entries with deterministic precedence; organizations.yaml merges evidenced spelling variants and splits combined labels. Rebuilt organization count 329 to 311; obsolete Principal/Cathay/OTTO/Entire/KPMG/combined-label records absent; regression covers aliases and preserves distinct Prudential companies. Declined blanket suffix merging and preserved potentially distinct parent/subsidiary pairs Manulife/Investment Management, Mercedes-Benz/Group, TD/Bank, Prudential/Financial without identity proof. Validation: full pytest 140 passed, final targeted 40 passed, Ruff clean, typecheck 0 errors, rebuilt 5092/5092 schema-valid artifacts."
resolution: null
duplicate_of: null
---
Severity: High. Reconcile finding O-4 in docs/project/research/review-2026-10-24-universe-kb-data-quality.md, linked from PR #5 (https://github.com/jlevy/universe2026-md/pull/5). Record exact current code/data evidence and one disposition before publishing the data import. Refer to the existing review for the issue and proposed fix; do not duplicate third-party identity or removal context here.
