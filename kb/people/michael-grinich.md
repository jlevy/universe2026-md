---
title: Michael Grinich
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:michael-grinich
  name: Michael Grinich
  given_name: Michael
  family_name: Grinich
  job_title: CEO
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:workos
    title: CEO
    current: true
    basis: event_listing
    label: WorkOS
  - organization: org:workos
    current: true
    basis: github_profile
    label: '@WorkOS'
    evidence:
    - url: https://github.com/grinich
      quote: '@WorkOS'
  - organization: org:workos
    current: true
    basis: linkedin
    label: WorkOS
    evidence:
    - url: https://www.linkedin.com/in/grinich
      observed_at: '2026-10-24T08:11:33Z'
  - organization: org:workos
    title: Founder
    current: false
    basis: event_listing
    label: WorkOS
    evidence:
    - observed_at: '2025'
  affiliation_label: WorkOS
  bio: Michael is the founder and CEO of WorkOS, a developer platform that helps businesses become enterprise-ready
    with features like SSO, SCIM, RBAC, and Audit Logs. Its customers include many of the fastest-growing
    companies — OpenAI, Cursor, Vercel, and over 1,000 others. Before WorkOS, Michael co-founded Nylas
    and studied computer science at MIT.
  photo_url: https://static.rainfocus.com/github/universe26/att/1759265517921001S428/attprofile/m2TFWGlC_400x400-1_1786029450086001Oo0E.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1784736653607001jayY
      ref: session:ldr1785d
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1753903718124001uR62
      ref: session:2025/sec1550d
  accounts:
  - gh:grinich
  - acct:linkedin/in/grinich
  - acct:x/grinich
  github: gh:grinich
  github_resolution: resolved
  github_match: name
  profile: profile:michael-grinich
  featured: false
  sessions:
  - session: session:2025/sec1550d
    role: speaker
  - session: session:ldr1785d
    role: speaker
  mentions:
  - target: org:openai
    text: OpenAI
    field: bio
    method: gazetteer
  - target: software:cursor
    text: Cursor
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1759265517921001S428
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: grinich
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1759265517921001S428
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
---
# Michael Grinich

CEO, [WorkOS](../organizations/workos.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2025:** speaker (confirmed)

Michael is the founder and CEO of WorkOS, a developer platform that helps businesses become enterprise-ready with features like SSO, SCIM, RBAC, and Audit Logs. Its customers include many of the fastest-growing companies — OpenAI, Cursor, Vercel, and over 1,000 others. Before WorkOS, Michael co-founded Nylas and studied computer science at MIT.

## Profile

- **Location:** San Francisco
- **Expertise:** AI (Agentic AI, Generative AI, Fine-tuned modeling, Models), IDE Integration, AI: Agents
- **Technologies:** Cursor, GitHub Copilot, Model Context Protocol
- **Languages:** TypeScript, Swift, Objective-C, Python
- **Interests:** AI, macos, swiftui, AI agents, GitHub Copilot, IDE Integration

Evidence for each item: [profile](../profiles/michael-grinich.yaml).

## Affiliations

- CEO, [WorkOS](../organizations/workos.md) (current; per event listing)
- [WorkOS](../organizations/workos.md) (current; per github profile)
- [WorkOS](../organizations/workos.md) (current; per linkedin)
- Founder, [WorkOS](../organizations/workos.md) (past; per event listing)

## Sessions

- [Enterprise-ready (and Copilot-ready) MCP servers](../sessions/2025/sec1550d.md) — Wed Oct 29 2025, 2:00 PM–2:15 PM PDT
- [Auth for agents: How auth.md lets agents skip the sign-up form (Sponsored)](../sessions/ldr1785d.md) — Wed Oct 28 2026, 1:50 PM–2:05 PM PDT

## Online

- github: <https://github.com/grinich>
- linkedin: <https://www.linkedin.com/in/grinich> (via event listing, github profile)
- x: <https://x.com/grinich> (via event listing, github profile)
