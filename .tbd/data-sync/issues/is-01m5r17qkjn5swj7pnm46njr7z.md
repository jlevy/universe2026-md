---
type: is
id: is-01m5r17qkjn5swj7pnm46njr7z
title: Build and deploy the public dataset Pages package
kind: task
status: in_progress
priority: 1
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0s3ra9dqavam413mc7cxv
hold: null
hold_until: null
created_at: 2026-10-24T22:41:52.753Z
updated_at: 2026-10-24T22:49:23.054Z
started_at: 2026-10-24T22:42:01.801Z
---
Prepare .github/workflows/pages.yml and docs/publishing.md for read-only PR builds and main-only Pages deployment of the validated public KB and complete data-access skill. Pin official actions, install frozen, keep Pages/OIDC authority only in a separate deployment job, and upload only the publisher output. No remote mutation in this delegated task.

## Notes

Local workflow/docs commit 7edea58673ec8c68f9bae860157bf24f4401c789 on codex/dataset-access-workflow from main11942e7. Separate read-only build and main-only Pages/OIDC deployment jobs; official actions SHA-pinned with releases older than 14 days, uv0.12.24 frozen wheels-only sync, no-install-project/PYTHONPATH source execution, no shared caches, PYTHONDONTWRITEBYTECODE to keep skill clean. actionlint passed; Flowmark/diff checks passed; config contract accepted valid workflow and rejected seven unsafe mutations. Publisher f2998bc copied read-only to external scratch: six tests pass on Python3.13.7; actual CLI fixture smoke verifies KB/skill archive sizes and SHA256; invalid missingKB returns exit1 with no publication. Coordinator owns integration, full-suite/CI, PR and any deployment approval/settings. No GitHub writes or sync performed. Leave open pending integration verification.
