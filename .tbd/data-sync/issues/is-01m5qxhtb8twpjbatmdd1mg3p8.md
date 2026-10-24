---
type: is
id: is-01m5qxhtb8twpjbatmdd1mg3p8
title: Historical KB data-quality review P-5
kind: bug
status: in_progress
priority: 1
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qxfr4vqrasqe241q6mwftf
hold: null
hold_until: null
created_at: 2026-10-24T21:37:28.935Z
updated_at: 2026-10-24T22:24:23.067Z
started_at: 2026-10-24T21:42:17.514Z
---
Severity: High. Reconcile finding P-5 in docs/project/research/review-2026-10-24-universe-kb-data-quality.md, linked from PR #5 (https://github.com/jlevy/universe2026-md/pull/5). Record exact current code/data evidence and one disposition before publishing the data import. Refer to the existing review for the issue and proposed fix; do not duplicate third-party identity or removal context here.

## Notes

Implementation verified and published in pipeline PR https://github.com/jlevy/universe2026-md/pull/8 (b529b99c12eca75090c5173bf799e2eba36c40df), with rebuilt data PR https://github.com/jlevy/universe2026-md/pull/9 (c6b4faa9a6df7e176bd265f3c3f706d31ec3c3ef), formal stack 11 rooted on main. Original and intermediate imports are absent from published ancestry.

Exact published pipeline tree: 145 tests passed in 68.88 seconds; Ruff clean; BasedPyright 0 errors. Two offline rebuilds are byte-identical; 5,092/5,092 artifacts valid; 5,522 nodes and 25,544 edges; 577 stored and attached valid, current bios; 23 persistent rejected owner/account pairs. Contact and excluded-identity scans return zero findings; raw policy reapplication changes zero files. Regressions prove rejection persists after raw pruning, the same account remains available to a correct owner, failed publication restores the previous KB without overwriting a concurrent complete tree, and enrich-packages preserves declaration provenance.

The committed review addendum reconciles all 50 historical findings: 17 fixed and 33 Medium/Low follow-ups with individual open beads. Awaiting final review and merge; implementation beads remain open until the owning layer lands. Aggregate audit and disposition evidence is retained privately outside disposable scratch. Public entries and reports contain no removal identity, reason or date.
