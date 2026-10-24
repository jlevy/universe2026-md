---
type: is
id: is-01m5qvsjcm03ze89aheq2yvrxj
title: "PR #1 Qodo 5 (https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484972): tbd skill closing checklist demands a push for no-code tasks"
kind: bug
status: open
priority: 2
version: 5
delegate: null
labels:
  - upstream-tbd
dependencies: []
parent_id: is-01m5qvqz78z0vsp7d5vm0rd34h
hold: blocked
hold_until: null
created_at: 2026-10-24T21:06:45.779Z
updated_at: 2026-10-24T21:57:24.493Z
started_at: 2026-10-24T21:06:53.965Z
---
Severity: Medium (Qodo 'Remediation recommended'). PR #1, review https://github.com/jlevy/universe2026-md/pull/1#pullrequestreview-5639981352, comment https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484972 .

Files: .agents/skills/tbd/SKILL.md:254-267 and the identical .claude/skills/tbd/SKILL.md. The "CRITICAL: Session Closing Protocol" checklist (commit, push, gh pr checks --watch, tbd close, tbd sync) applies to every session, with no condition for tasks that change no code, such as a review or an investigation. The skill already gates the push on github-editing (asks first without the grant), so the user keeps control of pushes, but the commit and CI-watch steps are still unconditional.

Generated: SKILL.md is tbd's own skill text, rewritten by every tbd setup; `tbd closing` prints the same protocol.

Disposition: deferred to upstream tbd. Waits on a tbd release that limits the commit, push and CI steps to sessions that changed code (bead close and tbd sync still apply), then `tbd setup` in this repo. This is a design choice in tbd's closing protocol; the decision belongs upstream. No counterpart on jlevy/paraverse#1's Qodo review; the same files are there.

## Notes

Disposition on PR #1 (head 6d1b7eb): deferred. The file is written verbatim by tbd setup 0.10.0 (the latest get-tbd release), so a local edit is lost on the next setup; the fix belongs in tbd's templates. Left open, waiting on a tbd release with the fix, then a tbd setup run in this repo. No upstream jlevy/tbd issue filed yet; the coordinator may file one and link it here.

Upstream follow-up: https://github.com/jlevy/tbd/issues/327. Generated copies remain unchanged; adoption waits on an upstream release and tbd setup refresh. Full review dispositions and replies are published on PR #1.
