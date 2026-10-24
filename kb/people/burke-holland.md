---
title: Burke Holland
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:burke-holland
  name: Burke Holland
  given_name: Burke
  family_name: Holland
  job_title: Principal Cloud Advocate
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:microsoft
    title: Principal Cloud Advocate
    current: true
    basis: event_listing
    label: Microsoft
  - organization: org:microsoft
    current: true
    basis: github_profile
    label: Microsoft
    evidence:
    - url: https://github.com/burkeholland
      quote: Microsoft
  - organization: org:microsoft
    current: true
    basis: linkedin
    label: Microsoft
    evidence:
    - url: https://www.linkedin.com/in/burkeholland
      observed_at: '2026-10-24T08:11:40Z'
  - organization: org:microsoft
    title: Developer Advocate
    current: false
    basis: event_listing
    label: Microsoft
    evidence:
    - observed_at: '2024'
  affiliation_label: Microsoft
  bio: |-
    Burke is a principal cloud advocate living in Nashville, TN, the greatest city in the world. He likes JavaScript a lot because it's the only way he “Node to Express” himself. Get it? Is this thing on?

    Never mind.

    Look, Burke blogs only slightly better than he codes and definitely not as good as he talks about himself in the third person. The legal requirement for living in Nashville is to play a guitar, so Burke plays the bass and tries in vain to rekindle his dreams of rock stardom. He's also a huge fan of running, lengthy bios, and sarcasm.

    Burke works on VS Code, GitHub and Azure—helping to make these things work better, together.
  photo_url: https://static.rainfocus.com/github/universe26/att/1790700744585001b0hx/attprofile/image%20%2858%29_1792711085141001qQVD.png
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1786370222106001jLNQ
      ref: session:1809k
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1790696144574001cNvK
      ref: session:bld1978m
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791897225330001x7Id
      ref: session:bld2152a
  - event: event:github-universe-2024
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1726152457231001LrEd
      ref: session:2024/dev2016m
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1726265048440001o3Nk
      ref: session:2024/ai2024l
  accounts:
  - gh:burkeholland
  - acct:bluesky/burkeholland.bsky.social
  - acct:linkedin/in/burkeholland
  - acct:x/burkeholland
  - acct:youtube/@burkeholland
  websites:
  - site:burkeholland.github.io
  github: gh:burkeholland
  github_resolution: resolved
  github_match: name
  profile: profile:burke-holland
  featured: false
  sessions:
  - session: session:1809k
    role: speaker
  - session: session:2024/ai2024l
    role: facilitator
  - session: session:2024/dev2016m
    role: speaker
  - session: session:bld1978m
    role: speaker
  - session: session:bld2152a
    role: speaker
  mentions:
  - target: software:javascript
    text: JavaScript
    field: bio
    method: gazetteer
  - target: software:vs-code
    text: VS Code
    field: bio
    method: gazetteer
  - target: software:azure
    text: Azure
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1790700744585001b0hx
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: burkeholland
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1724797307652001EIoq
    retrieved_at: '2026-10-24T08:03:31Z'
    snapshot: raw/editions/universe24/sessions.json
---
# Burke Holland

Principal Cloud Advocate, [Microsoft](../organizations/microsoft.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2024:** speaker (confirmed)

Burke is a principal cloud advocate living in Nashville, TN, the greatest city in the world. He likes JavaScript a lot because it's the only way he “Node to Express” himself. Get it? Is this thing on?

Never mind.

Look, Burke blogs only slightly better than he codes and definitely not as good as he talks about himself in the third person. The legal requirement for living in Nashville is to play a guitar, so Burke plays the bass and tries in vain to rekindle his dreams of rock stardom. He's also a huge fan of running, lengthy bios, and sarcasm.

Burke works on VS Code, GitHub and Azure—helping to make these things work better, together.

## Profile

- **Location:** Franklin, TN
- **Expertise:** AI, Productivity, Software Engineering, AI: Agents, AI: MCP and other integrations, AI: Models
- **Technologies:** GitHub Copilot, JavaScript, Microsoft Azure, Visual Studio Code
- **Languages:** JavaScript, C#, TypeScript, HTML
- **Interests:** GitHub Copilot, Productivity, VS Code, AI, AI agents, AI: MCP and other integrations

Evidence for each item: [profile](../profiles/burke-holland.yaml).

## Affiliations

- Principal Cloud Advocate, [Microsoft](../organizations/microsoft.md) (current; per event listing)
- [Microsoft](../organizations/microsoft.md) (current; per github profile)
- [Microsoft](../organizations/microsoft.md) (current; per linkedin)
- Developer Advocate, [Microsoft](../organizations/microsoft.md) (past; per event listing)

## Sessions

- [Opening Keynote](../sessions/1809k.md) — Wed Oct 28 2026, 9:00 AM–9:45 AM PDT
- [Is AI fundamentally changing the way that we write code?](../sessions/2024/ai2024l.md) (facilitator) — Wed Oct 30 2024, 11:30 AM–12:10 PM PDT
- [#HappyCoding! Build intelligent apps with Visual Studio Code, GitHub, and Azure](../sessions/2024/dev2016m.md) — Tue Oct 29 2024, 2:45 PM–3:25 PM PDT
- [Work together, your way, with GitHub Copilot](../sessions/bld1978m.md) — Wed Oct 28 2026, 1:40 PM–2:10 PM PDT
- [Session After Party: Work together, your way, with GitHub Copilot](../sessions/bld2152a.md) — Wed Oct 28 2026, 2:25 PM–2:55 PM PDT

## Online

- github: <https://github.com/burkeholland>
- bluesky: <https://bsky.app/profile/burkeholland.bsky.social> (via event listing)
- linkedin: <https://www.linkedin.com/in/burkeholland> (via event listing, github profile)
- x: <https://x.com/burkeholland> (via event listing, github profile)
- youtube: <https://www.youtube.com/@burkeholland> (via github profile)
- website: <https://burkeholland.github.io> — Burke Holland
