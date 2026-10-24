---
type: is
id: is-01m5qyq7dqfx8dz3b9dqs8m94j
title: Restore the previous KB when final publication rename fails
kind: bug
status: in_progress
priority: 2
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
hold: null
hold_until: null
created_at: 2026-10-24T21:57:54.727Z
updated_at: 2026-10-24T22:24:23.319Z
started_at: 2026-10-24T21:59:18.254Z
---
Independent final readiness review, Medium correctness finding. At pipeline/src/universe_kb/build.py:940-948 (source 8a72bccc2e055afda67c51a489b681c0f4f41409), write_kb renames the existing KB to .kb-previous-kb, then renames staging into place. If the second rename raises, the exception removes staging but never restores the previous KB. An isolated failure injection using the immutable write_kb function and a real temporary directory returned kb_exists_after_failed_swap=false and previous_copy_survives=true. The previous generated output remains recoverable, so deferred follow-up is acceptable for this publication. Fix: restore the prior output on failed final rename, preserve the backup if restoration fails, and add a failure-injection regression proving that the public KB path retains the previous complete dataset. Reproduction artifact: external review scratch dataset-readiness/swap-failure.json; source and injected state are fully specified here.

## Notes

Implementation verified and published in pipeline PR https://github.com/jlevy/universe2026-md/pull/8 (b529b99c12eca75090c5173bf799e2eba36c40df), with rebuilt data PR https://github.com/jlevy/universe2026-md/pull/9 (c6b4faa9a6df7e176bd265f3c3f706d31ec3c3ef), formal stack 11 rooted on main. Original and intermediate imports are absent from published ancestry.

Exact published pipeline tree: 145 tests passed in 68.88 seconds; Ruff clean; BasedPyright 0 errors. Two offline rebuilds are byte-identical; 5,092/5,092 artifacts valid; 5,522 nodes and 25,544 edges; 577 stored and attached valid, current bios; 23 persistent rejected owner/account pairs. Contact and excluded-identity scans return zero findings; raw policy reapplication changes zero files. Regressions prove rejection persists after raw pruning, the same account remains available to a correct owner, failed publication restores the previous KB without overwriting a concurrent complete tree, and enrich-packages preserves declaration provenance.

The committed review addendum reconciles all 50 historical findings: 17 fixed and 33 Medium/Low follow-ups with individual open beads. Awaiting final review and merge; implementation beads remain open until the owning layer lands. Aggregate audit and disposition evidence is retained privately outside disposable scratch. Public entries and reports contain no removal identity, reason or date.
