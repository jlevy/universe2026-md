---
title: Overmind
softschema:
  contract: paraverse.conference:Organization/v1
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: permissive
organization:
  id: org:overmind
  name: Overmind
  roles:
  - affiliation
  description: Simulate Terraform changes before deploy
  descriptions:
  - text: Simulate Terraform changes before deploy
    basis: github
  - text: Deploy infrastructure changes with confidence by simulating their impact before they go live.
      Full visibility into blast radius, risks, and expected outcomes.
    basis: website
  logo_url: https://cdn.prod.website-files.com/6241e92445c21f9c1245a940/699488f372776ac2f155e0a1_Home.jpg
  website: https://overmind.tech
  github: gh:overmindtech
  accounts:
  - gh:overmindtech
  people:
  - person:dylan-ratcliffe
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1755624535596001ehoJ
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: dylanratcliffe
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: website
    url: https://overmind.tech
    record_id: https://overmind.tech
    retrieved_at: '2026-10-24T08:43:43Z'
    snapshot: raw/websites/org-homepages.json
---
# Overmind

Website: <https://overmind.tech>

## People

- [Dylan Ratcliffe](../people/dylan-ratcliffe.md)
