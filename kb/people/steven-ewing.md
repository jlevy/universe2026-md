---
title: Steven Ewing
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:steven-ewing
  name: Steven Ewing
  given_name: Steven
  family_name: Ewing
  job_title: Staff Software Engineer
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:coinbase
    title: Staff Software Engineer
    current: true
    basis: event_listing
    label: Coinbase
  - organization: org:coinbase
    current: true
    basis: linkedin
    label: Coinbase
    evidence:
    - url: https://www.linkedin.com/in/steven-ewing
      observed_at: '2026-10-24T08:15:47Z'
  affiliation_label: Coinbase
  bio: Steven is a veteran developer with two decades immersed in enterprise infrastructure and SaaS at
    giants like Coinbase, Amazon, and NetApp. As a Staff Engineer at Coinbase, he spearheaded the company’s
    migration to GitHub Enterprise Cloud. Beyond the code, his passions range from the complexities of
    coffee and jazz to the artistry of wristwatches and the nostalgia of vintage video games. He finds
    a unique synergy in the world of AI programming, where innovation flows as smoothly as a well-brewed
    cup.
  photo_url: https://static.rainfocus.com/github/universe26/att/1698793901741001Lib6/attprofile/steven_1785859154659001M5yt.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1778094834694001VKKT
      ref: session:ldr1765b
  accounts:
  - gh:stewing
  - acct:linkedin/in/steven-ewing
  github: gh:stewing
  github_resolution: resolved
  github_match: name
  profile: profile:steven-ewing
  featured: false
  sessions:
  - session: session:ldr1765b
    role: speaker
  mentions:
  - target: org:amazon
    text: Amazon
    field: bio
    method: gazetteer
  - target: software:github-enterprise-cloud
    text: GitHub Enterprise Cloud
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1698793901741001Lib6
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: stewing
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Steven Ewing

Staff Software Engineer, [Coinbase](../organizations/coinbase.md)

- **GitHub Universe 2026:** speaker (confirmed)

Steven is a veteran developer with two decades immersed in enterprise infrastructure and SaaS at giants like Coinbase, Amazon, and NetApp. As a Staff Engineer at Coinbase, he spearheaded the company’s migration to GitHub Enterprise Cloud. Beyond the code, his passions range from the complexities of coffee and jazz to the artistry of wristwatches and the nostalgia of vintage video games. He finds a unique synergy in the world of AI programming, where innovation flows as smoothly as a well-brewed cup.

## Profile

- **Expertise:** Developer experience (DX), DevOps and DevSecOps, Governance and compliance, Infrastructure as code, Migration strategies, Monitoring and observability
- **Technologies:** GitHub Actions, GitHub Enterprise Cloud, GitHub Enterprise Server
- **Interests:** Developer experience (DX), DevOps and DevSecOps, GitHub Actions, GitHub Enterprise Cloud, GitHub Enterprise Server, Governance and compliance

Evidence for each item: [profile](../profiles/steven-ewing.yaml).

## Affiliations

- Staff Software Engineer, [Coinbase](../organizations/coinbase.md) (current; per event listing)
- [Coinbase](../organizations/coinbase.md) (current; per linkedin)

## Sessions

- [AI, Actions, and tooling: Coinbase's move to GitHub with data residency](../sessions/ldr1765b.md) — Thu Oct 29 2026, 11:00 AM–11:40 AM PDT

## Online

- github: <https://github.com/stewing>
- linkedin: <https://www.linkedin.com/in/steven-ewing> (via event listing)
