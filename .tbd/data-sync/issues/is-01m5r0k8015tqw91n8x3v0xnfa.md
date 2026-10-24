---
type: is
id: is-01m5r0k8015tqw91n8x3v0xnfa
title: "PR8 #3 r4368746706: corroborate LinkedIn outbound ownership"
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
created_at: 2026-10-24T22:30:41.407Z
updated_at: 2026-10-24T22:31:08.809Z
started_at: 2026-10-24T22:31:08.808Z
---
High; pipeline/src/universe_kb/profile_sources.py fill_linkedin promotes arbitrary outbound bio links to owner identity. Require independent ownership corroboration. Review: https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368746706
