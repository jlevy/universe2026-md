---
type: is
id: is-01m5r7btbfsv2zkvf3bcsbx41y
title: "PR13 Qodo 4: verify graph metadata against validated artifact identities"
kind: bug
status: in_progress
priority: 2
version: 2
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0s3ra9dqavam413mc7cxv
hold: null
hold_until: null
created_at: 2026-10-25T00:28:58.094Z
updated_at: 2026-10-25T00:30:48.355Z
started_at: 2026-10-25T00:30:48.354Z
---
Qodo Medium finding at pinned PR13 head c6d11c23af31c247250d2c6bf4d0a55bf4da69d6.
Original review: https://github.com/jlevy/universe2026-md/pull/13#pullrequestreview-5640712248
Original finding: https://github.com/jlevy/universe2026-md/pull/13#discussion_r4369039663
Qodo finding UUID: 2b306b04-60a2-4d39-b574-959d406146fd

Problem: build_site trusts nonempty graph node IDs/kinds and copied paths without proving they match validated artifact identities; published counts and indexes can therefore be wrong.

Acceptance: Derive expected ID, kind and path identities from validated artifacts, including embedded event days and taxonomy terms, and reject missing, extra, duplicate or mismatched graph claims before generating manifests/indexes. Add negative regressions and verify the actual KB still publishes. Identity writer owns implementation and publisher Windows surface.

Coordinator owns final integration, CI, disposition publication, closure and full/push tbd sync.
