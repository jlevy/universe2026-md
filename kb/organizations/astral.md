---
title: Astral
softschema:
  contract: paraverse.conference:Organization/v1
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: permissive
organization:
  id: org:astral
  name: Astral
  roles:
  - affiliation
  description: High-performance developer tools for the Python ecosystem, from @OpenAI.
  descriptions:
  - text: High-performance developer tools for the Python ecosystem, from @OpenAI.
    basis: github
  - text: 'Astral builds high-performance developer tools for the Python ecosystem: Ruff, ty, and uv,
      an extremely fast Python package manager, written in Rust.'
    basis: website
  logo_url: https://astral.sh/static/OpenGraph/Astral.jpg
  website: https://astral.sh
  github: gh:astral-sh
  accounts:
  - gh:astral-sh
  - acct:x/astral_sh
  sources:
  - system: github
    url: https://api.github.com/graphql
    record_id: woodruffw
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: website
    url: https://astral.sh
    record_id: https://astral.sh
    retrieved_at: '2026-10-24T08:43:43Z'
    snapshot: raw/websites/org-homepages.json
---
# Astral

Website: <https://astral.sh>
