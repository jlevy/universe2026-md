---
title: Baruch Sadogursky
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:baruch-sadogursky
  name: Baruch Sadogursky
  given_name: Baruch
  family_name: Sadogursky
  job_title: Head of Developer Relations
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:port
    title: Head of Developer Relations
    current: true
    basis: event_listing
    label: Port.io
  - organization: org:port
    current: true
    basis: linkedin
    label: Port.io
    evidence:
    - url: https://www.linkedin.com/in/jbaruch
      observed_at: '2026-10-24T08:11:36Z'
  affiliation_label: Port.io
  bio: "Baruch Sadogursky (@jbaruch) worked with Java before it had generics, practiced DevOps before\
    \ Docker existed, and built developer relations before it had a name. He built JFrog’s DevRel function\
    \ as the company grew from 10 people through its initial public offering. Baruch co-authored \"Liquid\
    \ Software\" and \"DevOps Tools for Java Developers\" and is a Java Champion, Microsoft MVP, and CNCF\
    \ Ambassador alum. \n\nToday, Baruch is obsessed with how AI agents write code. At Tessl, an AI agent\
    \ enablement platform, he works on engineering, managing, and sharing context with agents. He also\
    \ shares his knowledge with developers through blog posts, meetups, and conferences including DevNexus,\
    \ QCon, KubeCon, and Devoxx, often explaining why vibe coding doesn’t scale."
  photo_url: https://static.rainfocus.com/github/universe26/att/1786298949043001shg7/attprofile/Photo%20from%20Google%20Photos_1789597588175001ojQo.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1786375713754001DtuA
      ref: session:bld1810d
  accounts:
  - gh:jbaruch-port
  - acct:bluesky/jbaru.ch
  - acct:linkedin/in/jbaruch
  github: gh:jbaruch-port
  github_resolution: resolved
  github_match: name
  profile: profile:baruch-sadogursky
  featured: false
  sessions:
  - session: session:bld1810d
    role: speaker
  mentions:
  - target: software:java
    text: Java
    field: bio
    method: gazetteer
  - target: software:docker
    text: Docker
    field: bio
    method: gazetteer
  - target: org:jfrog
    text: JFrog
    field: bio
    method: gazetteer
  - target: org:microsoft
    text: Microsoft
    field: bio
    method: gazetteer
  - target: org:cncf
    text: CNCF
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1786298949043001shg7
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: jbaruch-port
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Baruch Sadogursky

Head of Developer Relations, [Port](../organizations/port.md)

- **GitHub Universe 2026:** speaker (confirmed)

Baruch Sadogursky (@jbaruch) worked with Java before it had generics, practiced DevOps before Docker existed, and built developer relations before it had a name. He built JFrog’s DevRel function as the company grew from 10 people through its initial public offering. Baruch co-authored "Liquid Software" and "DevOps Tools for Java Developers" and is a Java Champion, Microsoft MVP, and CNCF Ambassador alum. 

Today, Baruch is obsessed with how AI agents write code. At Tessl, an AI agent enablement platform, he works on engineering, managing, and sharing context with agents. He also shares his knowledge with developers through blog posts, meetups, and conferences including DevNexus, QCon, KubeCon, and Devoxx, often explaining why vibe coding doesn’t scale.

## Profile

- **Expertise:** Agile practices, AI: Agents, AI: MCP and other integrations, Automated Infrastructure Deployment, Code quality, review, and completion, Continuous Integration + Continuous Deployment (CI/CD)
- **Technologies:** Docker, GitHub Actions, GitHub Copilot, Java
- **Recognitions:** Microsoft MVP, Java Champion
- **Interests:** Agile practices, AI agents, AI: MCP and other integrations, Automated Infrastructure Deployment, Code quality, review, and completion, Continuous Integration + Continuous Deployment (CI/CD)

Evidence for each item: [profile](../profiles/baruch-sadogursky.yaml).

## Affiliations

- Head of Developer Relations, [Port](../organizations/port.md) (current; per event listing)
- [Port](../organizations/port.md) (current; per linkedin)

## Sessions

- [When a prototype becomes critical, does your GitHub policy know? (Sponsored)](../sessions/bld1810d.md) — Thu Oct 29 2026, 9:35 AM–9:50 AM PDT

## Online

- github: <https://github.com/jbaruch-port>
- bluesky: <https://bsky.app/profile/jbaru.ch> (via event listing)
- linkedin: <https://www.linkedin.com/in/jbaruch> (via event listing)
