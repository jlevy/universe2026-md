---
title: Pierce Boggan
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:pierce-boggan
  name: Pierce Boggan
  given_name: Pierce
  family_name: Boggan
  job_title: Product - GitHub Copilot
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Product - GitHub Copilot
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:microsoft
    current: true
    basis: github_profile
    label: Microsoft
    evidence:
    - url: https://github.com/pierceboggan
      quote: Microsoft
  - organization: org:microsoft
    current: true
    basis: linkedin
    label: Microsoft
    evidence:
    - url: https://www.linkedin.com/in/pierceboggan
      observed_at: '2026-10-24T08:15:43Z'
  - organization: org:microsoft
    title: PM Lead, VS Code
    current: false
    basis: event_listing
    label: Microsoft
    evidence:
    - observed_at: '2025'
  affiliation_label: GitHub
  bio: "Pierce Boggan is the product lead for the new GitHub Copilot app. Previously, he led product management\
    \ for Visual Studio Code and worked on developer tools across Azure, TypeScript, and .NET. He joined\
    \ Microsoft through its acquisition of Xamarin in 2016. \n\nPierce lives in Park City, Utah, with\
    \ his wife, two-year-old daughter, and four-year-old son. He enjoys skiing, mountain and road biking,\
    \ backpacking, camping, and exploring Utah’s beautiful national parks."
  photo_url: https://static.rainfocus.com/github/universe26/att/1789140562894001l2AC/attprofile/image%20%284%29_1792684529580001vpUP.png
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1790696144574001cNvK
      ref: session:bld1978m
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791897225330001x7Id
      ref: session:bld2152a
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1756898827184001uqBY
      ref: session:2025/1617k
  accounts:
  - gh:pierceboggan
  - acct:linkedin/in/pierceboggan
  - acct:x/pierceboggan
  websites:
  - site:pierceboggan.dev
  github: gh:pierceboggan
  github_resolution: resolved
  github_match: name
  profile: profile:pierce-boggan
  featured: false
  sessions:
  - session: session:2025/1617k
    role: speaker
  - session: session:bld1978m
    role: speaker
  - session: session:bld2152a
    role: speaker
  mentions:
  - target: software:github-copilot
    text: GitHub Copilot
    field: bio
    method: gazetteer
  - target: software:vs-code
    text: Visual Studio Code
    field: bio
    method: gazetteer
  - target: software:azure
    text: Azure
    field: bio
    method: gazetteer
  - target: software:typescript
    text: TypeScript
    field: bio
    method: gazetteer
  - target: software:dotnet
    text: .NET
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1789140562894001l2AC
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: pierceboggan
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1745868661376001iKtu
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
---
# Pierce Boggan

Product - GitHub Copilot, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2025:** speaker (confirmed)

Pierce Boggan is the product lead for the new GitHub Copilot app. Previously, he led product management for Visual Studio Code and worked on developer tools across Azure, TypeScript, and .NET. He joined Microsoft through its acquisition of Xamarin in 2016. 

Pierce lives in Park City, Utah, with his wife, two-year-old daughter, and four-year-old son. He enjoys skiing, mountain and road biking, backpacking, camping, and exploring Utah’s beautiful national parks.

## Profile

- **Location:** Park City, UT
- **Expertise:** AI: Agents, AI: MCP and other integrations, AI: Models, Developer experience (DX), Productivity, Accessibility
- **Technologies:** .NET, GitHub Copilot, Microsoft Azure, TypeScript, Visual Studio Code
- **Languages:** TypeScript, JavaScript, HTML, C#, Swift
- **Interests:** VS Code, GitHub Copilot, AI agents, Productivity, AI: MCP and other integrations, AI: Models

Evidence for each item: [profile](../profiles/pierce-boggan.yaml).

## Affiliations

- Product - GitHub Copilot, [GitHub](../organizations/github.md) (current; per event listing)
- [Microsoft](../organizations/microsoft.md) (current; per github profile)
- [Microsoft](../organizations/microsoft.md) (current; per linkedin)
- PM Lead, VS Code, [Microsoft](../organizations/microsoft.md) (past; per event listing)

## Sessions

- [Opening Keynote](../sessions/2025/1617k.md) — Tue Oct 28 2025, 9:00 AM–9:45 AM PDT
- [Work together, your way, with GitHub Copilot](../sessions/bld1978m.md) — Wed Oct 28 2026, 1:40 PM–2:10 PM PDT
- [Session After Party: Work together, your way, with GitHub Copilot](../sessions/bld2152a.md) — Wed Oct 28 2026, 2:25 PM–2:55 PM PDT

## Online

- github: <https://github.com/pierceboggan>
- linkedin: <https://www.linkedin.com/in/pierceboggan> (via event listing)
- x: <https://x.com/pierceboggan> (via event listing, github profile)
- website: <http://pierceboggan.dev/>
