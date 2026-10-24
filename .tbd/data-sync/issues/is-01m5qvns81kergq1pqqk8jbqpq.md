---
type: is
id: is-01m5qvns81kergq1pqqk8jbqpq
title: "PR #2 Qodo 1 (https://github.com/jlevy/universe2026-md/pull/2#discussion_r4368483018): skill allowed-tools does not cover the uvx/npx fallback runners"
kind: bug
status: open
priority: 2
version: 3
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvnghe11k3vpan1j8x4504
hold: null
hold_until: null
created_at: 2026-10-24T21:04:41.726Z
updated_at: 2026-10-24T21:05:26.515Z
started_at: 2026-10-24T21:05:01.297Z
---
Severity: Medium (Qodo: Remediation recommended; Bug, Reliability). PR: jlevy/universe2026-md#2. Review: https://github.com/jlevy/universe2026-md/pull/2#pullrequestreview-5639977233. Comment: https://github.com/jlevy/universe2026-md/pull/2#discussion_r4368483018.

Files: .claude/skills/softschema/SKILL.md:8 (allowed-tools: ["Bash(softschema:*)"]), .claude/skills/softschema/SKILL.md:29-42 (Pick One Runner First: softschema, else uvx softschema@latest, else npx -y softschema@latest), .agents/skills/softschema/SKILL.md:8 (identical mirror).

Finding: the Claude skill preapproves only direct softschema commands, while its runner selection falls back to uvx or npx when softschema is not on PATH, so on a fresh clone the fallback path (and the uvx --version / npx --version probes) needs a separate permission grant.

Both files are generated verbatim by softschema skill --install (DO NOT EDIT format=f02 marker at line 10). The template lives upstream in jlevy/softschema at skills/softschema/SKILL.md:8. softschema skill has no option that sets allowed-tools (only --brief, --scope, --agent, --dry-run, --install). The identical finding exists on jlevy/paraverse#2.

## Notes

Disposition: deferred (upstream softschema). Valid: allowed-tools (SKILL.md:8) covers only Bash(softschema:*), while the runner list (SKILL.md:34-36) falls back to uvx softschema@latest or npx -y softschema@latest, and the uvx/npx --version probes are not preapproved either.

No local fix on PR #2: both SKILL.md files are verbatim generator output (softschema skill --install --dry-run --scope project --agent portable --agent claude reports both files unchanged, softschema 0.8.0), they carry a DO NOT EDIT marker, and softschema skill has no option that sets allowed-tools. A local .claude/settings.json allow rule for uvx softschema@latest or npx -y softschema@latest would auto-approve running whichever release is newest, against the exact pin and 14-day cool-off the architecture doc plans (PR #5, arch-2026-10-24-conference-kb.md:894-895).

Waits on: an upstream softschema change to its skill template (jlevy/softschema skills/softschema/SKILL.md:8) that makes allowed-tools and the runner list agree, either with narrow package-specific patterns for its own fallbacks or with text that says the fallbacks prompt by design, and a release with it; then re-run softschema skill --install --scope project --agent portable --agent claude here. Same finding on jlevy/paraverse#2.
