---
title: Epic Dev Space
softschema:
  contract: paraverse.conference:Organization/v2
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: enforced
organization:
  id: org:epic-dev-space
  name: Epic Dev Space
  roles:
  - affiliation
  description: The organization hosting all the repositories for EpicWeb.dev, EpicReact.dev, and EpicAI.pro
    projects
  descriptions:
  - text: The organization hosting all the repositories for EpicWeb.dev, EpicReact.dev, and EpicAI.pro
      projects
    basis: github
  - text: Learn full-stack web development with Kent C. Dodds and the Epic Web instructors. Learn TypeScript,
      React, Node.js, and more through hands-on workshops.
    basis: website
  logo_url: https://www.epicweb.dev/api/og/default
  website: https://www.epicweb.dev
  github: gh:epicweb-dev
  accounts:
  - gh:epicweb-dev
  sources:
  - system: github
    url: https://api.github.com/graphql
    record_id: kentcdodds
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: website
    url: https://www.epicweb.dev
    record_id: https://www.epicweb.dev
    retrieved_at: '2026-10-24T08:43:43Z'
    snapshot: raw/websites/org-homepages.json
---
# Epic Dev Space

Website: <https://www.epicweb.dev>
