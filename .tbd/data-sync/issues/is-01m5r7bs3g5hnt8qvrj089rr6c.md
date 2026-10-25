---
type: is
id: is-01m5r7bs3g5hnt8qvrj089rr6c
title: "PR13 Qodo 1: resolve archive paths from redirected manifest URLs"
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
created_at: 2026-10-25T00:28:56.783Z
updated_at: 2026-10-25T00:30:47.718Z
started_at: 2026-10-25T00:30:33.508Z
---
Qodo Medium finding at pinned PR13 head c6d11c23af31c247250d2c6bf4d0a55bf4da69d6.
Original review: https://github.com/jlevy/universe2026-md/pull/13#pullrequestreview-5640712248
Original finding: https://github.com/jlevy/universe2026-md/pull/13#discussion_r4369039656
Qodo finding UUID: e040f3e9-9c5b-46bf-bd94-b87817675b9f

Problem: download_dataset resolves the archive path against the original manifest URL rather than the final redirected response URL.

Acceptance: Retain the final manifest response URL and derive the archive site-root base from it. Regression: redirect the manifest to another host or directory and assert the requested archive URL uses that final location. Preserve checksum and extraction safeguards. Network writer owns implementation.

Coordinator owns final integration, CI, disposition publication, closure and full/push tbd sync.

## Notes

Fixed locally in86ec78ca93b9e3156a8d870c884a777389e58fdd on codex/access-download-fixes. Downloader retains final HTTPS manifest response URL; archive paths resolve from that deployment root, including root-relative paths in release manifests. Regression reproduced wrong original host before fix, then ordinary+pinned redirect downloads succeed. Focused downloader/publication tests:12passed3.34s; Ruffclean,basedpyright0errors/warnings. Only download.py/newtest_download_review.py changed; no network calls/fullsuite per assigned host budget. Coordinator owns integration/CI/dispositions/closure/sync.
