---
title: Cooper Nederhood
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:cooper-nederhood
  name: Cooper Nederhood
  given_name: Cooper
  family_name: Nederhood
  job_title: Senior Applied Researcher
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Senior Applied Researcher
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: github_profile
    label: '@github Copilot'
    evidence:
    - url: https://github.com/CooperNederhood
      quote: '@github Copilot'
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/cooper-nederhood-b2a70072
      observed_at: '2026-10-24T08:11:43Z'
  - organization: org:github
    title: Machine Learning Engineer
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2024'
  affiliation_label: GitHub
  bio: Cooper is a senior software engineer at GitHub on the GitHub Copilot Applied Science Modeling team.
    His work has focused on building custom Copilot models for enterprise customers. He has also worked
    to improve Copilot code completion quality through additional LLM fine-tuning and prompt engineering
    techniques.
  photo_url: https://static.rainfocus.com/github/universe26/att/1699462878211001nWCv/attprofile/Cooper%20N_1786068684069001wS9L.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1777557576923001fNOZ
      ref: session:bld1372b
  - event: event:github-universe-2024
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1715178970303001Gg0A
      ref: session:2024/ai1332p
  accounts:
  - gh:coopernederhood
  - acct:linkedin/in/cooper-nederhood-b2a70072
  github: gh:coopernederhood
  github_resolution: resolved
  github_match: name
  profile: profile:cooper-nederhood
  featured: false
  sessions:
  - session: session:2024/ai1332p
    role: panelist
  - session: session:bld1372b
    role: speaker
  mentions:
  - target: software:github-copilot
    text: GitHub Copilot
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1699462878211001nWCv
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: CooperNederhood
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1699462878211001nWCv
    retrieved_at: '2026-10-24T08:03:31Z'
    snapshot: raw/editions/universe24/sessions.json
---
# Cooper Nederhood

Senior Applied Researcher, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2024:** speaker (confirmed)

Cooper is a senior software engineer at GitHub on the GitHub Copilot Applied Science Modeling team. His work has focused on building custom Copilot models for enterprise customers. He has also worked to improve Copilot code completion quality through additional LLM fine-tuning and prompt engineering techniques.

## Profile

- **Location:** Chicago, Illinois
- **Expertise:** AI, Machine Learning, AI: Agents, AI: Models
- **Technologies:** GitHub Copilot
- **Interests:** GitHub Copilot, AI, AI agents, AI: Models, Machine learning

Evidence for each item: [profile](../profiles/cooper-nederhood.yaml).

## Affiliations

- Senior Applied Researcher, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- [GitHub](../organizations/github.md) (current; per linkedin)
- Machine Learning Engineer, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [An inside look at how GitHub uses LLMs, fine-tuning, and prompt engineering in GitHub Copilot](../sessions/2024/ai1332p.md) (panelist) — Wed Oct 30 2024, 3:30 PM–4:10 PM PDT
- [How GitHub taught Copilot to remember and when to forget](../sessions/bld1372b.md) — Wed Oct 28 2026, 11:30 AM–12:10 PM PDT

## Online

- github: <https://github.com/CooperNederhood>
- linkedin: <https://www.linkedin.com/in/cooper-nederhood-b2a70072> (via event listing)
