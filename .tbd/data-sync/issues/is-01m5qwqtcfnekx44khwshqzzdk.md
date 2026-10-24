---
type: is
id: is-01m5qwqtcfnekx44khwshqzzdk
title: Finalize KB privacy exclusion and offline rebuild evidence
kind: bug
status: in_progress
priority: 1
version: 4
delegate: codex@spud10.local
labels: []
dependencies: []
hold: null
hold_until: null
created_at: 2026-10-24T21:23:17.006Z
updated_at: 2026-10-24T22:41:15.855Z
started_at: 2026-10-24T21:23:34.364Z
---

## Notes

New Qodo findings supersede the earlier clean-data claim for b529b99/c6b4faa. Source-only patch 2da81ce974f418686ac8306f840686663d780c34 addresses pipeline review findings 1, 2, 5, 8 and 13, and data findings 2 and 4. Seven scoped regression cases failed on old code; 34 now pass. The corpus test is intentionally deselected until coordinated raw backfill. Ruff is clean and BasedPyright reports 0 errors.

Expanded scanning detects 58 raw matches; curation, synthesis, tests and source each have zero. The patch enforces explicit typed-reference exemptions, contact validation for bios, malformed-entry/bundle rejections, professional README filtering, raw HTML sanitation and process-locked snapshot/manifest publication. Both Fetcher paths use the separately supplied network boundary.

Coordinator owns raw/synthesis cleanup, complete integration tests, offline rebuilds and fresh sanitized import reconstruction. The old b529b99/c6b4faa ancestry must also be absent from final publication. Do not publish the private patch branch or treat earlier review evidence as a current merge claim. Awaiting final review/merge; bead remains in progress.
