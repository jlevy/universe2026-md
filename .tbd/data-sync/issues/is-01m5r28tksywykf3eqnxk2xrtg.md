---
type: is
id: is-01m5r28tksywykf3eqnxk2xrtg
title: "PR9 summary #3: assign company websites to authoritative organization owners"
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
created_at: 2026-10-24T22:59:57.175Z
updated_at: 2026-10-24T23:04:14.313Z
started_at: 2026-10-24T23:00:16.461Z
closed_at: 2026-10-24T23:04:14.312Z
close_reason: Duplicate of coordinator-created u26-9bhs; retained only that finding bead for implementation and disposition.
resolution: null
duplicate_of: null
---
Medium; pipeline/src/universe_kb/build.py link_websites changes kind to company but leaves the employee as owner. Match a unique organization by authoritative website host/domain, keep wrapper and model owners consistent, reject ambiguous ownership, and prevent arbitrary site account claims. Review https://github.com/jlevy/universe2026-md/pull/9#issuecomment-6390280458 finding #3.
