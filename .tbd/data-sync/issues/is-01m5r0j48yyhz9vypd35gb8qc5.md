---
type: is
id: is-01m5r0j48yyhz9vypd35gb8qc5
title: "PR #8 Qodo 7: fail bios-merge when entries are rejected"
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
created_at: 2026-10-24T22:30:04.828Z
updated_at: 2026-10-24T22:30:25.215Z
started_at: 2026-10-24T22:30:25.215Z
---
Medium; pipeline/src/universe_kb/cli.py:169-174. https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368746716. Preserve JSON report and return nonzero on partial rejection; cover CLI exit status.
