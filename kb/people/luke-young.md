---
title: Luke Young
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:luke-young
  name: Luke Young
  given_name: Luke
  family_name: Young
  job_title: Principal Security Engineer
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:confluent
    title: Principal Security Engineer
    current: true
    basis: event_listing
    label: Confluent
  - organization: org:confluent
    current: true
    basis: linkedin
    label: Confluent
    evidence:
    - url: https://www.linkedin.com/in/bored-engineer
      observed_at: '2026-10-24T08:11:51Z'
  affiliation_label: Confluent
  bio: "Luke Young is a Principal Security Engineer at Confluent, where he focuses on GitHub security,\
    \ CI/CD security, and cloud security. He has presented at DEF CON 23, 24, and 25, and has researched\
    \ a variety of widely used products and network protocols, resulting in more than 50 CVE assignments.\
    \ \n\nPreviously, Luke was a Sr. Staff Security Engineer at LinkedIn, where he worked on the company's\
    \ initial migration to GitHub and helped drive the adoption of CodeQL across LinkedIn's repositories."
  photo_url: https://static.rainfocus.com/github/universe26/att/1777655944022001vjDf/attprofile/Headshot_1786397243971001fjwJ.png
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1777692373101001qvdo
      ref: session:tru1672b
  accounts:
  - gh:lyoung-confluent
  - acct:linkedin/in/bored-engineer
  - acct:x/theboredeng
  websites:
  - site:bored.engineer
  github: gh:lyoung-confluent
  github_resolution: resolved
  github_match: name
  profile: profile:luke-young
  featured: false
  sessions:
  - session: session:tru1672b
    role: speaker
  mentions:
  - target: software:codeql
    text: CodeQL
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1777655944022001vjDf
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: lyoung-confluent
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Luke Young

Principal Security Engineer, [Confluent](../organizations/confluent.md)

- **GitHub Universe 2026:** speaker (confirmed)

Luke Young is a Principal Security Engineer at Confluent, where he focuses on GitHub security, CI/CD security, and cloud security. He has presented at DEF CON 23, 24, and 25, and has researched a variety of widely used products and network protocols, resulting in more than 50 CVE assignments. 

Previously, Luke was a Sr. Staff Security Engineer at LinkedIn, where he worked on the company's initial migration to GitHub and helped drive the adoption of CodeQL across LinkedIn's repositories.

## Profile

- **Expertise:** Governance and compliance, Infrastructure as code, Productivity, Security (RASP, supply chain, threat modeling, vulnerability detection)
- **Technologies:** CodeQL, GitHub Enterprise Cloud, GitHub Enterprise Server
- **Interests:** terraform, terraform-provider, Security, vault, GitHub Enterprise Cloud, GitHub Enterprise Server

Evidence for each item: [profile](../profiles/luke-young.yaml).

## Affiliations

- Principal Security Engineer, [Confluent](../organizations/confluent.md) (current; per event listing)
- [Confluent](../organizations/confluent.md) (current; per linkedin)

## Sessions

- [PATs, rulesets, and IP allowlists: How Confluent secured GitHub Enterprise Cloud](../sessions/tru1672b.md) — Wed Oct 28 2026, 3:30 PM–4:10 PM PDT

## Online

- github: <https://github.com/lyoung-confluent>
- linkedin: <https://www.linkedin.com/in/bored-engineer> (via event listing)
- x: <https://x.com/TheBoredEng> (via event listing)
- website: <https://bored.engineer/>
