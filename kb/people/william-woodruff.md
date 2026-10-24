---
title: William Woodruff
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:william-woodruff
  name: William Woodruff
  given_name: William
  family_name: Woodruff
  job_title: Member of Technical Staff
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:openai
    title: Member of Technical Staff
    current: true
    basis: event_listing
    label: OpenAI
  - organization: org:openai
    current: true
    basis: github_profile
    label: '@astral-sh @openai'
    evidence:
    - url: https://github.com/woodruffw
      quote: '@astral-sh @openai'
  - organization: org:astral
    current: false
    basis: github_profile
    label: '@astral-sh @openai'
    evidence:
    - url: https://github.com/woodruffw
      quote: '@astral-sh @openai'
  affiliation_label: OpenAI
  bio: |-
    William is a Member of Technical Staff at OpenAI, working on high-performance and secure Python tooling. He previously worked at Astral on the same tooling, and prior to that was an Engineering Director at Trail of Bits, where he ran a team responsible for high-impact security contributions to open source ecosystems.

    Outside of work, William is the primary maintainer of zizmor, one of the maintainers of Homebrew, and a long-term contributor to Python packaging (PyPA, PyPI) and Python cryptography.
  photo_url: https://static.rainfocus.com/github/universe26/att/1715352580561001WhDd/attprofile/3059210_1777507440462001zwi7.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1777507244576001uh1q
      ref: session:tru1333b
  accounts:
  - gh:woodruffw
  - acct:bluesky/yossarian.net
  - acct:mastodon/yossarian@infosec.exchange
  websites:
  - site:blog.yossarian.net
  - site:yossarian.net
  github: gh:woodruffw
  github_resolution: resolved
  github_match: name
  profile: profile:william-woodruff
  featured: false
  sessions:
  - session: session:tru1333b
    role: speaker
  mentions:
  - target: software:python
    text: Python
    field: bio
    method: gazetteer
  - target: software:homebrew
    text: Homebrew
    field: bio
    method: gazetteer
  - target: software:pypi
    text: PyPI
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1715352580561001WhDd
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: woodruffw
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# William Woodruff

Member of Technical Staff, [OpenAI](../organizations/openai.md)

- **GitHub Universe 2026:** speaker (confirmed)

William is a Member of Technical Staff at OpenAI, working on high-performance and secure Python tooling. He previously worked at Astral on the same tooling, and prior to that was an Engineering Director at Trail of Bits, where he ran a team responsible for high-impact security contributions to open source ecosystems.

Outside of work, William is the primary maintainer of zizmor, one of the maintainers of Homebrew, and a long-term contributor to Python packaging (PyPA, PyPI) and Python cryptography.

## Profile

- **Location:** New York, NY
- **Expertise:** AI: Agents, Security (RASP, supply chain, threat modeling, vulnerability detection)
- **Technologies:** Dependabot, GitHub Actions, GitHub Code Security, Homebrew, PyPI, Python
- **Languages:** Rust, PowerShell, Python
- **Interests:** python, rust, GitHub Actions, Security, age, cryptography

Evidence for each item: [profile](../profiles/william-woodruff.yaml).

## Affiliations

- Member of Technical Staff, [OpenAI](../organizations/openai.md) (current; per event listing)
- [OpenAI](../organizations/openai.md) (current; per github profile)
- [Astral](../organizations/astral.md) (past; per github profile)

## Sessions

- [Security by default: a maintainer’s wishlist for GitHub Actions v2](../sessions/tru1333b.md) — Wed Oct 28 2026, 4:30 PM–5:10 PM PDT

## Online

- github: <https://github.com/woodruffw>
- bluesky: <https://bsky.app/profile/yossarian.net> (via event listing, github profile)
- mastodon: <https://infosec.exchange/@yossarian> (via github profile, website link)
- website: <https://blog.yossarian.net> — ENOSUCHBLOG
- website: <https://yossarian.net> — william woodruff
