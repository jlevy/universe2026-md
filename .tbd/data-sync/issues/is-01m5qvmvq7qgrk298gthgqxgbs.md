---
type: is
id: is-01m5qvmvq7qgrk298gthgqxgbs
title: "PR #3 Qodo 1 (https://github.com/jlevy/universe2026-md/pull/3#discussion_r4368484024): sensitive details can enter the dataset via verbatim self-written bios"
kind: bug
status: in_progress
priority: 2
version: 3
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvmk0g58be4sb3y4mgvnq0
hold: null
hold_until: null
created_at: 2026-10-24T21:04:11.492Z
updated_at: 2026-10-24T21:06:20.658Z
started_at: 2026-10-24T21:04:45.411Z
---
Severity: High (Action required). PR jlevy/universe2026-md#3, review https://github.com/jlevy/universe2026-md/pull/3#pullrequestreview-5639979389 , finding 1, comment https://github.com/jlevy/universe2026-md/pull/3#discussion_r4368484024 . Location: docs/data-policy.md:58-65 (Added sensitive personal attributes, with the self-written public bio exception) and docs/data-policy.md:107-108 (checklist). Qodo says the policy prohibits sensitive attributes but permits them in self-written public bios kept verbatim; it suggests a redaction rule for sensitive attributes in those bios. Changing the verbatim-bio rule is a design decision the user made explicitly; escalated.

## Notes

Escalated to the coordinator: rebutting a High finding that would change a user-decided rule (self-written public bios kept verbatim, pronouns included). Recommendation: rebut. The prohibition covers adding, deriving or inferring (docs/data-policy.md:58-62, 79-80); the exception keeps only the person's own published text verbatim (63-65); the checklist states the same rule (107-108). Alternatives: adopt Qodo's redaction rule (changes the user's rule; must change jlevy/paraverse#3 identically, and the pipeline's bio handling), or a wording-only clarification in both repos. Left open until decided.
