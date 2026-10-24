---
type: is
id: is-01m5qyq7dqfx8dz3b9dqs8m94j
title: Restore the previous KB when final publication rename fails
kind: bug
status: in_progress
priority: 2
version: 2
delegate: codex@spud10.local
labels: []
dependencies: []
hold: null
hold_until: null
created_at: 2026-10-24T21:57:54.727Z
updated_at: 2026-10-24T21:59:18.264Z
started_at: 2026-10-24T21:59:18.254Z
---
Independent final readiness review, Medium correctness finding. At pipeline/src/universe_kb/build.py:940-948 (source 8a72bccc2e055afda67c51a489b681c0f4f41409), write_kb renames the existing KB to .kb-previous-kb, then renames staging into place. If the second rename raises, the exception removes staging but never restores the previous KB. An isolated failure injection using the immutable write_kb function and a real temporary directory returned kb_exists_after_failed_swap=false and previous_copy_survives=true. The previous generated output remains recoverable, so deferred follow-up is acceptable for this publication. Fix: restore the prior output on failed final rename, preserve the backup if restoration fails, and add a failure-injection regression proving that the public KB path retains the previous complete dataset. Reproduction artifact: external review scratch dataset-readiness/swap-failure.json; source and injected state are fully specified here.
