---
type: is
id: is-01m5r1nmwsajcbmctdn9n20yhr
title: Bound decompressed archive metadata before tar parsing
kind: bug
status: closed
priority: 1
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0s3ra9dqavam413mc7cxv
hold: null
hold_until: null
created_at: 2026-10-24T22:49:28.728Z
updated_at: 2026-10-24T23:01:01.246Z
started_at: 2026-10-24T22:50:11.850Z
closed_at: 2026-10-24T23:01:01.245Z
close_reason: "Fixed abd34fb (integrated e7d34b5): all decompressed tar bytes bounded before metadata parsing. Malicious PAX regression RED on old code/GREEN new. Independent strong reviewer reproduced rejection and verified staging cleanup;7 focused tests and197 integrated tests pass."
resolution: null
duplicate_of: null
---
Confirmed strong review finding in .agents/skills/universe2026-data/scripts/download.py: tarfile consumes PAX/GNU metadata before yielding members, so summing yielded member sizes fails to bound actual decompression. Bound all decompressed tar bytes into private staging before invoking tarfile; regression uses oversized metadata with a tiny regular payload and must fail the prior implementation.
