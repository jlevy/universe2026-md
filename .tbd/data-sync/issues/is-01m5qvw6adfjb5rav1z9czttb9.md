---
type: is
id: is-01m5qvw6adfjb5rav1z9czttb9
title: "PR #5 Qodo 6 (https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488153): Phase 3 maps current X posts into attendance evidence without requiring the person's own statement of attendance"
kind: bug
status: closed
priority: 2
version: 4
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvvbg15jk7fs2w0tbxdcds
hold: null
hold_until: null
created_at: 2026-10-24T21:08:11.724Z
updated_at: 2026-10-24T21:13:47.243Z
started_at: 2026-10-24T21:08:23.714Z
closed_at: 2026-10-24T21:13:47.240Z
close_reason: "Disposition: fixed (as suggested). Commit 'docs: count only a stated attendance post as attendance evidence'. plan-2026-10-24-deeper-enrichment-sources.md: table B row 3 now says a person's own post saying they will attend can count as attendance evidence; Phase 3 maps a current X post into attendance evidence only when its author says in it that they will attend, as the data policy requires, and routes other posts and hashtags to writing and interests only. Confirmed by grep of the two attendance-evidence lines and flowmark -w 88 -s --smartquotes --check (pass)."
resolution: null
duplicate_of: null
---
Severity: Medium (Qodo: Remediation recommended; Bug, Correctness). Review: https://github.com/jlevy/universe2026-md/pull/5#pullrequestreview-5639988396. PR: jlevy/universe2026-md#5. Comment: https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488153. Files: docs/project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md:175-180 (table B priority 3: current X posts and hashtags so X posts can count as attendance evidence again) and :330-332 (Phase 3: map current X posts into attendance evidence). docs/data-policy.md (Unstated attendance): list someone as attending only if they said so publicly. Finding: as written, event discussion or a hashtag could become an attendee participation. Qodo's suggested fix: only the person's own post explicitly stating attendance creates attendance evidence; other posts and hashtags feed writing and interests only.

## Notes

Disposition: fixed (as suggested). Commit 'docs: count only a stated attendance post as attendance evidence'. plan-2026-10-24-deeper-enrichment-sources.md: table B row 3 now says a person's own post saying they will attend can count as attendance evidence; Phase 3 maps a current X post into attendance evidence only when its author says in it that they will attend, as the data policy requires, and routes other posts and hashtags to writing and interests only. Confirmed by grep of the two attendance-evidence lines and flowmark -w 88 -s --smartquotes --check (pass).
