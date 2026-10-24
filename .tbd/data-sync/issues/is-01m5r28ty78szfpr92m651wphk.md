---
type: is
id: is-01m5r28ty78szfpr92m651wphk
title: "PR9 summary #5: canonicalize tracked website URLs before IDs"
kind: bug
status: closed
priority: 2
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0dg7wbj0tkm5653mnjwn8
hold: null
hold_until: null
created_at: 2026-10-24T22:59:57.510Z
updated_at: 2026-10-24T23:04:14.575Z
started_at: 2026-10-24T23:00:16.953Z
closed_at: 2026-10-24T23:04:14.574Z
close_reason: Duplicate of coordinator-created u26-bhbm; retained only that finding bead for implementation and disposition.
resolution: null
duplicate_of: null
---
Low; pipeline/src/universe_kb/people.py website_id and add_website retain tracking query strings including malformed second question marks, producing duplicate website/search/graph records. Drop website queries and fragments before registration while preserving query-addressed OTHER_PROFILE accounts. Review https://github.com/jlevy/universe2026-md/pull/9#issuecomment-6390280458 finding #5.
