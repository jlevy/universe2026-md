---
title: Alex Gorischek
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:alex-gorischek
  name: Alex Gorischek
  given_name: Alex
  family_name: Gorischek
  job_title: Senior Research Engineer
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Senior Research Engineer
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/alexgorischek
      observed_at: '2026-10-24T08:11:38Z'
  - organization: org:microsoft
    current: false
    basis: github_profile
    label: Microsoft
    evidence:
    - url: https://github.com/agorischek
      quote: Microsoft
  affiliation_label: GitHub
  photo_url: https://static.rainfocus.com/github/universe26/att/1787354992642001uhKf/attprofile/E01DLHH5JM6-U0AQZULUG3V-37f2f87d3ec5-512_1792696630118001JpUV.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791904799664001SHnG
      ref: session:2154b
  accounts:
  - gh:agorischek
  - acct:bluesky/alexgorischek.bsky.social
  - acct:linkedin/in/alexgorischek
  - acct:x/alexgorischek
  websites:
  - site:alexgorischek.com
  github: gh:agorischek
  github_resolution: resolved
  github_match: name
  profile: profile:alex-gorischek
  featured: false
  sessions:
  - session: session:2154b
    role: speaker
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1787354992642001uhKf
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: agorischek
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Alex Gorischek

Senior Research Engineer, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)

## Profile

- **Location:** Seattle, WA
- **Languages:** TypeScript
- **Interests:** cli, go, json-schema, jsonc, LLMs, prompting

Evidence for each item: [profile](../profiles/alex-gorischek.yaml).

## Affiliations

- Senior Research Engineer, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per linkedin)
- [Microsoft](../organizations/microsoft.md) (past; per github profile)

## Sessions

- [Inside the Lab with GitHub Next](../sessions/2154b.md) — Wed Oct 28 2026, 11:00 AM–11:30 AM PDT

## Online

- github: <https://github.com/agorischek>
- bluesky: <https://bsky.app/profile/alexgorischek.bsky.social> (via event listing)
- linkedin: <https://www.linkedin.com/in/alexgorischek> (via event listing)
- x: <https://x.com/AlexGorischek> (via event listing)
- website: <https://www.alexgorischek.com>
