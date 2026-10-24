---
title: Tim Rogers
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:tim-rogers
  name: Tim Rogers
  given_name: Tim
  family_name: Rogers
  job_title: Principal Product Manager
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Principal Product Manager
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: github_profile
    label: '@github'
    evidence:
    - url: https://github.com/timrogers
      quote: '@github'
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/timrogers1
      observed_at: '2026-10-24T08:15:13Z'
  - organization: org:github
    title: Principal Product Manager
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2025'
  - organization: org:github
    title: Staff Product Manager
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2024'
  affiliation_label: GitHub
  bio: Tim is a recovering software engineer and now product manager at GitHub, working on Copilot agents
    in the cloud. Previously, Tim built Copilot cloud agent and Copilot code review, and worked on GitHub’s
    migration tools for moving code and CI/CD pipelines to GitHub.
  photo_url: https://static.rainfocus.com/github/universe26/att/1697183379437001R4Y9/attprofile/Tim%20Rogers_1792537647715001ajAZ.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1792537561954001NSTN
      ref: session:bld2452d
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1758764977768001MMTl
      ref: session:2025/bld1785s
  - event: event:github-universe-2024
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1724855655436001ip2k
      ref: session:2024/1975k
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1722975927915001mscT
      ref: session:2024/ai1898d
  accounts:
  - gh:timrogers
  - acct:linkedin/in/timrogers1
  - acct:x/timrogers
  websites:
  - site:timrogers.co.uk
  github: gh:timrogers
  github_resolution: resolved
  github_match: name
  profile: profile:tim-rogers
  featured: false
  sessions:
  - session: session:2024/1975k
    role: speaker
  - session: session:2024/ai1898d
    role: speaker
  - session: session:2025/bld1785s
    role: facilitator
  - session: session:bld2452d
    role: speaker
  mentions:
  - target: software:github-copilot
    text: Copilot
    field: bio
    method: gazetteer
  - target: software:copilot-code-review
    text: Copilot code review
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1697183379437001R4Y9
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: timrogers
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1697183379437001R4Y9
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1697183379437001R4Y9
    retrieved_at: '2026-10-24T08:03:31Z'
    snapshot: raw/editions/universe24/sessions.json
---
# Tim Rogers

Principal Product Manager, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2025:** speaker (confirmed)
- **GitHub Universe 2024:** speaker (confirmed)

Tim is a recovering software engineer and now product manager at GitHub, working on Copilot agents in the cloud. Previously, Tim built Copilot cloud agent and Copilot code review, and worked on GitHub’s migration tools for moving code and CI/CD pipelines to GitHub.

## Profile

- **Location:** London, UK
- **Expertise:** AI, AI (Agentic AI, Generative AI, Fine-tuned modeling, Models), Code quality, review, and completion, Productivity, Tech debt and security debt, AI: Agents
- **Technologies:** Copilot code review, Copilot coding agent, GitHub Copilot
- **Languages:** TypeScript, Rust, Ruby
- **Interests:** GitHub Copilot, AI, homebrew, VS Code, AI agents, AI: MCP and other integrations

Evidence for each item: [profile](../profiles/tim-rogers.yaml).

## Affiliations

- Principal Product Manager, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- [GitHub](../organizations/github.md) (current; per linkedin)
- Principal Product Manager, [GitHub](../organizations/github.md) (past; per event listing)
- Staff Product Manager, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [Opening keynote](../sessions/2024/1975k.md) — Tue Oct 29 2024, 9:00 AM–9:45 AM PDT
- [In case you missed it: Powerful AI agents and AI-native workflows across GitHub](../sessions/2024/ai1898d.md) — Wed Oct 30 2024, 3:30 PM–3:55 PM PDT
- [The multi-core developer: Unlocking productivity with GitHub Copilot coding agent](../sessions/2025/bld1785s.md) (facilitator) — Tue Oct 28 2025, 3:50 PM–4:50 PM PDT
- [Automate the everyday with Copilot Automations](../sessions/bld2452d.md) — Wed Oct 28 2026, 2:05 PM–2:20 PM PDT

## Online

- github: <https://github.com/timrogers>
- linkedin: <https://www.linkedin.com/in/timrogers1> (via event listing, github profile)
- x: <https://x.com/timrogers> (via event listing, github profile)
- website: <https://timrogers.co.uk> — Tim Rogers
