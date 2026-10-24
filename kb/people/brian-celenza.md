---
title: Brian Celenza
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:brian-celenza
  name: Brian Celenza
  given_name: Brian
  family_name: Celenza
  job_title: Principal Software Engineer
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Principal Software Engineer
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: github_profile
    label: '@github'
    evidence:
    - url: https://github.com/bcelenza
      quote: '@github'
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/bcelenza
      observed_at: '2026-10-24T08:11:51Z'
  affiliation_label: GitHub
  bio: Brian Celenza is a Principal Software Engineer at GitHub, where he works on the storage and services
    that power every git push and git clone. He has spent two decades building software and cloud infrastructure
    across developer productivity, healthcare, and commerce. Brian is now helping rebuild GitHub’s Git
    infrastructure to support workloads at agent scale. Outside of work, he enjoys hiking, gardening,
    cooking, and baking.
  photo_url: https://static.rainfocus.com/github/universe26/att/1730217678268001g2iV/attprofile/me_1791587256361001AhlN.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791396311592001XtGo
      ref: session:bld2049b
  accounts:
  - gh:bcelenza
  - acct:linkedin/in/bcelenza
  github: gh:bcelenza
  github_resolution: resolved
  github_match: name
  profile: profile:brian-celenza
  featured: false
  sessions:
  - session: session:bld2049b
    role: speaker
  mentions:
  - target: software:git
    text: Git
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1730217678268001g2iV
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: bcelenza
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Brian Celenza

Principal Software Engineer, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)

Brian Celenza is a Principal Software Engineer at GitHub, where he works on the storage and services that power every git push and git clone. He has spent two decades building software and cloud infrastructure across developer productivity, healthcare, and commerce. Brian is now helping rebuild GitHub’s Git infrastructure to support workloads at agent scale. Outside of work, he enjoys hiking, gardening, cooking, and baking.

## Profile

- **Location:** Seattle, WA
- **Technologies:** Git
- **Languages:** Rust, TypeScript
- **Interests:** aws, aws-cloudwatch, aws-cloudwatch-logs, cli, cloudwatch, cloudwatch-insights

Evidence for each item: [profile](../profiles/brian-celenza.yaml).

## Affiliations

- Principal Software Engineer, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- [GitHub](../organizations/github.md) (current; per linkedin)

## Sessions

- [Scaling GitHub’s infrastructure for how developers build today](../sessions/bld2049b.md) — Thu Oct 29 2026, 9:00 AM–9:40 AM PDT

## Online

- github: <https://github.com/bcelenza>
- linkedin: <https://www.linkedin.com/in/bcelenza> (via event listing, github profile)
