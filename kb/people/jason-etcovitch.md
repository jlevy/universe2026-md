---
title: Jason Etcovitch
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:jason-etcovitch
  name: Jason Etcovitch
  given_name: Jason
  family_name: Etcovitch
  job_title: Principal Software Engineer
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Principal Software Engineer
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: github_profile
    label: GitHub
    evidence:
    - url: https://github.com/JasonEtco
      quote: GitHub
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/jasonetco
      observed_at: '2026-10-24T08:11:40Z'
  - organization: org:github
    title: Staff Software Engineer
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2025'
  affiliation_label: GitHub
  bio: Jason is a principal software engineer at GitHub, leading the technical teams behind Copilot products.
    He has a long history of building cool things at GitHub and is now focused on the future of agentic
    development. When he isn’t pushing AI-assisted development forward, he’s almost certainly showing
    off cat photos.
  photo_url: https://static.rainfocus.com/github/universe26/att/1699461399745001CjiR/attprofile/10660468_1785858316567001afoQ.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1777574160712001zRFB
      ref: session:bld1402h
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1758764977768001MMTl
      ref: session:2025/bld1785s
  accounts:
  - gh:jasonetco
  - acct:linkedin/in/jasonetco
  - acct:x/jasonetco
  websites:
  - site:jasonet.co
  github: gh:jasonetco
  github_resolution: resolved
  github_match: name
  profile: profile:jason-etcovitch
  featured: false
  sessions:
  - session: session:2025/bld1785s
    role: facilitator
  - session: session:bld1402h
    role: speaker
  mentions:
  - target: software:github-copilot
    text: Copilot
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1699461399745001CjiR
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: JasonEtco
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1699461399745001CjiR
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
---
# Jason Etcovitch

Principal Software Engineer, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2025:** speaker (confirmed)

Jason is a principal software engineer at GitHub, leading the technical teams behind Copilot products. He has a long history of building cool things at GitHub and is now focused on the future of agentic development. When he isn’t pushing AI-assisted development forward, he’s almost certainly showing off cat photos.

## Profile

- **Location:** Toronto, ON
- **Expertise:** AI (Agentic AI, Generative AI, Fine-tuned modeling, Models), Code quality, review, and completion, Productivity, Tech debt and security debt, AI: Agents, AI: MCP and other integrations
- **Technologies:** Copilot coding agent, GitHub Copilot
- **Languages:** TypeScript, JavaScript, Nunjucks
- **Interests:** GitHub Copilot, GitHub Actions, probot, AI, AI agents, AI: MCP and other integrations

Evidence for each item: [profile](../profiles/jason-etcovitch.yaml).

## Affiliations

- Principal Software Engineer, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- [GitHub](../organizations/github.md) (current; per linkedin)
- Staff Software Engineer, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [The multi-core developer: Unlocking productivity with GitHub Copilot coding agent](../sessions/2025/bld1785s.md) (facilitator) — Tue Oct 28 2025, 3:50 PM–4:50 PM PDT
- [Building Copilot in the cloud](../sessions/bld1402h.md) — Wed Oct 28 2026, 3:40 PM–3:55 PM PDT

## Online

- github: <https://github.com/JasonEtco>
- linkedin: <https://www.linkedin.com/in/jasonetco> (via event listing)
- x: <https://x.com/jasonetco> (via event listing, github profile, website link)
- website: <https://jasonet.co> — Jason Etcovitch
