---
type: is
id: is-01m5qvw4hvmk8cdksh75s2zcg6
title: "PR #5 Qodo 1 (https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488137): the pilot's hidden-simulation arm runs on speakers without simulation consent"
kind: bug
status: closed
priority: 1
version: 4
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvvbg15jk7fs2w0tbxdcds
hold: null
hold_until: null
created_at: 2026-10-24T21:08:09.914Z
updated_at: 2026-10-24T21:13:45.021Z
started_at: 2026-10-24T21:08:19.292Z
closed_at: 2026-10-24T21:13:45.019Z
close_reason: "Disposition: fixed (Qodo option 1: arm (c) contingent on explicit simulation consent from both people; the project owner's open decision on whether hidden scoring counts as Cited is kept as the only other gate, unchanged in substance). Commit 'docs: gate the pilot's hidden-simulation arm on consent' on docs/research-and-plans. research-2026-10-24-simulated-conference-avatars.md: step 4 now runs arm (c) only for pairs in which both speakers opted in through simulation_consent, or for every pair once the owner decides hidden scoring counts as Cited, and until then compares (a) and (b) alone; the intro limits the safety claim to the graph and card arms; the simulation_consent paragraph and the Next Steps decision say hidden scoring may not run without consent until decided. Confirmed by grep (the old 'It is safe with current data' sentence is gone; the gate sentence is present in step 4) and flowmark -w 88 -s --smartquotes --check (pass). Not escalated: the fix accepts the finding and leaves the owner's open decision open."
resolution: null
duplicate_of: null
---
Severity: High (Qodo: Action required; Bug, Correctness). Review: https://github.com/jlevy/universe2026-md/pull/5#pullrequestreview-5639988396. PR: jlevy/universe2026-md#5. Comment: https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488137. Files: docs/project/research/research-2026-10-24-simulated-conference-avatars.md:962-968 (Recommended First Experiment, arm (c) hidden simulation between pairs of 2026 speakers) and :623-639 (simulation_consent defaults to none; 'Simulation should check simulation_consent alone'). Finding: the first experiment runs person-specific simulated exchanges for speakers whose simulation_consent is none, against the doc's own consent gate (also Key Insights: being a published speaker is not consent to be simulated). Qodo's suggested fix: make the exchange arm contingent on explicit simulation consent from both people, or use archetypes; keep the graph and cited-card arms.

## Notes

Disposition: fixed (Qodo option 1: arm (c) contingent on explicit simulation consent from both people; the project owner's open decision on whether hidden scoring counts as Cited is kept as the only other gate, unchanged in substance). Commit 'docs: gate the pilot's hidden-simulation arm on consent' on docs/research-and-plans. research-2026-10-24-simulated-conference-avatars.md: step 4 now runs arm (c) only for pairs in which both speakers opted in through simulation_consent, or for every pair once the owner decides hidden scoring counts as Cited, and until then compares (a) and (b) alone; the intro limits the safety claim to the graph and card arms; the simulation_consent paragraph and the Next Steps decision say hidden scoring may not run without consent until decided. Confirmed by grep (the old 'It is safe with current data' sentence is gone; the gate sentence is present in step 4) and flowmark -w 88 -s --smartquotes --check (pass). Not escalated: the fix accepts the finding and leaves the owner's open decision open.
