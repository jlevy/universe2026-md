---
type: is
id: is-01m5r0k8jjp5xpty3j52ms8nv6
title: "PR8 #10 r4368746727: reject ambiguous identity matches"
kind: bug
status: closed
priority: 1
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0dg7wbj0tkm5653mnjwn8
hold: null
hold_until: null
created_at: 2026-10-24T22:30:42.001Z
updated_at: 2026-10-24T22:34:35.280Z
started_at: 2026-10-24T22:31:09.091Z
closed_at: 2026-10-24T22:34:35.280Z
close_reason: "Fixed in local commit 3babcab5ca446821cdd5bfef294f3f5f7f06cf92. Anonymized tests reproduce baseline defects and pass after fixes: LinkedIn requires independent ownership corroboration, identity resolution gathers owners and rejects ambiguity, shared feeds require one owner. Focused people/profile/identity pytest: 29 passed in 0.53s; full Ruff passed and BasedPyright reported 0 errors/warnings. Coordinator owns push, shared tbd sync and final integrated gates."
resolution: null
duplicate_of: null
---
Medium; pipeline/src/universe_kb/people.py PeopleIndex.resolve chooses one of multiple account owners through set iteration. Gather candidates and reject conflicts. Review: https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368746727
