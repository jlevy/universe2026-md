---
type: is
id: is-01m5r3wbzkn4j5rpqkqtrr5jje
title: "PR8: prevent excluded cached homepages from triggering feed fetches"
kind: bug
status: closed
priority: 1
version: 4
delegate: codex@spud10.local
labels: []
dependencies: []
parent_id: is-01m5r0dg7wbj0tkm5653mnjwn8
hold: null
hold_until: null
created_at: 2026-10-24T23:28:06.131Z
updated_at: 2026-10-24T23:42:16.560Z
started_at: 2026-10-24T23:29:06.948Z
closed_at: 2026-10-24T23:42:16.559Z
close_reason: "Fixed in final source 983cb39279308c39ad75726db835f4ba55e016a2. Final gate: 209 tests passed in 90.21s; Ruff passed; BasedPyright 0 errors. Excluded-feed regressions: 40 focused tests passed, including test_exclusion_added_after_caching_blocks_feed_requests_and_replaces_stale_entries. Published fixed disposition: https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368954078 ; original thread resolved and verified."
resolution: null
duplicate_of: null
---
High Qodo finding https://github.com/jlevy/universe2026-md/pull/8#discussion_r4368927645 (72840989-1d6e-4a10-b13d-6c21ae57a9c5), source769652b. enrich_social derives feed URLs from all cached homepages before CLI scrub, allowing an excluded site owner feed to be requested and persisted. Apply existing normalized website exclusion policy before deriving/fetching/saving feeds; prove excluded destinations never reach FakeFetcher while retained sites still work.

## Notes

Local fix653d31de74b8bcea9ecfd32a01e2f6d1254621e6 on codex/dataset-excluded-feed-fetch from source769652b. enrich_social screens each cached homepage through the existing normalized website-ID removal fingerprint before deriving feed URLs. Feeds are freshly fetched only for retained sites and replace the saved feed map, removing excluded-only stale entries; shared feeds remain when retained sites reference them. Baseline regression failed on an excluded feed request. Postfix40focused policy/enrich/feed/SSRF tests pass0.64s, Ruffpass, basedpyright0errors/warnings. Regression covers caches created before exclusion, scheme/www normalization, ownhost and offdomain excluded feeds never requested, stale cache removed, retained public feed content preserved and shared-feed ownership policy. Only enrich.py/newtest changed; no transport modifications or external fetches. Coordinator owns source integration, finalfullgate, CI, disposition, closure and sync.
