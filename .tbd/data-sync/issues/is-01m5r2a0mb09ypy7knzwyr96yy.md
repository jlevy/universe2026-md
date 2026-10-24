---
type: is
id: is-01m5r2a0mb09ypy7knzwyr96yy
title: Allow contract-validated dot-prefixed public artifact filenames
kind: bug
status: in_progress
priority: 1
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0s3ra9dqavam413mc7cxv
hold: null
hold_until: null
created_at: 2026-10-24T23:00:36.106Z
updated_at: 2026-10-24T23:04:52.352Z
started_at: 2026-10-24T23:01:07.074Z
---
Full-KB Pages assembly rejects legitimate repositories/entirehq/.github.yaml because of the generic hidden-path guard. Permit regular artifact filenames under existing entity directories only when validated by the existing contract, retaining rejection of hidden directories, credentials, symlinks and unknown paths. Add regression and verify exact full-KB byte preservation.

## Notes

Local fix commit10cae2994b4562e1bf98273439c2a056a87bc3a5 on codex/dataset-access-hidden-artifacts from cfc98d0. Terminal regular .md/.yaml artifact filenames are accepted under existing public entity roots with no hidden ancestors; unchanged public allowlist and complete staged contract validation still gate publication. Hidden credentials/directories/unknown paths remain rejected. Positive .github.yaml regression failed before change and passed after, with negative tampered-contract and seven hidden-path cases. Focused publisher9pass, full suite199pass76.32s, fullRuffpass/type0/actionlintpass. Real corrected KB assembled:5008files4984artifacts5414entities; all source/copy/tar-member SHA256 maps identical including repositories/entirehq/.github.yaml. Archive4459129bytes SHA2567036419ad3ddde13ffa21626051f244c6a30beda5621717c59f6a3fd7807b4ea. Parent owns integration, strong review and CI; no remote mutations/sync. Workflow changed only the parent-approved comment about hidden artifacts.
