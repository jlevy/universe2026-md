---
type: is
id: is-01m5qvshd90nrkkzwm2q0yeadk
title: "PR #1 Qodo 3 (https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484966): ensure-gh-cli.sh PATH change does not reach the agent"
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
created_at: 2026-10-24T21:06:44.775Z
updated_at: 2026-10-24T21:57:19.683Z
started_at: 2026-10-24T21:06:53.275Z
---
Severity: Medium (Qodo 'Remediation recommended'). PR #1, review https://github.com/jlevy/universe2026-md/pull/1#pullrequestreview-5639981352, comment https://github.com/jlevy/universe2026-md/pull/1#discussion_r4368484966 .

Files: .claude/scripts/ensure-gh-cli.sh:35,209-216,221-238 and the identical .codex/ensure-gh-cli.sh. Line 35 prepends ~/.local/bin to PATH inside the hook process only. The install writes ~/.local/bin/gh, and the "still not found in PATH" check (lines 221-226) and the shadowing warning (lines 228-238) both run against that private PATH, so they pass even when the agent's own PATH lacks ~/.local/bin or puts an older gh ahead of it. Later agent commands then find no gh, or the older gh the pin exists to replace, while the hook reported success.

Claude Code supports persisting env changes from SessionStart through CLAUDE_ENV_FILE (each later Bash command sources it); Codex needs an equivalent or an explicit path.

Generated: tbd 0.10.0 bundled docs/install/ensure-gh-cli.sh, rewritten by every tbd setup when use_gh_cli is true.

Disposition: deferred to upstream tbd. Waits on a tbd release whose ensure-gh-cli.sh checks the inherited PATH and, for Claude, writes the PATH update to CLAUDE_ENV_FILE (or warns explicitly), then `tbd setup` in this repo. No counterpart on jlevy/paraverse#1's Qodo review; the same files are there.

## Notes

Disposition on PR #1 (head 6d1b7eb): deferred. The file is written verbatim by tbd setup 0.10.0 (the latest get-tbd release), so a local edit is lost on the next setup; the fix belongs in tbd's templates. Left open, waiting on a tbd release with the fix, then a tbd setup run in this repo. No upstream jlevy/tbd issue filed yet; the coordinator may file one and link it here.

Upstream follow-up: https://github.com/jlevy/tbd/issues/327. Generated copies remain unchanged; adoption waits on an upstream release and tbd setup refresh. Full review dispositions and replies are published on PR #1.
