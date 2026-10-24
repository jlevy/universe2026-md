---
type: is
id: is-01m5qzkv1x4bt4cyej9f4f2x3r
title: Carry manifest declaration through enrich-packages verification
kind: bug
status: in_progress
priority: 2
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
hold: null
hold_until: null
created_at: 2026-10-24T22:13:32.331Z
updated_at: 2026-10-24T22:24:23.617Z
started_at: 2026-10-24T22:13:54.333Z
---
Independent final review, Medium correctness regression at pipeline/src/universe_kb/enrich.py in immutable 8a72bccc2e055afda67c51a489b681c0f4f41409. The O2 fix added mandatory manifest provenance in verify_package and updated repo_packages, but enrich_packages still calls verify_package without filename and does not persist declared_in. Offline synthetic FakeWeb reproduction with package.json declaring acme-tools and registry backlink to acme/tools yields declared=1, verified=0, reason=no_manifest_declaration, declared_in=null. Fix: pass filename to verify_package and include declared_in in each saved record; add an offline CLI-helper regression. Existing saved import is unaffected; this prevents future enrichment from losing legitimate package-source relationships.

## Notes

Implementation verified and published in pipeline PR https://github.com/jlevy/universe2026-md/pull/8 (b529b99c12eca75090c5173bf799e2eba36c40df), with rebuilt data PR https://github.com/jlevy/universe2026-md/pull/9 (c6b4faa9a6df7e176bd265f3c3f706d31ec3c3ef), formal stack 11 rooted on main. Original and intermediate imports are absent from published ancestry.

Exact published pipeline tree: 145 tests passed in 68.88 seconds; Ruff clean; BasedPyright 0 errors. Two offline rebuilds are byte-identical; 5,092/5,092 artifacts valid; 5,522 nodes and 25,544 edges; 577 stored and attached valid, current bios; 23 persistent rejected owner/account pairs. Contact and excluded-identity scans return zero findings; raw policy reapplication changes zero files. Regressions prove rejection persists after raw pruning, the same account remains available to a correct owner, failed publication restores the previous KB without overwriting a concurrent complete tree, and enrich-packages preserves declaration provenance.

The committed review addendum reconciles all 50 historical findings: 17 fixed and 33 Medium/Low follow-ups with individual open beads. Awaiting final review and merge; implementation beads remain open until the owning layer lands. Aggregate audit and disposition evidence is retained privately outside disposable scratch. Public entries and reports contain no removal identity, reason or date.
