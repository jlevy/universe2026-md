---
title: Josh Scriven
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:josh-scriven
  name: Josh Scriven
  given_name: Josh
  family_name: Scriven
  job_title: Microsoft Americas Practice, AI Leader
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:ibm
    title: Microsoft Americas Practice, AI Leader
    current: true
    basis: event_listing
    label: IBM Consulting
  - organization: org:ibm
    current: true
    basis: github_profile
    label: IBM Consulting
    evidence:
    - url: https://github.com/eccolab
      quote: IBM Consulting
  - organization: org:ibm
    current: true
    basis: linkedin
    label: IBM
    evidence:
    - url: https://www.linkedin.com/in/josh-scriven
      observed_at: '2026-10-24T08:11:36Z'
  affiliation_label: IBM Consulting
  bio: Microsoft Americas Practice AI Leader at IBM Consulting, where he focuses on scaling AI‑assisted
    and agent‑driven development across large enterprise organizations. He works closely with GitHub and
    Microsoft teams to integrate Copilot, automation, and governance‑first patterns into real‑world software
    engineering and modernization efforts. Josh helps enterprises move beyond experimentation to repeatable,
    production‑ready AI development models that balance developer velocity with operational control.
  photo_url: https://static.rainfocus.com/github/universe26/att/1777679202201001q4zO/attprofile/Designer_1792625462054001EcGR.png
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791895677566001pbO0
      ref: session:bld2151d
  accounts:
  - gh:eccolab
  - acct:linkedin/in/josh-scriven
  github: gh:eccolab
  github_resolution: resolved
  github_match: name
  profile: profile:josh-scriven
  featured: false
  sessions:
  - session: session:bld2151d
    role: speaker
  mentions:
  - target: org:microsoft
    text: Microsoft
    field: bio
    method: gazetteer
  - target: software:github-copilot
    text: Copilot
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1777679202201001q4zO
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: eccolab
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Josh Scriven

Microsoft Americas Practice, AI Leader, [IBM](../organizations/ibm.md)

- **GitHub Universe 2026:** speaker (confirmed)

Microsoft Americas Practice AI Leader at IBM Consulting, where he focuses on scaling AI‑assisted and agent‑driven development across large enterprise organizations. He works closely with GitHub and Microsoft teams to integrate Copilot, automation, and governance‑first patterns into real‑world software engineering and modernization efforts. Josh helps enterprises move beyond experimentation to repeatable, production‑ready AI development models that balance developer velocity with operational control.

## Profile

- **Expertise:** AI: Agents, AI: Models, Cloud-native development, Developer experience (DX)
- **Technologies:** GitHub Copilot
- **Interests:** AI agents, AI: Models, Cloud-native development, Developer experience (DX), GitHub Copilot

Evidence for each item: [profile](../profiles/josh-scriven.yaml).

## Affiliations

- Microsoft Americas Practice, AI Leader, [IBM](../organizations/ibm.md) (current; per event listing)
- [IBM](../organizations/ibm.md) (current; per github profile)
- [IBM](../organizations/ibm.md) (current; per linkedin)

## Sessions

- [IBM Neo: From specifications to verified software delivery (Sponsored)](../sessions/bld2151d.md) — Thu Oct 29 2026, 9:55 AM–10:10 AM PDT

## Online

- github: <https://github.com/eccolab>
- linkedin: <https://www.linkedin.com/in/josh-scriven> (via event listing)
