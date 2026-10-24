---
type: is
id: is-01m5qvs1twqvyffvc0eh0d3gkk
title: "PR #7 Q1 (https://github.com/jlevy/universe2026-md/pull/7#issuecomment-6389467968): exclusion-list open question treats hashing as privacy protection"
kind: bug
status: in_progress
priority: 2
version: 2
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvrnjs3fk2bn4m19jzjwrb
hold: null
hold_until: null
created_at: 2026-10-24T21:06:28.826Z
updated_at: 2026-10-24T21:06:36.207Z
started_at: 2026-10-24T21:06:36.206Z
---
Severity: Low (suggestion; Qodo's High-Level Assessment, not a flagged issue). PR jlevy/universe2026-md#7, review comment https://github.com/jlevy/universe2026-md/pull/7#issuecomment-6389467968 (PR Summary, High-Level Assessment, alternative 1 'Hashed exclusion identifiers' and its Recommendation). Location: docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:517-518 (open question on hashing the excluded list) and :409 (implementation checklist item for the excluded list). Qodo recommends resolving the public exclusion-list format before implementation and notes that unsalted hashes of predictable identifiers are recoverable, so hashing alone is not privacy protection. The open question currently frames a hash as a way to avoid republishing removed names.
