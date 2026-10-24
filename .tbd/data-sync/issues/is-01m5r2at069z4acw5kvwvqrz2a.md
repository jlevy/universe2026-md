---
type: is
id: is-01m5r2at069z4acw5kvwvqrz2a
title: "PR9 summary5: canonicalize tracking website URLs without changing profile identities"
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
created_at: 2026-10-24T23:01:02.083Z
updated_at: 2026-10-24T23:25:17.187Z
started_at: 2026-10-24T23:04:15.353Z
closed_at: 2026-10-24T23:25:17.186Z
close_reason: "Fixed final source769652b: strip only known tracking parameters/fragments, including malformed secondary UTM suffix, while preserving meaningful case-sensitive query identities. Query-addressed profiles remain distinct. RED regression on old query-dropping code;37 focused and203 full tests pass."
resolution: null
duplicate_of: null
---
