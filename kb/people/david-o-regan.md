---
title: David O'Regan
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:david-o-regan
  name: David O'Regan
  given_name: David
  family_name: O'Regan
  job_title: Staff EM
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Staff EM
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: github_profile
    label: GitHub - Copilot
    evidence:
    - url: https://github.com/Oregand
      quote: GitHub - Copilot
  affiliation_label: GitHub
  bio: David O’Regan is a Senior Engineering Manager working on GitHub Copilot. Before joining GitHub,
    he led GitLab’s AI & ML group behind GitLab Duo and managed its Remote Development team. He has nearly
    a decade of engineering management experience across three companies and two continents. At oregand.github.io,
    David writes about AI, leadership, and how agents change the work of engineering managers. He’s an
    ENFJ with a bias for shipping.
  photo_url: https://static.rainfocus.com/github/universe26/att/1777571700465001GJZZ/attprofile/PXL_20250301_211418867-EDIT_1790203174672001EpW1.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1776970168128001LO8t
      ref: session:ldr1185d
  accounts:
  - gh:oregand
  - acct:linkedin/in/oregand7
  websites:
  - site:oregand.github.io
  github: gh:oregand
  github_resolution: resolved
  github_match: name
  profile: profile:david-o-regan
  featured: false
  sessions:
  - session: session:ldr1185d
    role: speaker
  mentions:
  - target: software:github-copilot
    text: GitHub Copilot
    field: bio
    method: gazetteer
  - target: software:gitlab
    text: GitLab
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1777571700465001GJZZ
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: Oregand
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# David O'Regan

Staff EM, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)

David O’Regan is a Senior Engineering Manager working on GitHub Copilot. Before joining GitHub, he led GitLab’s AI & ML group behind GitLab Duo and managed its Remote Development team. He has nearly a decade of engineering management experience across three companies and two continents. At oregand.github.io, David writes about AI, leadership, and how agents change the work of engineering managers. He’s an ENFJ with a bias for shipping.

## Profile

- **Location:** Seattle
- **Expertise:** AI: Agents, AI: MCP and other integrations, Custom integrations and APIs, Platform engineering, Productivity
- **Technologies:** GitHub Actions, GitHub Copilot, GitLab, Model Context Protocol
- **Interests:** AI agents, AI: MCP and other integrations, Custom integrations and APIs, GitHub Actions, GitHub Copilot, Platform engineering

Evidence for each item: [profile](../profiles/david-o-regan.yaml).

## Affiliations

- Staff EM, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)

## Sessions

- [Plugins and engines: Extending GitHub Copilot live](../sessions/ldr1185d.md) — Thu Oct 29 2026, 12:25 PM–12:40 PM PDT

## Online

- github: <https://github.com/Oregand>
- linkedin: <https://www.linkedin.com/in/oregand7> (via event listing, github profile, website link)
- website: <https://oregand.github.io/> — David O'Regan | Staff Engineering Manager, Copilot @ GitHub | David O'Regan
