---
title: Yasuhiro Osaki
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:yasuhiro-osaki
  name: Yasuhiro Osaki
  given_name: Yasuhiro
  family_name: Osaki
  job_title: Software Engineer
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:sony
    title: Software Engineer
    current: true
    basis: event_listing
    label: Sony
  - organization: org:sony
    title: Software Engineer - Sony 2010年 - 現在
    current: true
    basis: linkedin
    label: Sony
    evidence:
    - url: https://www.linkedin.com/in/yasuhiro-osaki-769025b2
      observed_at: '2026-10-24T08:15:40Z'
  affiliation_label: Sony
  bio: "Yasuhiro is a Software Engineer at Sony, where he has spent over a decade driving GitHub adoption\
    \ and serving as GitHub Owner across the organization. Sony’s development landscape spans embedded\
    \ software to web and cloud applications, and he has developed enterprise-specific strategies for\
    \ GitHub utilization at scale. \n\nIn the past year alone, Yasuhiro helped grow GitHub Enterprise\
    \ Cloud users from 4,000 to 7,000 and GitHub Copilot users from 900 to 4,000. He currently advises\
    \ multiple organizations as a GitHub Enterprise Owner. He holds three GitHub Certifications (Actions,\
    \ Admin, and GitHub Advanced Security) and recently spoke at GitHub Universe ’25 Recap Tokyo, receiving\
    \ an audience rating of 4.38 out of 5."
  photo_url: https://static.rainfocus.com/github/universe26/att/1696301111381001ifAP/attprofile/20230329_1785399789757001jGYg.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1777547424946001LZQq
      ref: session:ldr1358d
  accounts:
  - gh:te-yasuhiroosaki
  - acct:linkedin/in/yasuhiro-osaki-769025b2
  github: gh:te-yasuhiroosaki
  github_resolution: resolved
  github_match: name
  profile: profile:yasuhiro-osaki
  featured: false
  sessions:
  - session: session:ldr1358d
    role: speaker
  mentions:
  - target: software:github-enterprise-cloud
    text: GitHub Enterprise Cloud
    field: bio
    method: gazetteer
  - target: software:github-copilot
    text: GitHub Copilot
    field: bio
    method: gazetteer
  - target: software:github-advanced-security
    text: GitHub Advanced Security
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1696301111381001ifAP
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: TE-YasuhiroOsaki
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Yasuhiro Osaki

Software Engineer, [Sony](../organizations/sony.md)

- **GitHub Universe 2026:** speaker (confirmed)

Yasuhiro is a Software Engineer at Sony, where he has spent over a decade driving GitHub adoption and serving as GitHub Owner across the organization. Sony’s development landscape spans embedded software to web and cloud applications, and he has developed enterprise-specific strategies for GitHub utilization at scale. 

In the past year alone, Yasuhiro helped grow GitHub Enterprise Cloud users from 4,000 to 7,000 and GitHub Copilot users from 900 to 4,000. He currently advises multiple organizations as a GitHub Enterprise Owner. He holds three GitHub Certifications (Actions, Admin, and GitHub Advanced Security) and recently spoke at GitHub Universe ’25 Recap Tokyo, receiving an audience rating of 4.38 out of 5.

## Profile

- **Expertise:** AI: Agents, Continuous Integration + Continuous Deployment (CI/CD), Git and code management techniques, Governance and compliance, Infrastructure as code, Productivity
- **Technologies:** GitHub Actions, GitHub Advanced Security, GitHub Copilot, GitHub Enterprise Cloud, Terraform
- **Interests:** AI agents, Continuous Integration + Continuous Deployment (CI/CD), Git and code management techniques, GitHub Actions, GitHub Copilot, GitHub Enterprise Cloud

Evidence for each item: [profile](../profiles/yasuhiro-osaki.yaml).

## Affiliations

- Software Engineer, [Sony](../organizations/sony.md) (current; per event listing)
- Software Engineer - Sony 2010年 - 現在, [Sony](../organizations/sony.md) (current; per linkedin)

## Sessions

- [GitHub configuration as code: Scaling org management with Terraform](../sessions/ldr1358d.md) — Thu Oct 29 2026, 9:15 AM–9:30 AM PDT

## Online

- github: <https://github.com/TE-YasuhiroOsaki>
- linkedin: <https://www.linkedin.com/in/yasuhiro-osaki-769025b2> (via event listing)
