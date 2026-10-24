---
type: is
id: is-01m5r28ty78szfpr92m651wphk
title: "PR9 summary #5: canonicalize tracked website URLs before IDs"
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
created_at: 2026-10-24T22:59:57.510Z
updated_at: 2026-10-24T23:00:16.958Z
started_at: 2026-10-24T23:00:16.953Z
---
Low; pipeline/src/universe_kb/people.py website_id and add_website retain tracking query strings including malformed second question marks, producing duplicate website/search/graph records. Drop website queries and fragments before registration while preserving query-addressed OTHER_PROFILE accounts. Review https://github.com/jlevy/universe2026-md/pull/9#issuecomment-6390280458 finding #5.
