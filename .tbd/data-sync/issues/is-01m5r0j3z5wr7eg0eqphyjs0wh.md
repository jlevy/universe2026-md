---
type: is
id: is-01m5r0j3z5wr7eg0eqphyjs0wh
title: "PR #8 Qodo 6: preserve bundle batches on interrupted regeneration"
kind: bug
status: in_progress
priority: 2
version: 2
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0dg7wbj0tkm5653mnjwn8
hold: null
hold_until: null
created_at: 2026-10-24T22:30:04.516Z
updated_at: 2026-10-24T22:30:25.206Z
started_at: 2026-10-24T22:30:25.205Z
---
Medium; pipeline/src/universe_kb/cli.py:147-154. https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368746715. Stage a complete replacement bundle set and publish with rollback; test interrupted writing and commit failure.
