---
type: is
id: is-01m5qvs1twqvyffvc0eh0d3gkk
title: "PR #7 Q1 (https://github.com/jlevy/universe2026-md/pull/7#issuecomment-6389467968): exclusion-list open question treats hashing as privacy protection"
kind: bug
status: closed
priority: 2
version: 3
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvrnjs3fk2bn4m19jzjwrb
hold: null
hold_until: null
created_at: 2026-10-24T21:06:28.826Z
updated_at: 2026-10-24T21:08:24.572Z
started_at: 2026-10-24T21:06:36.206Z
closed_at: 2026-10-24T21:08:24.571Z
close_reason: "fixed in commit 'docs(plan): note that a plain hash does not hide the excluded names' on docs/people-intake-plan (local 90d709c, SHA changes on restack): the open question now asks for the public excluded list's format, says a plain hash of a predictable ID or handle is recoverable by hashing candidates, and asks for it to be settled before the list is built; the implementation checklist item waits on it. The format itself stays an open question for the maintainers. Confirmed by /private/tmp/claude-502/-Users-levy-wrk-github-paraverse/d31a7712-52d0-48af-a28f-fa903f3a5198/scratchpad/review/u7/check-u7.sh Q1 (3 checks fail at e449de5, pass after) and flowmark --check."
resolution: null
duplicate_of: null
---
Severity: Low (suggestion; Qodo's High-Level Assessment, not a flagged issue). PR jlevy/universe2026-md#7, review comment https://github.com/jlevy/universe2026-md/pull/7#issuecomment-6389467968 (PR Summary, High-Level Assessment, alternative 1 'Hashed exclusion identifiers' and its Recommendation). Location: docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:517-518 (open question on hashing the excluded list) and :409 (implementation checklist item for the excluded list). Qodo recommends resolving the public exclusion-list format before implementation and notes that unsalted hashes of predictable identifiers are recoverable, so hashing alone is not privacy protection. The open question currently frames a hash as a way to avoid republishing removed names.
