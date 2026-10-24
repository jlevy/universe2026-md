---
type: is
id: is-01m5r0gnbtfrjazvpeag4fkdtn
title: "PR8 #4: block private destinations and unsafe redirects (discussion_r4368746710)"
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
created_at: 2026-10-24T22:29:16.793Z
updated_at: 2026-10-24T22:29:27.747Z
started_at: 2026-10-24T22:29:27.734Z
---
High SSRF finding https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368746710. enrich.py:500 gathers arbitrary profile websites; snapshot.py Fetcher follows automatic redirects. Validate public HTTP(S) destinations and every DNS answer, pin connections to validated IPs, and validate every redirect while preserving public APIs.
