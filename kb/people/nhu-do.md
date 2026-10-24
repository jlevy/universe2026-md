---
title: Nhu Do
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:nhu-do
  name: Nhu Do
  given_name: Nhu
  family_name: Do
  job_title: Senior Product Manager
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Senior Product Manager
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: github_profile
    label: GitHub
    evidence:
    - url: https://github.com/nhu-do
      quote: GitHub
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/nhudo
      observed_at: '2026-10-24T08:15:26Z'
  affiliation_label: GitHub
  bio: Nhu is a Product Manager on the GitHub Copilot platform team, focused on making Copilot smarter,
    more efficient, and more effective at scale — from how Copilot uses AI models to the experiences developers
    use every day. Previously, she worked at Microsoft, building content safety systems and evaluation
    frameworks to support the responsible deployment and use of generative AI. Based in New York City,
    Nhu enjoys exploring the city's lively food and art scene.
  photo_url: https://static.rainfocus.com/github/universe26/att/1730217260193001ONtz/attprofile/16AD108F-8C52-4474-A706-7CF19E684046_1786220535987001lK33.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1777658767198001Xsp1
      ref: session:bld1553d
  accounts:
  - gh:nhu-do
  - acct:linkedin/in/nhudo
  github: gh:nhu-do
  github_resolution: resolved
  github_match: name
  profile: profile:nhu-do
  featured: false
  sessions:
  - session: session:bld1553d
    role: speaker
  mentions:
  - target: software:github-copilot
    text: GitHub Copilot
    field: bio
    method: gazetteer
  - target: org:microsoft
    text: Microsoft
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1730217260193001ONtz
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: nhu-do
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Nhu Do

Senior Product Manager, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)

Nhu is a Product Manager on the GitHub Copilot platform team, focused on making Copilot smarter, more efficient, and more effective at scale — from how Copilot uses AI models to the experiences developers use every day. Previously, she worked at Microsoft, building content safety systems and evaluation frameworks to support the responsible deployment and use of generative AI. Based in New York City, Nhu enjoys exploring the city's lively food and art scene.

## Profile

- **Location:** New York
- **Expertise:** Platform engineering
- **Technologies:** GitHub Copilot
- **Interests:** GitHub Copilot, Platform engineering, docs, editor, electron, TypeScript

Evidence for each item: [profile](../profiles/nhu-do.yaml).

## Affiliations

- Senior Product Manager, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- [GitHub](../organizations/github.md) (current; per linkedin)

## Sessions

- [Inside Copilot's model router: How auto picks the right model for every task](../sessions/bld1553d.md) — Thu Oct 29 2026, 12:05 PM–12:20 PM PDT

## Online

- github: <https://github.com/nhu-do>
- linkedin: <https://www.linkedin.com/in/nhudo> (via event listing)
