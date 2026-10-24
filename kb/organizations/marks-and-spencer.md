---
title: Marks and Spencer
softschema:
  contract: paraverse.conference:Organization/v1
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: permissive
organization:
  id: org:marks-and-spencer
  name: Marks and Spencer
  aliases:
  - M&S
  roles:
  - affiliation
  people:
  - person:tim-mason
  sources:
  - system: curation
    snapshot: curation/organizations.yaml
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1785161862192001xkAl
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: mason-tim
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Marks and Spencer

## People

- [Tim Mason](../people/tim-mason.md)
