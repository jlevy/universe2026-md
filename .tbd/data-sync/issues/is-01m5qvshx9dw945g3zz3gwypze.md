---
type: is
id: is-01m5qvshx9dw945g3zz3gwypze
title: "PR #1 Qodo 4 (https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484968): closing reminder exits silently when jq is missing"
kind: bug
status: open
priority: 2
version: 4
delegate: claude-code@spud10.local
labels:
  - upstream-tbd
dependencies: []
parent_id: is-01m5qvqz78z0vsp7d5vm0rd34h
hold: blocked
hold_until: null
created_at: 2026-10-24T21:06:45.289Z
updated_at: 2026-10-24T21:07:08.130Z
started_at: 2026-10-24T21:06:53.631Z
---
Severity: Medium (Qodo 'Remediation recommended'). PR #1, review https://github.com/jlevy/universe2026-md/pull/1#pullrequestreview-5639981352, comment https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484968 .

Files: .claude/hooks/tbd-closing-reminder.sh:27-31 and the identical .codex/tbd-closing-reminder.sh. The hook parses its input with jq without checking jq exists. Without jq, command is empty, the push test fails, and the script exits 0 with no reminder.

Reproduced: with PATH holding only cat and git, piping {"tool_input":{"command":"git push origin setup/tbd"}} into the Claude and Codex copies exits 0 with 0 bytes of stdout and only "jq: command not found" on stderr; with jq present the same input prints the 1351-byte closing checklist.

Generated: tbd 0.10.0 TBD_CLOSE_PROTOCOL_SCRIPT.

Disposition: deferred to upstream tbd. Waits on a tbd release whose closing-reminder hook checks for jq (or parses without it) and warns instead of exiting silently, then `tbd setup` in this repo. Same finding on jlevy/paraverse#1 (Qodo 4, discussion_r4368485583).

## Notes

Disposition on PR #1 (head 6d1b7eb): deferred. The file is written verbatim by tbd setup 0.10.0 (the latest get-tbd release), so a local edit is lost on the next setup; the fix belongs in tbd's templates. Left open, waiting on a tbd release with the fix, then a tbd setup run in this repo. No upstream jlevy/tbd issue filed yet; the coordinator may file one and link it here.
