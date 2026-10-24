---
title: Block
softschema:
  contract: paraverse.conference:Organization/v2
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: enforced
organization:
  id: org:block
  name: Block
  roles:
  - affiliation
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1746242817811001G0Rf
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1694192487472001BR32
    retrieved_at: '2026-10-24T08:03:37Z'
    snapshot: raw/editions/universe23/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: angiejones
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Block
