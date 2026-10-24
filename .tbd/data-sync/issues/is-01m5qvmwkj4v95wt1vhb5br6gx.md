---
type: is
id: is-01m5qvmwkj4v95wt1vhb5br6gx
title: "PR #3 Qodo 2 (https://github.com/jlevy/universe2026-md/pull/3#discussion_r4368484028): README and policy describe kb/ and pipeline/ that are absent at this layer"
kind: bug
status: closed
priority: 2
version: 3
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvmk0g58be4sb3y4mgvnq0
hold: null
hold_until: null
created_at: 2026-10-24T21:04:12.400Z
updated_at: 2026-10-24T21:06:20.084Z
started_at: 2026-10-24T21:04:45.976Z
closed_at: 2026-10-24T21:06:20.083Z
close_reason: "Rebutted (coordinator-authorized): kb/ and pipeline/ land in later layers of stack #6 (pipeline layer, branch kb/pipeline, bead u26-2xaq; built KB, branch kb/data, bead u26-uff0). The README, AGENTS.md layout and removal procedure describe the repository as the stack leaves it; the pipeline layer provides pipeline/README.md, the universe-kb build command and the exclude list in pipeline/curation/people.yaml. Holds only if those layers join the stack before it merges. Disposition reply prepared for the coordinator to post."
resolution: null
duplicate_of: null
---
Severity: High (Action required). PR jlevy/universe2026-md#3, review https://github.com/jlevy/universe2026-md/pull/3#pullrequestreview-5639979389 , finding 2, comment https://github.com/jlevy/universe2026-md/pull/3#discussion_r4368484028 . Location: README.md:26-50 (derived directories, layout table, rebuilding), AGENTS.md:59-73 (repository layout), docs/data-policy.md:84-96 (removal requests). Qodo says pipeline/, kb/, curation data and the rebuild command are absent from the checkout. They land in later layers of the stack: the pipeline layer (branch kb/pipeline, bead u26-2xaq) and the built KB layer (branch kb/data, bead u26-uff0).
