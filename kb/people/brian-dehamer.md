---
title: Brian DeHamer
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:brian-dehamer
  name: Brian DeHamer
  given_name: Brian
  family_name: DeHamer
  job_title: Staff Software Engineer
  listed_for: event:github-universe-2025
  affiliations:
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/bdehamer
      observed_at: '2026-10-24T08:43:01Z'
  - organization: org:github
    title: Staff Software Engineer
    current: false
    basis: event_listing
    label: GitHub
  affiliation_label: GitHub
  bio: Brian is a Staff Engineer at GitHub, where he works on improving the security and transparency
    of the software supply chain. With over 30 years of experience in the software industry, Brian has
    spent most of his career focused on enhancing developer experience across a wide range of tools and
    platforms. At GitHub, he has played a key role in bringing support for provenance attestations to
    npm and to artifacts built on GitHub Actions.
  photo_url: https://static.rainfocus.com/github/universe25/att/1686593528195001MBdN/attprofile/IMG_3683_1756411810978001qKkk.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1746238472345001zMNN
      ref: session:2025/aut1451d
  accounts:
  - acct:linkedin/in/bdehamer
  github_resolution: absent
  profile: profile:brian-dehamer
  featured: false
  sessions:
  - session: session:2025/aut1451d
    role: speaker
  mentions:
  - target: software:npm-registry
    text: npm
    field: bio
    method: gazetteer
  - target: software:github-actions
    text: GitHub Actions
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1686593528195001MBdN
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
---
# Brian DeHamer

[GitHub](../organizations/github.md)

Listed for GitHub Universe 2025 as Staff Software Engineer, GitHub.

- **GitHub Universe 2025:** speaker (confirmed)

Brian is a Staff Engineer at GitHub, where he works on improving the security and transparency of the software supply chain. With over 30 years of experience in the software industry, Brian has spent most of his career focused on enhancing developer experience across a wide range of tools and platforms. At GitHub, he has played a key role in bringing support for provenance attestations to npm and to artifacts built on GitHub Actions.

## Profile

- **Expertise:** Open source, Security (RASP, supply chain, threat modeling, vulnerability detection)
- **Technologies:** GitHub Actions, npm
- **Interests:** Open source, Security

Evidence for each item: [profile](../profiles/brian-dehamer.yaml).

## Affiliations

- [GitHub](../organizations/github.md) (current; per linkedin)
- Staff Software Engineer, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [Immutable releases: How to create trust, transparency, and verifiability](../sessions/2025/aut1451d.md) — Tue Oct 28 2025, 11:30 AM–11:45 AM PDT

## Online

- linkedin: <https://www.linkedin.com/in/bdehamer> (via event listing)
