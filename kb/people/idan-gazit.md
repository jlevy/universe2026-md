---
title: Idan Gazit
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:idan-gazit
  name: Idan Gazit
  given_name: Idan
  family_name: Gazit
  job_title: Head of GitHub Next
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Head of GitHub Next
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: github_profile
    label: '@github'
    evidence:
    - url: https://github.com/idan
      quote: '@github'
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/idangazit
      observed_at: '2026-10-24T08:11:39Z'
  - organization: org:github
    title: Head of GitHub Next
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2025'
  affiliation_label: GitHub
  bio: Idan leads GitHub Next, the birthplace of GitHub Copilot and many more prototypes that explore
    how AI will make software development faster, easier, safer, and more accessible for developers everywhere.
    As a hybrid designer and developer, his interests span a variety of fields. Idan is keenly interested
    in data display issues, typography, and color. You’re likely to hear him talk about the pit of success
    and the importance of good nouns. Idan was previously a principal engineer at Heroku and is an alumnus
    of the Django web framework’s core development team. He is a firm believer in the power of web technologies
    and is most at home in them. Though many evenings you can find him soldering a new keyboard while
    trying to get Rust to run on a microcontroller.
  photo_url: https://static.rainfocus.com/github/universe26/att/1694120273763001Iy5q/attprofile/Idan_1787603998244001pvYs.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1791904799664001SHnG
      ref: session:2154b
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1787603491482001y0IY
      ref: session:bld1820b
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1745434414420001ipKz
      ref: session:2025/bld1143m
  accounts:
  - gh:idan
  - acct:bluesky/gazit.me
  - acct:linkedin/in/idangazit
  - acct:x/idangazit
  websites:
  - site:gazit.me
  github: gh:idan
  github_resolution: resolved
  github_match: name
  profile: profile:idan-gazit
  featured: false
  sessions:
  - session: session:2025/bld1143m
    role: speaker
  - session: session:2154b
    role: speaker
  - session: session:bld1820b
    role: speaker
  mentions:
  - target: software:github-copilot
    text: GitHub Copilot
    field: bio
    method: gazetteer
  - target: software:rust
    text: Rust
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1694120273763001Iy5q
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: idan
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1694120273763001Iy5q
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
---
# Idan Gazit

Head of GitHub Next, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2025:** speaker (confirmed)

Idan leads GitHub Next, the birthplace of GitHub Copilot and many more prototypes that explore how AI will make software development faster, easier, safer, and more accessible for developers everywhere. As a hybrid designer and developer, his interests span a variety of fields. Idan is keenly interested in data display issues, typography, and color. You’re likely to hear him talk about the pit of success and the importance of good nouns. Idan was previously a principal engineer at Heroku and is an alumnus of the Django web framework’s core development team. He is a firm believer in the power of web technologies and is most at home in them. Though many evenings you can find him soldering a new keyboard while trying to get Rust to run on a microcontroller.

## Profile

- **Location:** East Bay, CA
- **Expertise:** AI (Agentic AI, Generative AI, Fine-tuned modeling, Models), Collaboration, IDE Integration, Productivity
- **Technologies:** GitHub Actions, GitHub Agentic Workflows, GitHub Copilot, GitHub Copilot CLI, Rust, Visual Studio Code
- **Languages:** Python, TypeScript
- **Interests:** GitHub Copilot, python, AI, Collaboration, IDE Integration, Productivity

Evidence for each item: [profile](../profiles/idan-gazit.yaml).

## Affiliations

- Head of GitHub Next, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- [GitHub](../organizations/github.md) (current; per linkedin)
- Head of GitHub Next, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [Continuous AI: A new way to collaborate](../sessions/2025/bld1143m.md) — Wed Oct 29 2025, 11:15 AM–11:45 AM PDT
- [Inside the Lab with GitHub Next](../sessions/2154b.md) — Wed Oct 28 2026, 11:00 AM–11:30 AM PDT
- [What's next with GitHub Next: tomorrow's tools for making software](../sessions/bld1820b.md) — Wed Oct 28 2026, 12:30 PM–1:10 PM PDT

## Online

- github: <https://github.com/idan>
- bluesky: <https://bsky.app/profile/gazit.me> (via event listing, github profile, website link)
- linkedin: <https://www.linkedin.com/in/idangazit> (via event listing, website link)
- x: <https://x.com/idangazit> (via event listing, github profile)
- website: <https://gazit.me> — Idan Gazit
