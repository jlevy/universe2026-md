---
type: is
id: is-01m5qvs27d907m8p6tacqrqvc4
title: "PR #7 W1: plan says no one can ask to be removed, contradicting the data policy and architecture doc"
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
created_at: 2026-10-24T21:06:29.228Z
updated_at: 2026-10-24T21:06:35.836Z
started_at: 2026-10-24T21:06:35.835Z
---
Severity: Medium (factual contradiction in a plan). Raised by the addressing agent at the coordinator's request, on PR jlevy/universe2026-md#7 (review context https://github.com/jlevy/universe2026-md/pull/7#issuecomment-6389465958). Location: docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:298 ('There is also no way for anyone to ask to be removed.') and :338 ('curation/people.yaml gains an excluded list'). Contradicts docs/data-policy.md:84-96 (Removal Requests: anyone may ask by issue or privately through a maintainer) and docs/project/architecture/arch-2026-10-24-conference-kb.md:646-648 (a maintainer adds the person to the person-exclusion field in curation/people.yaml). Owned by this PR's diff.
