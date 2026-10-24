---
type: is
id: is-01m5qxht1zd12dg45e6sqcmy27
title: Historical KB data-quality review P-4
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
created_at: 2026-10-24T21:37:28.638Z
updated_at: 2026-10-24T21:52:59.318Z
started_at: 2026-10-24T21:40:38.889Z
closed_at: 2026-10-24T21:52:59.318Z
close_reason: "Fixed in local integration commit 86da470dab5454d8233f8672160680c7a10c58ef, pipeline/tests/test_data_quality.py regressions. Canonical organization-page facts, explicit LinkedIn size labeling, manifest-backed source links with no inferred registry publisher, stable catalog userRef identity, corroboration-only rel-me accounts, campus aliases/floor notes, catalog day labels, sentinel capacity filtering, and ambiguous organization mention suppression. RED cases reproduced; full pytest 140 passed (66.08s), post-review targeted 40 passed, Ruff clean, basedpyright 0 errors. Offline saved-source rebuild: 5092 artifacts valid, 0 invalid; duplicate userRefs 0, campus-external rooms 0, placeholder capacities 0, rel-me-only person accounts 0. Coordinator handles final consolidated publication."
resolution: null
duplicate_of: null
---
Severity: High. Reconcile finding P-4 in docs/project/research/review-2026-10-24-universe-kb-data-quality.md, linked from PR #5 (https://github.com/jlevy/universe2026-md/pull/5). Record exact current code/data evidence and one disposition before publishing the data import. Refer to the existing review for the issue and proposed fix; do not duplicate third-party identity or removal context here.
