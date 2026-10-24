---
type: is
id: is-01m5qvmwkj4v95wt1vhb5br6gx
title: "PR #3 Qodo 2 (https://github.com/jlevy/universe2026-md/pull/3#discussion_r4368484028): README and policy describe kb/ and pipeline/ that are absent at this layer"
kind: bug
status: open
priority: 2
version: 6
delegate: null
labels: []
dependencies: []
parent_id: is-01m5qvmk0g58be4sb3y4mgvnq0
hold: null
hold_until: null
created_at: 2026-10-24T21:04:12.400Z
updated_at: 2026-10-24T22:07:22.880Z
started_at: 2026-10-24T21:04:45.976Z
closed_at: null
close_reason: null
resolution: null
duplicate_of: null
---
Severity: High (Action required). PR jlevy/universe2026-md#3, review https://github.com/jlevy/universe2026-md/pull/3#pullrequestreview-5639979389 , finding 2, comment https://github.com/jlevy/universe2026-md/pull/3#discussion_r4368484028 . Location: README.md:26-50 (derived directories, layout table, rebuilding), AGENTS.md:59-73 (repository layout), docs/data-policy.md:84-96 (removal requests). Qodo says pipeline/, kb/, curation data and the rebuild command are absent from the checkout. They land in later layers of the stack: the pipeline layer (branch kb/pipeline, bead u26-2xaq) and the built KB layer (branch kb/data, bead u26-uff0).

## Notes

Disposition: deferred. The README rebuild and removal commands require the pending sanitized pipeline and built-KB imports. Those paths do not exist at documentation head 4dabee999bd2a52b4b19c374e843dd6b0470c44d. Verify reviewed safe imports have landed on main, then run an offline build and validation before closing. The earlier conditional rebuttal is superseded.
