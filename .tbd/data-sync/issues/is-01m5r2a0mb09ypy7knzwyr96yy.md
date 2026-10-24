---
type: is
id: is-01m5r2a0mb09ypy7knzwyr96yy
title: Allow contract-validated dot-prefixed public artifact filenames
kind: bug
status: open
priority: 1
version: 1
labels: []
dependencies: []
parent_id: is-01m5r0s3ra9dqavam413mc7cxv
created_at: 2026-10-24T23:00:36.106Z
updated_at: 2026-10-24T23:00:36.106Z
---
Full-KB Pages assembly rejects legitimate repositories/entirehq/.github.yaml because of the generic hidden-path guard. Permit regular artifact filenames under existing entity directories only when validated by the existing contract, retaining rejection of hidden directories, credentials, symlinks and unknown paths. Add regression and verify exact full-KB byte preservation.
