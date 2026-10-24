---
type: is
id: is-01m5r38j16tmhgwamrr4r73k2j
title: "PR #8 Qodo r4368847383: remove sensitive attributes from hashtag posts"
kind: bug
status: in_progress
priority: 1
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
hold: null
hold_until: null
created_at: 2026-10-24T23:17:16.965Z
updated_at: 2026-10-24T23:19:48.024Z
started_at: 2026-10-24T23:17:46.257Z
---
High security finding at policy.py:_hashtag_timeline, reviewed at source8ec8747. https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368847383. Attendance timelines currently redact contacts but retain sensitive personal clauses outside the owner-written bio exception. Apply the existing sensitive clause sanitizer before cache publication, preserving only supported explicit attendance evidence and its source metadata; add synthetic RED/GREEN regressions and snapshot publication checks. Coordinator owns raw backfill and final rebuilt imports.

## Notes

Source fix ready for coordinator integration: ff5717c88c9947206fcbd12a32f604c9155b00f5, parent approved safe8ec8747. Only policy.py and synthetic tests changed. RED4 failures/1pass; GREEN35 focused policy/privacy/snapshot/sensitive tests passed; Ruff clean; BasedPyright0errors0warnings. Sensitive post clauses are removed before cache retention; explicit attendance must exist in both original and surviving text. Supported quote source/id/timestamp preserved. Coordinator must apply sanitize-raw/backfill and final rebuilt snapshot before claiming the published raw corpus clean. No raw/KB mutation or push performed in source fix branch.
