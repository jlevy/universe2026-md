---
title: James Fletcher
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:james-fletcher
  name: James Fletcher
  given_name: James
  family_name: Fletcher
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
    - url: https://github.com/jf205
      quote: GitHub
  - organization: org:github
    title: Senior Product Manager
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2024'
  affiliation_label: GitHub
  bio: James works on GitHub Advanced Security and primarily focuses on helping security-conscious users
    find and fix more security problems in their code.
  photo_url: https://static.rainfocus.com/github/universe26/att/1715337711236001Gykn/attprofile/James%20Fletcher_1786068462656001yvKM.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791984478620001QW23
      ref: session:tru2230d
  - event: event:github-universe-2024
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1715337432495001xTGa
      ref: session:2024/sec1511d
  accounts:
  - gh:jf205
  - acct:linkedin/in/james-fletcher-1853a4159
  github: gh:jf205
  github_resolution: resolved
  github_match: name
  profile: profile:james-fletcher
  featured: false
  sessions:
  - session: session:2024/sec1511d
    role: speaker
  - session: session:tru2230d
    role: speaker
  mentions:
  - target: software:github-advanced-security
    text: GitHub Advanced Security
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1715337711236001Gykn
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: jf205
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1715337711236001Gykn
    retrieved_at: '2026-10-24T08:03:31Z'
    snapshot: raw/editions/universe24/sessions.json
---
# James Fletcher

Senior Product Manager, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2024:** speaker (confirmed)

James works on GitHub Advanced Security and primarily focuses on helping security-conscious users find and fix more security problems in their code.

## Profile

- **Location:** Oxfordshire, UK
- **Expertise:** AI, Security
- **Technologies:** GitHub Advanced Security, GitHub Copilot
- **Interests:** AI, GitHub Advanced Security, Security, docs, works-with-codespaces

Evidence for each item: [profile](../profiles/james-fletcher.yaml).

## Affiliations

- Senior Product Manager, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- Senior Product Manager, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [Pay down security debt with Copilot Autofix](../sessions/2024/sec1511d.md) — Wed Oct 30 2024, 10:30 AM–10:55 AM PDT
- [Keep vulnerabilities out of your codebase, without leaving where you build](../sessions/tru2230d.md) — Wed Oct 28 2026, 3:05 PM–3:20 PM PDT

## Online

- github: <https://github.com/jf205>
- linkedin: <https://www.linkedin.com/in/james-fletcher-1853a4159> (via event listing)
