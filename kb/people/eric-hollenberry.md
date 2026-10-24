---
title: Eric Hollenberry
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:eric-hollenberry
  name: Eric Hollenberry
  given_name: Eric
  family_name: Hollenberry
  job_title: Principal Product Manager, Metrics
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Principal Product Manager, Metrics
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/hollenberry
      observed_at: '2026-10-24T08:11:49Z'
  affiliation_label: GitHub
  bio: Eric is GitHub's PM for AI usage metrics. He's spent the last 10 years helping everyone learn all
    things Git, GitHub, and Copilot. He spends his time offline being devastated by Padres baseball, and
    copes by enjoying Seattle with his wife and two precious cats.
  photo_url: https://static.rainfocus.com/github/universe26/att/1699462765566001lKc9/attprofile/Profile%20Hollenberry_1784137628987001YYQP.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1776695285557001LaZG
      ref: session:ldr1145b
  accounts:
  - gh:hollenberry
  - acct:linkedin/in/hollenberry
  - acct:x/hollenberry
  github: gh:hollenberry
  github_resolution: resolved
  github_match: name
  profile: profile:eric-hollenberry
  featured: false
  sessions:
  - session: session:ldr1145b
    role: speaker
  mentions:
  - target: software:git
    text: Git
    field: bio
    method: gazetteer
  - target: software:github-copilot
    text: Copilot
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1699462765566001lKc9
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: hollenberry
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Eric Hollenberry

Principal Product Manager, Metrics, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)

Eric is GitHub's PM for AI usage metrics. He's spent the last 10 years helping everyone learn all things Git, GitHub, and Copilot. He spends his time offline being devastated by Padres baseball, and copes by enjoying Seattle with his wife and two precious cats.

## Profile

- **Location:** Seattle, WA
- **Expertise:** Community and social impact, Developer experience (DX), Productivity
- **Technologies:** Git, GitHub Copilot
- **Interests:** Community and social impact, Developer experience (DX), GitHub Copilot, Productivity, cheatsheet, cheatsheets

Evidence for each item: [profile](../profiles/eric-hollenberry.yaml).

## Affiliations

- Principal Product Manager, Metrics, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per linkedin)

## Sessions

- [Beyond "hours saved": How AMD and ING measure AI at enterprise scale](../sessions/ldr1145b.md) — Wed Oct 28 2026, 2:30 PM–3:10 PM PDT

## Online

- github: <https://github.com/hollenberry>
- linkedin: <https://www.linkedin.com/in/hollenberry> (via event listing)
- x: <https://x.com/hollenberry> (via github profile)
