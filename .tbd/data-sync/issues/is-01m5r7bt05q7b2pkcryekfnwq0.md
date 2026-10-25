---
type: is
id: is-01m5r7bt05q7b2pkcryekfnwq0
title: "PR13 Qodo 3: gate Pages publication on compiled schema drift"
kind: bug
status: closed
priority: 2
version: 3
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0s3ra9dqavam413mc7cxv
hold: null
hold_until: null
created_at: 2026-10-25T00:28:57.733Z
updated_at: 2026-10-25T00:43:10.717Z
started_at: 2026-10-25T00:31:25.566Z
closed_at: 2026-10-25T00:43:10.717Z
close_reason: Merged PR13 at maina82367923bee34147da575dbd0cef17b5bc285a8, exactreviewedtree7612ccc. Final CI40147259367 passed243tests plus schema/Ruff/types and realpublicpackage5001files5407entities; KBarchiveSHAd0db0d23a6246330ba1c69291b46e8089b879be3f1058050a78f081c6da2fc1a matches fullbyte-roundtrip. Independent senior5640795770/security5640796730/correctness5640798282 clear. All5Qodo findings fixed, original-ID dispositions issuecomment6391532058,5/5threadsresolved andfreshsweepclear.
resolution: null
duplicate_of: null
---
Qodo Medium finding at pinned PR13 head c6d11c23af31c247250d2c6bf4d0a55bf4da69d6.
Original review: https://github.com/jlevy/universe2026-md/pull/13#pullrequestreview-5640712248
Original finding: https://github.com/jlevy/universe2026-md/pull/13#discussion_r4369039661
Qodo finding UUID: dba9b68a-ef6a-4b11-be87-24659b3cc71d

Problem: The Pages workflow omits the existing schemas --check gate, allowing compiled schema copies to drift from Python contracts.

Acceptance: Run universe-kb schemas --check in the frozen build environment before publication. Confirm the workflow uses the gate and current compiled schemas pass; confirm a contract/schema mismatch causes a failing gate. Primary owns implementation.

Coordinator owns final integration, CI, disposition publication, closure and full/push tbd sync.
