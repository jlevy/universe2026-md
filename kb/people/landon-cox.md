---
title: Landon Cox
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:landon-cox
  name: Landon Cox
  given_name: Landon
  family_name: Cox
  job_title: Senior Principle Researcher
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:microsoft
    title: Senior Principle Researcher
    current: true
    basis: event_listing
    label: Microsoft
  - organization: org:microsoft
    current: true
    basis: github_profile
    label: Microsoft
    evidence:
    - url: https://github.com/lpcox
      quote: Microsoft
  - organization: org:microsoft
    current: true
    basis: linkedin
    label: Microsoft
    evidence:
    - url: https://www.linkedin.com/in/landon-cox-6727363
      observed_at: '2026-10-24T08:15:13Z'
  affiliation_label: Microsoft
  bio: Landon Cox is a Senior Principal Researcher from Microsoft Research and GitHub Next. He is currently
    the Security Lead for GitHub Agentic Workflows. He previously worked on Azure Programmable Connectivity
    (APC), helped deploy Exposure Notifications in the state of Washington, and was a tenured professor
    at Duke University. Landon was recognized as an ACM Distinguished Member and received an ACM SIGOPS
    Hall of Fame Award for his work on privacy in mobile computing.
  photo_url: https://static.rainfocus.com/github/universe26/att/1777673854269001pz9T/attprofile/Landon%20Cox_1792464062560001jrkl.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791904349224001xUTs
      ref: session:2153b
  accounts:
  - gh:lpcox
  - acct:bluesky/lpcox.bsky.social
  - acct:linkedin/in/landon-cox-6727363
  - acct:x/lpcox
  github: gh:lpcox
  github_resolution: resolved
  github_match: name
  profile: profile:landon-cox
  featured: false
  sessions:
  - session: session:2153b
    role: speaker
  mentions:
  - target: software:github-agentic-workflows
    text: GitHub Agentic Workflows
    field: bio
    method: gazetteer
  - target: software:azure
    text: Azure
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1777673854269001pz9T
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: lpcox
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Landon Cox

Senior Principle Researcher, [Microsoft](../organizations/microsoft.md)

- **GitHub Universe 2026:** speaker (confirmed)

Landon Cox is a Senior Principal Researcher from Microsoft Research and GitHub Next. He is currently the Security Lead for GitHub Agentic Workflows. He previously worked on Azure Programmable Connectivity (APC), helped deploy Exposure Notifications in the state of Washington, and was a tenured professor at Duke University. Landon was recognized as an ACM Distinguished Member and received an ACM SIGOPS Hall of Fame Award for his work on privacy in mobile computing.

## Profile

- **Location:** Seattle, WA
- **Technologies:** GitHub Agentic Workflows, Microsoft Azure
- **Interests:** GitHub Actions, agentic, agentic-factory, agentic-workflows, cai, cao

Evidence for each item: [profile](../profiles/landon-cox.yaml).

## Affiliations

- Senior Principle Researcher, [Microsoft](../organizations/microsoft.md) (current; per event listing)
- [Microsoft](../organizations/microsoft.md) (current; per github profile)
- [Microsoft](../organizations/microsoft.md) (current; per linkedin)

## Sessions

- [Agentic Workflows: Automation at scale](../sessions/2153b.md) — Wed Oct 28 2026, 10:15 AM–10:45 AM PDT

## Online

- github: <https://github.com/lpcox>
- bluesky: <https://bsky.app/profile/lpcox.bsky.social> (via event listing)
- linkedin: <https://www.linkedin.com/in/landon-cox-6727363> (via event listing)
- x: <https://x.com/lpcox> (via event listing)
