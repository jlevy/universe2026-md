---
title: Nuevo Foundation
softschema:
  contract: paraverse.conference:Organization/v2
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: enforced
organization:
  id: org:nuevo-foundation
  name: Nuevo Foundation
  roles:
  - affiliation
  description: We inspire kids to be curious, confident, and courageous by discovering the world of STEM.
  descriptions:
  - text: We inspire kids to be curious, confident, and courageous by discovering the world of STEM.
    basis: github
  website: https://nuevofoundation.org
  github: gh:nuevofoundation
  accounts:
  - gh:nuevofoundation
  - acct:x/nuevofoundation
  websites:
  - site:nuevofoundation.org
  people:
  - person:bea-mendez-gandica
  - person:jeremiah-isaacson
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1777613357747001v3F9
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1697650998115001DwEv
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: beagandica
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: website
    url: https://nuevofoundation.org
    record_id: https://nuevofoundation.org
    retrieved_at: '2026-10-24T08:43:43Z'
    snapshot: raw/websites/org-homepages.json
---
# Nuevo Foundation

Website: <https://nuevofoundation.org>

## People

- [Bea Mendez Gandica](../people/bea-mendez-gandica.md)
- [Jeremiah Isaacson](../people/jeremiah-isaacson.md)
