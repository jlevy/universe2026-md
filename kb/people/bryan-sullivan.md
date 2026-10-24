---
title: Bryan Sullivan
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:bryan-sullivan
  name: Bryan Sullivan
  given_name: Bryan
  family_name: Sullivan
  job_title: Sr Director Product Management
  listed_for: event:github-universe-2024
  affiliations:
  - organization: org:github
    title: Sr Director Product Management
    current: false
    basis: event_listing
    label: GitHub
  affiliation_label: GitHub
  bio: Bryan is a senior director of product at GitHub, where he is responsible for GitHub Advanced Security
    (GHAS). Bryan has focused on developer security tooling for over 20 years, helping developers “fall
    into a pit of success” by building more secure software without impacting their productivity. Prior
    to GitHub, Bryan worked at Microsoft where he was responsible for building security tooling into the
    Microsoft One Engineering System (1ES) used by all Microsoft engineers.
  photo_url: https://static.rainfocus.com/github/universe24/att/1724899834885001GSxp/attprofile/bryan%20sulli_1725392041228001WOus.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2024
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1726431915292001pUWU
      ref: session:2024/sec2025m
  github_resolution: absent
  profile: profile:bryan-sullivan
  featured: false
  sessions:
  - session: session:2024/sec2025m
    role: speaker
  mentions:
  - target: software:github-advanced-security
    text: GitHub Advanced Security
    field: bio
    method: gazetteer
  - target: org:microsoft
    text: Microsoft
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1724899834885001GSxp
    retrieved_at: '2026-10-24T08:03:31Z'
    snapshot: raw/editions/universe24/sessions.json
---
# Bryan Sullivan

Sr Director Product Management, GitHub

- **GitHub Universe 2024:** speaker (confirmed)

Bryan is a senior director of product at GitHub, where he is responsible for GitHub Advanced Security (GHAS). Bryan has focused on developer security tooling for over 20 years, helping developers “fall into a pit of success” by building more secure software without impacting their productivity. Prior to GitHub, Bryan worked at Microsoft where he was responsible for building security tooling into the Microsoft One Engineering System (1ES) used by all Microsoft engineers.

## Profile

- **Expertise:** AI, Security, Tech Debt, Threat Modeling, Vulnerability Detection
- **Technologies:** GitHub Advanced Security, GitHub Copilot
- **Interests:** AI, GitHub Advanced Security, GitHub Copilot, Security, Tech Debt, Threat Modeling

Evidence for each item: [profile](../profiles/bryan-sullivan.yaml).

## Affiliations

- Sr Director Product Management, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [Found means fixed: Addressing security debt at scale](../sessions/2024/sec2025m.md) — Tue Oct 29 2024, 1:45 PM–2:25 PM PDT
