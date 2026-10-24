---
type: is
id: is-01m5qvsgw2y9hm7mtw8whm4cka
title: "PR #1 Qodo 2 (https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484965): Codex ignores the closing reminder's plain stdout"
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
created_at: 2026-10-24T21:06:44.224Z
updated_at: 2026-10-24T21:07:07.320Z
started_at: 2026-10-24T21:06:52.922Z
---
Severity: Medium (Qodo 'Remediation recommended'). PR #1, review https://github.com/jlevy/universe2026-md/pull/1#pullrequestreview-5639981352, comment https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484965 .

Files: .codex/hooks.json:35-44, .codex/tbd-closing-reminder.sh:37-47. The PostToolUse hook prints `tbd closing` output as plain stdout. Codex hooks docs, PostToolUse: plain text on stdout is ignored; context must come back as JSON hookSpecificOutput.additionalContext. So the reminder never reaches a Codex agent.

The Claude copy (.claude/hooks/tbd-closing-reminder.sh, wired at .claude/settings.json:41) has the same limitation: Claude Code docs say plain stdout from most events, PostToolUse included, goes to the debug log, and only UserPromptSubmit, SessionStart and a few others add it to context. The upstream fix should cover both surfaces.

Generated: tbd 0.10.0 TBD_CLOSE_PROTOCOL_SCRIPT. Related upstream discussion: https://github.com/jlevy/tbd/issues/179 (open question on stdout vs additionalContext for the closing reminder).

Disposition: deferred to upstream tbd. Waits on a tbd release whose closing-reminder hook emits PostToolUse JSON with hookSpecificOutput.additionalContext, then `tbd setup` in this repo. Same finding on jlevy/paraverse#1 (Qodo 1, discussion_r4368485574).

## Notes

Disposition on PR #1 (head 6d1b7eb): deferred. The file is written verbatim by tbd setup 0.10.0 (the latest get-tbd release), so a local edit is lost on the next setup; the fix belongs in tbd's templates. Left open, waiting on a tbd release with the fix, then a tbd setup run in this repo. No upstream jlevy/tbd issue filed yet; the coordinator may file one and link it here.
