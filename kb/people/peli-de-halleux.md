---
title: Peli de Halleux
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:peli-de-halleux
  name: Peli de Halleux
  given_name: Peli
  family_name: de Halleux
  job_title: Agentic Engineer, GitHub Next
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:microsoft
    title: Agentic Engineer, GitHub Next
    current: true
    basis: event_listing
    label: Microsoft
  - organization: org:microsoft
    current: true
    basis: github_profile
    label: Microsoft
    evidence:
    - url: https://github.com/pelikhan
      quote: Microsoft
  - organization: org:microsoft
    current: true
    basis: linkedin
    label: Microsoft
    evidence:
    - url: https://www.linkedin.com/in/pelidehalleux
      observed_at: '2026-10-24T08:15:07Z'
  - organization: org:microsoft
    title: Senior Research Software Engineer
    current: false
    basis: event_listing
    label: Microsoft
    evidence:
    - observed_at: '2025'
  affiliation_label: Microsoft
  bio: Jonathan "Peli" de Halleux is a Principal Research Software Engineer at Microsoft Research, where
    he created GitHub Agentic Workflows. He's also one of the creators of MakeCode and previously built
    GenAIScript, DeviceScript, and Jacdac. Earlier in his career, he created Pex and Moles for automated
    test generation in .NET. Peli holds a PhD in Applied Mathematics from the Catholic University of Louvain.
    He brings a deep practitioner perspective on AI agent orchestration, agentic automation, and developer
    tooling.
  photo_url: https://static.rainfocus.com/github/universe26/att/1777450204317001zcJY/attprofile/Peli_1786068200969001wq5a.png
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791904349224001xUTs
      ref: session:2153b
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1785161525956001tBix
      ref: session:ldr1786m
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1790267224100001ISK1
      ref: session:ldr1913a
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1745434414420001ipKz
      ref: session:2025/bld1143m
  accounts:
  - gh:pelikhan
  - acct:linkedin/in/pelidehalleux
  github: gh:pelikhan
  github_resolution: resolved
  github_match: name
  profile: profile:peli-de-halleux
  featured: false
  sessions:
  - session: session:2025/bld1143m
    role: speaker
  - session: session:2153b
    role: speaker
  - session: session:ldr1786m
    role: speaker
  - session: session:ldr1913a
    role: speaker
  mentions:
  - target: software:github-agentic-workflows
    text: GitHub Agentic Workflows
    field: bio
    method: gazetteer
  - target: software:dotnet
    text: .NET
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1777450204317001zcJY
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: pelikhan
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1692113199740001BmIl
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
---
# Peli de Halleux

Agentic Engineer, GitHub Next, [Microsoft](../organizations/microsoft.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2025:** speaker (confirmed)

Jonathan "Peli" de Halleux is a Principal Research Software Engineer at Microsoft Research, where he created GitHub Agentic Workflows. He's also one of the creators of MakeCode and previously built GenAIScript, DeviceScript, and Jacdac. Earlier in his career, he created Pex and Moles for automated test generation in .NET. Peli holds a PhD in Applied Mathematics from the Catholic University of Louvain. He brings a deep practitioner perspective on AI agent orchestration, agentic automation, and developer tooling.

## Profile

- **Location:** Seattle, WA
- **Expertise:** AI: Agents, Developer experience (DX), Monitoring and observability, Security (RASP, supply chain, threat modeling, vulnerability detection), AI (Agentic AI, Generative AI, Fine-tuned modeling, Models), Collaboration
- **Technologies:** .NET, GitHub Actions, GitHub Agentic Workflows, GitHub Copilot, GitHub Copilot CLI, Visual Studio Code
- **Languages:** TypeScript, C#
- **Interests:** GitHub Actions, GitHub Copilot, AI agents, Developer experience (DX), Monitoring and observability, Security

Evidence for each item: [profile](../profiles/peli-de-halleux.yaml).

## Affiliations

- Agentic Engineer, GitHub Next, [Microsoft](../organizations/microsoft.md) (current; per event listing)
- [Microsoft](../organizations/microsoft.md) (current; per github profile)
- [Microsoft](../organizations/microsoft.md) (current; per linkedin)
- Senior Research Software Engineer, [Microsoft](../organizations/microsoft.md) (past; per event listing)

## Sessions

- [Continuous AI: A new way to collaborate](../sessions/2025/bld1143m.md) — Wed Oct 29 2025, 11:15 AM–11:45 AM PDT
- [Agentic Workflows: Automation at scale](../sessions/2153b.md) — Wed Oct 28 2026, 10:15 AM–10:45 AM PDT
- [The factory mindset: Agentic workflows in production](../sessions/ldr1786m.md) — Wed Oct 28 2026, 12:50 PM–1:20 PM PDT
- [Session After Party: The factory mindset: Agentic workflows in production](../sessions/ldr1913a.md) — Wed Oct 28 2026, 1:35 PM–2:05 PM PDT

## Online

- github: <https://github.com/pelikhan>
- linkedin: <https://www.linkedin.com/in/pelidehalleux> (via event listing, github profile)
