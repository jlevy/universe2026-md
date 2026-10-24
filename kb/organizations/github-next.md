---
title: GitHub Next
softschema:
  contract: paraverse.conference:Organization/v1
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: permissive
organization:
  id: org:github-next
  name: GitHub Next
  roles:
  - affiliation
  description: Exploring the future of software development
  descriptions:
  - text: Exploring the future of software development
    basis: github
  - text: A team of researchers and engineers at GitHub prototyping the tools, workflows, and ideas that
      will shape the future of software development.
    basis: website
  logo_url: https://githubnext.com/og/default.png
  website: https://githubnext.com
  github: gh:githubnext
  accounts:
  - gh:githubnext
  - acct:x/githubnext
  related_organizations:
  - org:github
  sources:
  - system: curation
    snapshot: curation/organizations.yaml
  - system: github
    url: https://api.github.com/graphql
    record_id: MaggieAppleton
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: website
    url: https://githubnext.com
    record_id: https://githubnext.com
    retrieved_at: '2026-10-24T08:43:43Z'
    snapshot: raw/websites/org-homepages.json
---
# GitHub Next

Website: <https://githubnext.com>
