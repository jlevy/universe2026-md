---
type: is
id: is-01m5qvns81kergq1pqqk8jbqpq
title: "PR #2 Qodo 1 (https://github.com/jlevy/universe2026-md/pull/2#discussion_r4368483018): skill allowed-tools does not cover the uvx/npx fallback runners"
kind: bug
status: closed
priority: 2
version: 6
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvnghe11k3vpan1j8x4504
hold: null
hold_until: null
created_at: 2026-10-24T21:04:41.726Z
updated_at: 2026-10-24T21:11:08.909Z
started_at: 2026-10-24T21:05:01.297Z
closed_at: 2026-10-24T21:11:08.908Z
close_reason: "fixed in 'chore: pre-approve the softschema uvx and npx runners for Claude Code': .claude/settings.json now allows Bash(uvx softschema@latest:*) and Bash(npx -y softschema@latest:*); confirmed by the runner-rule check (fails before, passes after), tbd doctor, and a real tbd setup --auto run that keeps the block"
resolution: null
duplicate_of: null
---
Severity: Medium (Qodo: Remediation recommended; Bug, Reliability). PR: jlevy/universe2026-md#2. Review: https://github.com/jlevy/universe2026-md/pull/2#pullrequestreview-5639977233. Comment: https://github.com/jlevy/universe2026-md/pull/2#discussion_r4368483018.

Files: .claude/skills/softschema/SKILL.md:8 (allowed-tools: ["Bash(softschema:*)"]), .claude/skills/softschema/SKILL.md:29-42 (Pick One Runner First: softschema, else uvx softschema@latest, else npx -y softschema@latest), .agents/skills/softschema/SKILL.md:8 (identical mirror).

Finding: the Claude skill preapproves only direct softschema commands, while its runner selection falls back to uvx or npx when softschema is not on PATH, so on a fresh clone the fallback path (and the uvx --version / npx --version probes) needs a separate permission grant.

Both files are generated verbatim by softschema skill --install (DO NOT EDIT format=f02 marker at line 10). The template lives upstream in jlevy/softschema at skills/softschema/SKILL.md:8. softschema skill has no option that sets allowed-tools (only --brief, --scope, --agent, --dry-run, --install). The identical finding exists on jlevy/paraverse#2.

## Notes

Disposition: fixed (user decision relayed by the coordinator: pre-approve the @latest runners exactly as the skill writes them; supersedes the earlier deferral).

Commit: chore: pre-approve the softschema uvx and npx runners for Claude Code (eefa6e2 before the restack). It adds permissions.allow to .claude/settings.json with Bash(uvx softschema@latest:*) and Bash(npx -y softschema@latest:*) and keeps the tbd hooks. The Claude Code permissions docs say the :* suffix is equivalent to a trailing space-star wildcard. The generated SKILL.md files are unchanged.

Confirmed by: a check script (scratchpad check-runner-rules.sh) that requires every SS runner prefix in .claude/skills/softschema/SKILL.md to have a matching Bash rule failed before the change (uvx and npx prefixes uncovered) and passes after. tbd doctor exits 0 (its only warning is the existing AGENTS.md policy-grant difference from origin/main). tbd setup --auto, run for real in an isolated scratch clone, keeps the permissions block. A control run shows it reorders the two SessionStart hooks with or without this change. uvx softschema@0.8.1 skill --install --dry-run reports both SKILL.md files unchanged.

Caveat: Claude Code applies project allow rules only after the workspace trust dialog is accepted; the uvx --version and npx --version probes are not covered.
