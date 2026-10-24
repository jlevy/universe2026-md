---
type: is
id: is-01m5qvp0rwrrqm5nzqy3fbkv3h
title: "PR #2 Qodo S1 (https://github.com/jlevy/universe2026-md/pull/2#issuecomment-6389397864): pin the softschema CLI as a project dependency"
kind: task
status: open
priority: 3
version: 3
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvnghe11k3vpan1j8x4504
hold: null
hold_until: null
created_at: 2026-10-24T21:04:49.434Z
updated_at: 2026-10-24T21:05:27.332Z
started_at: 2026-10-24T21:05:01.305Z
---
Suggestion (no severity; Qodo PR summary, High-Level Assessment, alternative approach 1). PR: jlevy/universe2026-md#2. Source: https://github.com/jlevy/universe2026-md/pull/2#issuecomment-6389397864. The ID S1 was assigned by the addressing agent, since the summary has no IDs.

Suggestion: if consistent softschema behavior is required, add a separately pinned project CLI dependency, because the skill's uvx and npx fallbacks resolve the latest release and this PR does not install the CLI.

Context: this PR installs only the two generated skill files and the repo has no build system at this layer. The architecture doc added by PR #5 (docs/project/architecture/arch-2026-10-24-conference-kb.md:894-895) plans pipeline/pyproject.toml with a 14-day exclude-newer cool-off and an exact softschema pin; that work is tracked by u26-2xaq (Crawl, enrichment and build pipeline).

## Notes

Disposition: deferred (owning work: u26-2xaq, the crawl, enrichment and build pipeline). Outside PR #2's scope: this PR adds only the two generated skill files, and the repo has no build system at this layer. The pinned dependency is already planned: arch-2026-10-24-conference-kb.md:894-895 (added by PR #5) says pipeline/pyproject.toml pins softschema to an exact version with a 14-day exclude-newer cool-off. Waits on: the pipeline PR under u26-2xaq; close this bead when that pin lands.
