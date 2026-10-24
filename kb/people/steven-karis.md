---
title: Steven Karis
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:steven-karis
  name: Steven Karis
  given_name: Steven
  family_name: Karis
  job_title: Chief Architect
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:resolve-ai
    title: Chief Architect
    current: true
    basis: event_listing
    label: ResolveAI
  - organization: org:resolve-ai
    current: true
    basis: linkedin
    label: Resolve AI
    evidence:
    - url: https://www.linkedin.com/in/steven-karis-62817a96
      observed_at: '2026-10-24T08:15:46Z'
  affiliation_label: ResolveAI
  bio: Steven is a founding engineer at ResolveAI. He focuses on building the agentic AI systems that
    power ResolveAI's Production Engineer. He previously held engineering roles at Splunk and Uber.
  photo_url: https://static.rainfocus.com/github/universe26/att/1785986741141001w6Pw/attprofile/T04MNTXDWGJ-U063A3B047N-8155dca2bf97-512_1785986742025001wkdL.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1785969390274001jXD8
      ref: session:ldr1801d
  accounts:
  - gh:sjkaris
  - acct:linkedin/in/steven-karis-62817a96
  github: gh:sjkaris
  github_resolution: resolved
  github_match: name
  profile: profile:steven-karis
  featured: false
  sessions:
  - session: session:ldr1801d
    role: speaker
  mentions:
  - target: org:uber
    text: Uber
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1785986741141001w6Pw
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: sjkaris
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Steven Karis

Chief Architect, [Resolve AI](../organizations/resolve-ai.md)

- **GitHub Universe 2026:** speaker (confirmed)

Steven is a founding engineer at ResolveAI. He focuses on building the agentic AI systems that power ResolveAI's Production Engineer. He previously held engineering roles at Splunk and Uber.

## Profile

- **Expertise:** AI: Agents, Continuous Integration + Continuous Deployment (CI/CD), DevOps and DevSecOps, Platform engineering
- **Technologies:** GitHub Actions, GitHub Copilot, GitHub Enterprise Cloud
- **Interests:** AI agents, Continuous Integration + Continuous Deployment (CI/CD), DevOps and DevSecOps, GitHub Actions, GitHub Copilot, GitHub Enterprise Cloud

Evidence for each item: [profile](../profiles/steven-karis.yaml).

## Affiliations

- Chief Architect, [Resolve AI](../organizations/resolve-ai.md) (current; per event listing)
- [Resolve AI](../organizations/resolve-ai.md) (current; per linkedin)

## Sessions

- [Four primitives to evaluate and improve your on-call agent's autonomy (Sponsored)](../sessions/ldr1801d.md) — Wed Oct 28 2026, 11:30 AM–11:45 AM PDT

## Online

- github: <https://github.com/sjkaris>
- linkedin: <https://www.linkedin.com/in/steven-karis-62817a96> (via event listing)
