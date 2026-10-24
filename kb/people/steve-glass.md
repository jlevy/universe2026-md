---
title: Steve Glass
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:steve-glass
  name: Steve Glass
  given_name: Steve
  family_name: Glass
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
    label: GitHub
    evidence:
    - url: https://github.com/Steve-Glass
      quote: GitHub
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/sglass1
      observed_at: '2026-10-24T08:15:33Z'
  affiliation_label: GitHub
  bio: |-
    Stephen Glass is a Senior Product Manager at GitHub, where he leads the strategy and roadmap for securing GitHub Actions across identity, policy, and infrastructure, shaping how some of the world’s largest enterprises protect their CI/CD environments and software supply chains. With more than a decade of experience across product management, engineering, and developer platforms, he’s spent the last several years advancing CI/CD security and secure software delivery, driving GitHub Actions innovations like workload identity federation, policy-based controls, and software supply chain protections. He also co-authored GitHub’s Actions security roadmap.

    An active member of the developer community, Stephen regularly shares insights on software supply chain security and platform engineering; learn more at sglass.dev. When he’s not thinking about CI/CD pipelines, he can usually be found mountain biking, playing basketball, or spending time with his family.
  photo_url: https://static.rainfocus.com/github/universe26/att/1777473235971001H2Xj/attprofile/Steve%20Glass_1782312045910001YXqp.png
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1777658986177001QNCH
      ref: session:tru1556m
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1790267895282001BYJW
      ref: session:tru1914a
  accounts:
  - gh:steve-glass
  - acct:linkedin/in/sglass1
  github: gh:steve-glass
  github_resolution: resolved
  github_match: name
  profile: profile:steve-glass
  featured: false
  sessions:
  - session: session:tru1556m
    role: speaker
  - session: session:tru1914a
    role: speaker
  mentions:
  - target: software:github-actions
    text: GitHub Actions
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1777473235971001H2Xj
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: Steve-Glass
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Steve Glass

Senior Product Manager, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)

Stephen Glass is a Senior Product Manager at GitHub, where he leads the strategy and roadmap for securing GitHub Actions across identity, policy, and infrastructure, shaping how some of the world’s largest enterprises protect their CI/CD environments and software supply chains. With more than a decade of experience across product management, engineering, and developer platforms, he’s spent the last several years advancing CI/CD security and secure software delivery, driving GitHub Actions innovations like workload identity federation, policy-based controls, and software supply chain protections. He also co-authored GitHub’s Actions security roadmap.

An active member of the developer community, Stephen regularly shares insights on software supply chain security and platform engineering; learn more at sglass.dev. When he’s not thinking about CI/CD pipelines, he can usually be found mountain biking, playing basketball, or spending time with his family.

## Profile

- **Location:** Maryland
- **Expertise:** AI: Agents, Continuous Integration + Continuous Deployment (CI/CD), DevOps and DevSecOps, Governance and compliance, Monitoring and observability, Open source
- **Technologies:** GitHub Actions, GitHub Code Security
- **Interests:** GitHub Actions, Security, Supply Chain Security, AI agents, Continuous Integration + Continuous Deployment (CI/CD), DevOps and DevSecOps

Evidence for each item: [profile](../profiles/steve-glass.yaml).

## Affiliations

- Senior Product Manager, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- [GitHub](../organizations/github.md) (current; per linkedin)

## Sessions

- [Disrupting supply chain attacks: A threat framework for GitHub Actions](../sessions/tru1556m.md) — Wed Oct 28 2026, 2:30 PM–3:00 PM PDT
- [Session After Party: Disrupting supply chain attacks: A threat framework for GitHub Actions](../sessions/tru1914a.md) — Wed Oct 28 2026, 3:15 PM–3:45 PM PDT

## Online

- github: <https://github.com/Steve-Glass>
- linkedin: <https://www.linkedin.com/in/sglass1> (via event listing)
