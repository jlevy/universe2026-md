---
type: is
id: is-01m5qzkv1x4bt4cyej9f4f2x3r
title: Carry manifest declaration through enrich-packages verification
kind: bug
status: open
priority: 2
version: 1
labels: []
dependencies: []
created_at: 2026-10-24T22:13:32.331Z
updated_at: 2026-10-24T22:13:32.331Z
---
Independent final review, Medium correctness regression at pipeline/src/universe_kb/enrich.py in immutable 8a72bccc2e055afda67c51a489b681c0f4f41409. The O2 fix added mandatory manifest provenance in verify_package and updated repo_packages, but enrich_packages still calls verify_package without filename and does not persist declared_in. Offline synthetic FakeWeb reproduction with package.json declaring acme-tools and registry backlink to acme/tools yields declared=1, verified=0, reason=no_manifest_declaration, declared_in=null. Fix: pass filename to verify_package and include declared_in in each saved record; add an offline CLI-helper regression. Existing saved import is unaffected; this prevents future enrichment from losing legitimate package-source relationships.
