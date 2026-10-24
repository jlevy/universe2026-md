---
title: Erin Havens
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:erin-havens
  name: Erin Havens
  given_name: Erin
  family_name: Havens
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
    label: '@GitHub'
    evidence:
    - url: https://github.com/erinhav
      quote: '@GitHub'
  - organization: org:github
    title: Senior Product Manager
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2023'
  affiliation_label: GitHub
  bio: Erin is a senior product manager at GitHub, focused on security products. Over the past few years,
    she’s shipped 100+ (and counting!) improvements across GitHub secret scanning, Dependabot alerts,
    and Dependabot pull requests. Prior to GitHub, she studied at McGill University in Canada, where she
    wrote code for robots, founded McGill Women in Computer Science, and published a paper on Frank Stella’s
    minimalist art. Outside of work, she likes eating at Michelin-starred restaurants around the world.
  photo_url: https://static.rainfocus.com/github/universe26/att/1695060072936001Zz7u/attprofile/1602878139660_1792697163793001uhnh.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1781211124375001NOiy
      ref: session:tru1775d
  - event: event:github-universe-2023
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe23/attendee-portal/page/sessioncatalog/session/1693507627643001sEwl
      ref: session:2023/sec2759d
  accounts:
  - gh:erinhav
  - acct:bluesky/erinhavens.bsky.social
  - acct:linkedin/in/havenserin
  - acct:x/erinhavens
  websites:
  - site:erinhavens.com
  github: gh:erinhav
  github_resolution: resolved
  github_match: name
  profile: profile:erin-havens
  featured: false
  sessions:
  - session: session:2023/sec2759d
    role: speaker
  - session: session:tru1775d
    role: speaker
  mentions:
  - target: software:dependabot
    text: Dependabot
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1695060072936001Zz7u
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: erinhav
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1695060072936001Zz7u
    retrieved_at: '2026-10-24T08:03:37Z'
    snapshot: raw/editions/universe23/sessions.json
---
# Erin Havens

Senior Product Manager, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2023:** speaker (confirmed)

Erin is a senior product manager at GitHub, focused on security products. Over the past few years, she’s shipped 100+ (and counting!) improvements across GitHub secret scanning, Dependabot alerts, and Dependabot pull requests. Prior to GitHub, she studied at McGill University in Canada, where she wrote code for robots, founded McGill Women in Computer Science, and published a paper on Frank Stella’s minimalist art. Outside of work, she likes eating at Michelin-starred restaurants around the world.

## Profile

- **Location:** San Francisco
- **Expertise:** DevSecOps, Open Source, Security, Supply Chain Security, Vulnerability Detection, AI: Models
- **Technologies:** Dependabot, GitHub Advanced Security, GitHub Copilot, GitHub Enterprise Server, GitHub Secret Protection
- **Interests:** Security, Supply Chain Security, AI: Models, DevSecOps, GitHub Advanced Security, GitHub Copilot

Evidence for each item: [profile](../profiles/erin-havens.yaml).

## Affiliations

- Senior Product Manager, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- Senior Product Manager, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [GitHub Advanced Security: Supply Chain Security](../sessions/2023/sec2759d.md) — Thu Nov 9 2023, 12:00 PM–12:25 PM PST
- [Bringing AI-detected secret scanning to push time and on-prem environments](../sessions/tru1775d.md) — Wed Oct 28 2026, 2:10 PM–2:25 PM PDT

## Online

- github: <https://github.com/erinhav>
- bluesky: <https://bsky.app/profile/erinhavens.bsky.social> (via event listing)
- linkedin: <https://www.linkedin.com/in/havenserin> (via event listing)
- x: <https://x.com/erinhavens> (via event listing)
- website: <http://erinhavens.com/> — Erin L. Havens
