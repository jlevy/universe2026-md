---
type: is
id: is-01m5r0k8015tqw91n8x3v0xnfa
title: "PR8 #3 r4368746706: corroborate LinkedIn outbound ownership"
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
created_at: 2026-10-24T22:30:41.407Z
updated_at: 2026-10-24T22:34:35.271Z
started_at: 2026-10-24T22:31:08.808Z
closed_at: 2026-10-24T22:34:35.259Z
close_reason: "Fixed in local commit 3babcab5ca446821cdd5bfef294f3f5f7f06cf92. Anonymized tests reproduce baseline defects and pass after fixes: LinkedIn requires independent ownership corroboration, identity resolution gathers owners and rejects ambiguity, shared feeds require one owner. Focused people/profile/identity pytest: 29 passed in 0.53s; full Ruff passed and BasedPyright reported 0 errors/warnings. Coordinator owns push, shared tbd sync and final integrated gates."
resolution: null
duplicate_of: null
---
High; pipeline/src/universe_kb/profile_sources.py fill_linkedin promotes arbitrary outbound bio links to owner identity. Require independent ownership corroboration. Review: https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368746706
