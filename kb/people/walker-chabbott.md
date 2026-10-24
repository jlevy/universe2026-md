---
title: Walker Chabbott
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:walker-chabbott
  name: Walker Chabbott
  given_name: Walker
  family_name: Chabbott
  job_title: Product Manager III
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Product Manager III
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/wchabbott
      observed_at: '2026-10-24T08:15:20Z'
  - organization: org:github
    title: Product Marketing Manager
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2023'
  affiliation_label: GitHub
  bio: Walker is a Model Lifecycle PM at GitHub. He works with partners like OpenAI, Anthropic, and Google
    to bring the latest frontier models to GitHub and Microsoft products. Outside of work, you can find
    him on multi-hour walks around Brooklyn with his golden retriever rescue, Rocket.
  photo_url: https://static.rainfocus.com/github/universe26/att/1695047642558001tX7W/attprofile/Facetune_23-07-2024-11-24-02_1775249888564001HlsX.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1776460904386001a8nL
      ref: session:bld1132s
  - event: event:github-universe-2023
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe23/attendee-portal/page/sessioncatalog/session/1692906208509001tqhC
      ref: session:2023/sec2753d
    - url: https://reg.githubuniverse.com/flow/github/universe23/attendee-portal/page/sessioncatalog/session/1693506948216001NVpG
      ref: session:2023/sec2757d
  accounts:
  - gh:wchabbott
  - acct:linkedin/in/wchabbott
  github: gh:wchabbott
  github_resolution: resolved
  github_match: name
  profile: profile:walker-chabbott
  featured: false
  sessions:
  - session: session:2023/sec2753d
    role: speaker
  - session: session:2023/sec2757d
    role: speaker
  - session: session:bld1132s
    role: facilitator
  mentions:
  - target: org:openai
    text: OpenAI
    field: bio
    method: gazetteer
  - target: org:anthropic
    text: Anthropic
    field: bio
    method: gazetteer
  - target: org:google
    text: Google
    field: bio
    method: gazetteer
  - target: org:microsoft
    text: Microsoft
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1695047642558001tX7W
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: wchabbott
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1695047642558001tX7W
    retrieved_at: '2026-10-24T08:03:37Z'
    snapshot: raw/editions/universe23/sessions.json
---
# Walker Chabbott

Product Manager III, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2023:** speaker (confirmed)

Walker is a Model Lifecycle PM at GitHub. He works with partners like OpenAI, Anthropic, and Google to bring the latest frontier models to GitHub and Microsoft products. Outside of work, you can find him on multi-hour walks around Brooklyn with his golden retriever rescue, Rocket.

## Profile

- **Expertise:** Artificial Intelligence (AI), DevSecOps, Vulnerability Detection, Security, Supply Chain Security, Data (analytics, management, privacy)
- **Technologies:** CodeQL, GitHub Advanced Security, GitHub Copilot
- **Interests:** AI, DevSecOps, GitHub Advanced Security, GitHub Copilot, Vulnerability Detection, Data (analytics, management, privacy)

Evidence for each item: [profile](../profiles/walker-chabbott.yaml).

## Affiliations

- Product Manager III, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per linkedin)
- Product Marketing Manager, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [GitHub Advanced Security: Turbocharging AppSec with AI](../sessions/2023/sec2753d.md) — Wed Nov 8 2023, 10:30 AM–10:55 AM PST
- [GitHub Advanced Security: Code Scanning](../sessions/2023/sec2757d.md) — Wed Nov 8 2023, 1:00 PM–1:25 PM PST
- [Your benchmark is lying: What evals actually look like](../sessions/bld1132s.md) (facilitator) — Wed Oct 28 2026, 10:30 AM–11:15 AM PDT

## Online

- github: <https://github.com/wchabbott>
- linkedin: <https://www.linkedin.com/in/wchabbott> (via event listing)
