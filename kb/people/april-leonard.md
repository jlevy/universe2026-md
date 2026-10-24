---
title: April Leonard
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:april-leonard
  name: April Leonard
  given_name: April
  family_name: Leonard
  job_title: VP, Engineering
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: VP, Engineering
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: github_profile
    label: GitHub
    evidence:
    - url: https://github.com/aprilla
      quote: GitHub
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/aprilschuff
      observed_at: '2026-10-24T08:11:41Z'
  affiliation_label: GitHub
  bio: April Leonard is VP of Engineering for GitHub Copilot, leading the teams responsible for the platform,
    infrastructure, and product experiences behind AI-powered software development. She focuses on bringing
    advanced AI capabilities to developers while meeting the reliability, security, and governance requirements
    of the world's largest enterprises.
  photo_url: https://static.rainfocus.com/github/universe26/att/1699473035093001TDcX/attprofile/April%20Leonard%20Headshot_1790200267947001haJc.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1786370222106001jLNQ
      ref: session:1809k
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1776470103196001fJPe
      ref: session:bld1134m
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791124397678001jrYp
      ref: session:bld2019a
  accounts:
  - gh:aprilla
  - acct:linkedin/in/aprilschuff
  - acct:x/aprilla
  websites:
  - site:aprilleonard.me
  github: gh:aprilla
  github_resolution: resolved
  github_match: name
  profile: profile:april-leonard
  featured: false
  sessions:
  - session: session:1809k
    role: speaker
  - session: session:bld1134m
    role: moderator
  - session: session:bld2019a
    role: speaker
  mentions:
  - target: software:github-copilot
    text: GitHub Copilot
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1699473035093001TDcX
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: aprilla
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# April Leonard

VP, Engineering, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)

April Leonard is VP of Engineering for GitHub Copilot, leading the teams responsible for the platform, infrastructure, and product experiences behind AI-powered software development. She focuses on bringing advanced AI capabilities to developers while meeting the reliability, security, and governance requirements of the world's largest enterprises.

## Profile

- **Location:** Portland, OR
- **Expertise:** AI: Agents, AI: MCP and other integrations, AI: Models, Open source
- **Technologies:** GitHub Code Security, GitHub Copilot, GitHub Secret Protection
- **Languages:** JavaScript, TypeScript, Ruby, CSS
- **Interests:** GitHub Code Security, GitHub Copilot, GitHub Secret Protection, Supply Chain Security, AI agents, AI: MCP and other integrations

Evidence for each item: [profile](../profiles/april-leonard.yaml).

## Affiliations

- VP, Engineering, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- [GitHub](../organizations/github.md) (current; per linkedin)

## Sessions

- [Opening Keynote](../sessions/1809k.md) — Wed Oct 28 2026, 9:00 AM–9:45 AM PDT
- [The view from the labs: What's next for AI-assisted development](../sessions/bld1134m.md) (moderator) — Thu Oct 29 2026, 9:00 AM–9:30 AM PDT
- [Session After Party: The view from the labs: What's next for AI-assisted development](../sessions/bld2019a.md) — Thu Oct 29 2026, 9:45 AM–10:15 AM PDT

## Online

- github: <https://github.com/aprilla>
- linkedin: <https://www.linkedin.com/in/aprilschuff> (via event listing)
- x: <https://x.com/aprilla> (via event listing, github profile)
- website: <https://aprilleonard.me> — April Leonard - Blog home
