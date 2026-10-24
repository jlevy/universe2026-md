---
title: Thomas Dohmke
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:thomas-dohmke
  name: Thomas Dohmke
  given_name: Thomas
  family_name: Dohmke
  job_title: CEO
  listed_for: event:github-universe-2024
  affiliations:
  - organization: org:deutsche-telekom
    current: true
    basis: linkedin
    label: Deutsche Telekom
    evidence:
    - url: https://www.linkedin.com/in/ashtom
      observed_at: '2026-10-24T08:43:05Z'
  - organization: org:github
    title: CEO
    current: false
    basis: event_listing
    label: GitHub
  - organization: org:entire
    current: false
    basis: github_profile
    label: '@entirehq'
    evidence:
    - url: https://github.com/ashtom
      quote: '@entirehq'
  affiliation_label: GitHub
  bio: Thomas Dohmke is CEO of GitHub and drives the company’s mission of making GitHub the home for all
    developers. Fascinated by software development since his childhood, Thomas is passionate about building
    tools developers love and creating products that drive software development forward. He previously
    co-founded HockeyApp and led the company as CEO through its acquisition by Microsoft in 2014. Thomas
    holds a PhD in mechanical engineering from the University of Glasgow, UK. He lives in the Seattle
    area, is a LEGO enthusiast, and enjoys coding and making his GitHub contribution graph green in his
    spare time.
  photo_url: https://static.rainfocus.com/github/universe24/att/1692113530217001az2Z/attprofile/thomas_1724855851018001a5d8.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2024
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1724855655436001ip2k
      ref: session:2024/1975k
  - event: event:github-universe-2023
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe23/attendee-portal/page/sessioncatalog/session/1695657268465001jL1D
      ref: session:2023/ai2849k
  accounts:
  - gh:ashtom
  - acct:linkedin/in/ashtom
  - acct:x/ashtom
  github: gh:ashtom
  github_resolution: resolved
  github_match: name
  profile: profile:thomas-dohmke
  featured: false
  sessions:
  - session: session:2023/ai2849k
    role: speaker
  - session: session:2024/1975k
    role: speaker
  mentions:
  - target: org:microsoft
    text: Microsoft
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1692113530217001az2Z
    retrieved_at: '2026-10-24T08:03:31Z'
    snapshot: raw/editions/universe24/sessions.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1692113530217001az2Z
    retrieved_at: '2026-10-24T08:03:37Z'
    snapshot: raw/editions/universe23/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: ashtom
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Thomas Dohmke

[Deutsche Telekom](../organizations/deutsche-telekom.md)

Listed for GitHub Universe 2024 as CEO, GitHub.

- **GitHub Universe 2024:** speaker (confirmed)
- **GitHub Universe 2023:** speaker (confirmed)

Thomas Dohmke is CEO of GitHub and drives the company’s mission of making GitHub the home for all developers. Fascinated by software development since his childhood, Thomas is passionate about building tools developers love and creating products that drive software development forward. He previously co-founded HockeyApp and led the company as CEO through its acquisition by Microsoft in 2014. Thomas holds a PhD in mechanical engineering from the University of Glasgow, UK. He lives in the Seattle area, is a LEGO enthusiast, and enjoys coding and making his GitHub contribution graph green in his spare time.

## Profile

- **Location:** Earth
- **Expertise:** Artificial Intelligence (AI)
- **Languages:** Swift, Java
- **Interests:** AI, about-me, AI agents, claude, developer-platform, gemini

Evidence for each item: [profile](../profiles/thomas-dohmke.yaml).

## Affiliations

- [Deutsche Telekom](../organizations/deutsche-telekom.md) (current; per linkedin)
- CEO, [GitHub](../organizations/github.md) (past; per event listing)
- [Entire](../organizations/entire.md) (past; per github profile)

## Sessions

- [Opening Keynote](../sessions/2023/ai2849k.md) — Wed Nov 8 2023, 9:00 AM–9:45 AM PST
- [Opening keynote](../sessions/2024/1975k.md) — Tue Oct 29 2024, 9:00 AM–9:45 AM PDT

## Online

- github: <https://github.com/ashtom>
- linkedin: <https://www.linkedin.com/in/ashtom> (via event listing, github profile)
- x: <https://x.com/ashtom> (via event listing, github profile)
