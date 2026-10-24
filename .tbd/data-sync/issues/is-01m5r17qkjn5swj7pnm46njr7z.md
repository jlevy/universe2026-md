---
type: is
id: is-01m5r17qkjn5swj7pnm46njr7z
title: Build and deploy the public dataset Pages package
kind: task
status: in_progress
priority: 1
version: 2
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0s3ra9dqavam413mc7cxv
hold: null
hold_until: null
created_at: 2026-10-24T22:41:52.753Z
updated_at: 2026-10-24T22:42:01.803Z
started_at: 2026-10-24T22:42:01.801Z
---
Prepare .github/workflows/pages.yml and docs/publishing.md for read-only PR builds and main-only Pages deployment of the validated public KB and complete data-access skill. Pin official actions, install frozen, keep Pages/OIDC authority only in a separate deployment job, and upload only the publisher output. No remote mutation in this delegated task.
