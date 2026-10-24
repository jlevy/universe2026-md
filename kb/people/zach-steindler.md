---
title: Zach Steindler
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:zach-steindler
  name: Zach Steindler
  given_name: Zach
  family_name: Steindler
  job_title: Principal Engineer
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Principal Engineer
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/steiza
      observed_at: '2026-10-24T08:15:09Z'
  - organization: org:github
    title: Principal Engineer
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2025'
  affiliation_label: GitHub
  bio: Zach is the chair of the OpenSSF Technical Advisory Council and co-chair of the Securing Repositories
    Working Group, which helps coordinate security improvements in programming language package repositories
    like PyPI and RubyGems. He works at GitHub on securing software development for open source and enterprises.
    Away from computers, he enjoys gardening and welding.
  photo_url: https://static.rainfocus.com/github/universe26/att/1698956387483001A8Kv/attprofile/zach_cropped_1776954822649001G07B.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1776954516891001V7aB
      ref: session:tru1173d
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1744311125177001b4jS
      ref: session:2025/sec1073d
  accounts:
  - gh:steiza
  - acct:linkedin/in/steiza
  - acct:mastodon/steiza@a2mi.social
  websites:
  - site:coffeehousecoders.org
  github: gh:steiza
  github_resolution: resolved
  github_match: name
  profile: profile:zach-steindler
  featured: false
  sessions:
  - session: session:2025/sec1073d
    role: speaker
  - session: session:tru1173d
    role: speaker
  mentions:
  - target: org:openssf
    text: OpenSSF
    field: bio
    method: gazetteer
  - target: software:pypi
    text: PyPI
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1698956387483001A8Kv
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: steiza
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1698956387483001A8Kv
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
---
# Zach Steindler

Principal Engineer, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2025:** speaker (confirmed)

Zach is the chair of the OpenSSF Technical Advisory Council and co-chair of the Securing Repositories Working Group, which helps coordinate security improvements in programming language package repositories like PyPI and RubyGems. He works at GitHub on securing software development for open source and enterprises. Away from computers, he enjoys gardening and welding.

## Profile

- **Expertise:** Cloud-native development, Containerized applications, Continuous Integration + Continuous Deployment (CI/CD), Governance and compliance, Kubernetes, Security (RASP, supply chain, threat modeling, vulnerability detection)
- **Technologies:** GitHub Actions, PyPI
- **Languages:** Python, PostScript, OpenSCAD, HTML, Go
- **Interests:** Continuous Integration + Continuous Deployment (CI/CD), GitHub Actions, Security, Cloud-native development, Containerized applications, GitHub Enterprise Cloud

Evidence for each item: [profile](../profiles/zach-steindler.yaml).

## Affiliations

- Principal Engineer, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per linkedin)
- Principal Engineer, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [Get a handle on securing your build process with Artifact Attestations](../sessions/2025/sec1073d.md) — Tue Oct 28 2025, 3:50 PM–4:05 PM PDT
- [Your CI has full internet access. GitHub Actions firewall changes that.](../sessions/tru1173d.md) — Thu Oct 29 2026, 11:45 AM–12:00 PM PDT

## Online

- github: <https://github.com/steiza>
- linkedin: <https://www.linkedin.com/in/steiza> (via event listing, github profile, website link)
- mastodon: <https://a2mi.social/@steiza> (via github profile, website link)
- website: <https://coffeehousecoders.org> — Coffee House Coders
