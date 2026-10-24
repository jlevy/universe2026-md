---
type: is
id: is-01m5qvsga8rfwkc1ysmybhjhmk
title: "PR #1 Qodo 1 (https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484963): session hooks use cwd-relative script paths"
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
created_at: 2026-10-24T21:06:43.654Z
updated_at: 2026-10-24T21:57:15.888Z
started_at: 2026-10-24T21:06:52.552Z
---
Severity: Medium (Qodo 'Remediation recommended'). PR #1, review https://github.com/jlevy/universe2026-md/pull/1#pullrequestreview-5639981352, comment https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484963 .

Files: .claude/settings.json:9,18,30 and .codex/hooks.json:9,18,30,41. The SessionStart and PreCompact commands (`bash .claude/scripts/tbd-session.sh`, `bash .claude/scripts/ensure-gh-cli.sh`, and the .codex/ copies, plus the Codex PostToolUse `bash .codex/tbd-closing-reminder.sh`) use paths relative to the hook's working directory. Hooks run in the session's current directory, so a session started in, or a compaction after the agent moved into, a subdirectory cannot find the scripts.

Evidence: `cd .tbd && bash .claude/scripts/tbd-session.sh --brief` exits 127 with "No such file or directory" (same for .codex/). Codex hooks docs: commands run with the session cwd, and the docs advise against relative `.codex/...` paths because Codex may start from a subdirectory. Claude Code docs: hooks run in the current directory; use $CLAUDE_PROJECT_DIR. The generated Claude PostToolUse entry already uses "$CLAUDE_PROJECT_DIR"; the SessionStart/PreCompact entries do not.

Generated: tbd 0.10.0 constants CLAUDE_TBD_SESSION_COMMAND, GH_CLI_HOOK_ENTRY and getCodexHooksConfig(). tbd setup drops any tbd-session.sh entry and re-adds the relative form, so a local edit is lost on the next setup.

Disposition: deferred to upstream tbd. Waits on a tbd release whose generated hooks resolve scripts from the project root (Claude: "$CLAUDE_PROJECT_DIR"; Codex: `$(git rev-parse --show-toplevel)`), then `tbd setup` in this repo. Same finding on jlevy/paraverse#1 (Qodo 2, discussion_r4368485576).

## Notes

Disposition on PR #1 (head 6d1b7eb): deferred. The file is written verbatim by tbd setup 0.10.0 (the latest get-tbd release), so a local edit is lost on the next setup; the fix belongs in tbd's templates. Left open, waiting on a tbd release with the fix, then a tbd setup run in this repo. No upstream jlevy/tbd issue filed yet; the coordinator may file one and link it here.

Upstream follow-up: https://github.com/jlevy/tbd/issues/327. Generated copies remain unchanged; adoption waits on an upstream release and tbd setup refresh. Full review dispositions and replies are published on PR #1.
