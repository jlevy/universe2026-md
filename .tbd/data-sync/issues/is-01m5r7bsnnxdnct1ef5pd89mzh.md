---
type: is
id: is-01m5r7bsnnxdnct1ef5pd89mzh
title: "PR13 Qodo 2: support empty download destinations on Windows"
kind: bug
status: in_progress
priority: 2
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0s3ra9dqavam413mc7cxv
hold: null
hold_until: null
created_at: 2026-10-25T00:28:57.396Z
updated_at: 2026-10-25T00:30:48.008Z
started_at: 2026-10-25T00:30:33.771Z
---
Qodo Medium finding at pinned PR13 head c6d11c23af31c247250d2c6bf4d0a55bf4da69d6.
Original review: https://github.com/jlevy/universe2026-md/pull/13#pullrequestreview-5640712248
Original finding: https://github.com/jlevy/universe2026-md/pull/13#discussion_r4369039658
Qodo finding UUID: 095fec45-5c41-4740-8e33-1b88c241f705

Problem: An existing empty destination is accepted, but staged Path.rename over that directory fails on Windows.

Acceptance: Choose and document one portable destination contract: require an absent destination on all platforms, or safely remove a confirmed-empty destination immediately before the staged rename. Test Windows-existing-directory behavior, retain nonempty destinations unchanged, and preserve staged failure safety. Network writer owns downloader implementation; coordinate any publisher Windows surface with identity writer.

Coordinator owns final integration, CI, disposition publication, closure and full/push tbd sync.

## Notes

Fixed locally in86ec78ca93b9e3156a8d870c884a777389e58fdd on codex/access-download-fixes. Record whether destination initially accepted empty; rmdir immediately before stagedrename supports Windows and refuses new contents without recursive deletion. Regression simulates Windows rejecting existing directory and now succeeds. Fault injection adds user file during download; failure leaves bytes intact and cleans staging. Initial nonempty directory refused before any fetch. Focused downloader/publication tests:12passed3.34s; Ruffclean,basedpyright0errors/warnings. Windows semantics simulated, no native Windows run/fullsuite per host budget. Coordinator owns integration/CI/dispositions/closure/sync.
