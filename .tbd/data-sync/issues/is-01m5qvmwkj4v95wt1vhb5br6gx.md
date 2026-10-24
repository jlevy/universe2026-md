---
type: is
id: is-01m5qvmwkj4v95wt1vhb5br6gx
title: "PR #3 Qodo 2 (https://github.com/jlevy/universe2026-md/pull/3#discussion_r4368484028): README and policy describe kb/ and pipeline/ that are absent at this layer"
kind: bug
status: in_progress
priority: 2
version: 5
delegate: dataset-readiness
labels: []
dependencies: []
parent_id: is-01m5qvmk0g58be4sb3y4mgvnq0
hold: null
hold_until: null
created_at: 2026-10-24T21:04:12.400Z
updated_at: 2026-10-24T22:07:00.378Z
started_at: 2026-10-24T21:04:45.976Z
closed_at: null
close_reason: null
resolution: null
duplicate_of: null
---
Severity: High (Action required). PR jlevy/universe2026-md#3, review https://github.com/jlevy/universe2026-md/pull/3#pullrequestreview-5639979389 , finding 2, comment https://github.com/jlevy/universe2026-md/pull/3#discussion_r4368484028 . Location: README.md:26-50 (derived directories, layout table, rebuilding), AGENTS.md:59-73 (repository layout), docs/data-policy.md:84-96 (removal requests). Qodo says pipeline/, kb/, curation data and the rebuild command are absent from the checkout. They land in later layers of the stack: the pipeline layer (branch kb/pipeline, bead u26-2xaq) and the built KB layer (branch kb/data, bead u26-uff0).

## Notes

Reopened: Deferred pending the separately reviewed sanitized pipeline and generated KB imports. The documentation stack may land first by coordinator direction; the earlier conditional rebuttal did not establish that pipeline/ or kb/ exists at this head.
