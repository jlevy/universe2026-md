---
type: is
id: is-01m5r38j16tmhgwamrr4r73k2j
title: "PR #8 Qodo r4368847383: remove sensitive attributes from hashtag posts"
kind: bug
status: in_progress
priority: 1
version: 2
delegate: codex@spud10.local
labels: []
dependencies: []
hold: null
hold_until: null
created_at: 2026-10-24T23:17:16.965Z
updated_at: 2026-10-24T23:17:46.259Z
started_at: 2026-10-24T23:17:46.257Z
---
High security finding at policy.py:_hashtag_timeline, reviewed at source8ec8747. https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368847383. Attendance timelines currently redact contacts but retain sensitive personal clauses outside the owner-written bio exception. Apply the existing sensitive clause sanitizer before cache publication, preserving only supported explicit attendance evidence and its source metadata; add synthetic RED/GREEN regressions and snapshot publication checks. Coordinator owns raw backfill and final rebuilt imports.
