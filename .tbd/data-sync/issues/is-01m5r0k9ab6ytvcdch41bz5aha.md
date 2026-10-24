---
type: is
id: is-01m5r0k9ab6ytvcdch41bz5aha
title: "PR8 #11 r4368746735: reject ambiguous feed authorship"
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
created_at: 2026-10-24T22:30:42.762Z
updated_at: 2026-10-24T22:31:09.362Z
started_at: 2026-10-24T22:31:09.361Z
---
Medium; pipeline/src/universe_kb/profile_sources.py writing_from_feeds silently attributes a shared feed to the last website owner. Require one unique owner. Review: https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368746735
