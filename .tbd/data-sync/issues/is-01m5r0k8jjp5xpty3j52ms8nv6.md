---
type: is
id: is-01m5r0k8jjp5xpty3j52ms8nv6
title: "PR8 #10 r4368746727: reject ambiguous identity matches"
kind: bug
status: in_progress
priority: 1
version: 2
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0dg7wbj0tkm5653mnjwn8
hold: null
hold_until: null
created_at: 2026-10-24T22:30:42.001Z
updated_at: 2026-10-24T22:31:09.092Z
started_at: 2026-10-24T22:31:09.091Z
---
Medium; pipeline/src/universe_kb/people.py PeopleIndex.resolve chooses one of multiple account owners through set iteration. Gather candidates and reject conflicts. Review: https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368746727
