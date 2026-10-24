---
type: is
id: is-01m5r0hj31xxcz3xfta9scngwg
title: "PR8 build findings: catalog filters, day labels and publication locking"
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
created_at: 2026-10-24T22:29:46.208Z
updated_at: 2026-10-24T23:00:59.841Z
started_at: 2026-10-24T22:32:40.807Z
closed_at: 2026-10-24T23:00:59.839Z
close_reason: Fixed in reviewed safe pipeline 8ec8747. Current test rows filtered before entity construction; edition-specific highlights and pre/post agenda labels covered by RED/GREEN regressions; shared directory publication lock, unique recovery and injected two-writer failure tests pass. Full source suite190 passed, Ruff and types clean. Data rebuilt and byte-identical across5008files.
resolution: null
duplicate_of: null
---
Own PR8 Qodo #12 r4368746741 current catalog tests/unscheduled rows, #14 r4368746746 fringe-day labels, #15 r4368746749 concurrent KB publication backup safety; PR9 #6 r4368747867 year-mismatched highlights. Fix build.py with meaningful synthetic and failure-injection regressions; generated KB rebuild after all owners integrate.
