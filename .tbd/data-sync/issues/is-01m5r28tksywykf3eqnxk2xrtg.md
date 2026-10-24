---
type: is
id: is-01m5r28tksywykf3eqnxk2xrtg
title: "PR9 summary #3: assign company websites to authoritative organization owners"
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
created_at: 2026-10-24T22:59:57.175Z
updated_at: 2026-10-24T23:00:16.463Z
started_at: 2026-10-24T23:00:16.461Z
---
Medium; pipeline/src/universe_kb/build.py link_websites changes kind to company but leaves the employee as owner. Match a unique organization by authoritative website host/domain, keep wrapper and model owners consistent, reject ambiguous ownership, and prevent arbitrary site account claims. Review https://github.com/jlevy/universe2026-md/pull/9#issuecomment-6390280458 finding #3.
