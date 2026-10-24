---
title: Pierre Tempel
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:pierre-tempel
  name: Pierre Tempel
  given_name: Pierre
  family_name: Tempel
  job_title: Director, Product Management
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Director, Product Management
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: github_profile
    label: '@GitHub'
    evidence:
    - url: https://github.com/turbo
      quote: '@GitHub'
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/pierre-tempel
      observed_at: '2026-10-24T08:15:29Z'
  - organization: org:github
    title: Director, Product Management
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
  - organization: org:github
    title: Staff Product Manager, CodeQL
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2023'
  affiliation_label: GitHub
  bio: |-
    Pierre is a director of product management at GitHub, responsible for the detection and AI-powered remediation engines that power GitHub Advanced Security, Copilot Code Review, and Copilot Autofix — helping thousands of open source projects and enterprises find and fix vulnerabilities before they ship. He partners with engineering, product, and design to expand language coverage, improve performance, and advance AI-driven autofix so that powerful application security capabilities remain both developer-friendly and freely available to the open source community.

    Previously, he shaped tech strategy and supply chain security programs at SolarWinds in the aftermath of its high-profile supply chain attack, founded and advised security startups, briefed governments and media on cyber risk, and mentored emerging technical leaders. Based in Berlin, he continues to advocate for secure-by-default software development.
  photo_url: https://static.rainfocus.com/github/universe26/att/1695047674656001ZiRw/attprofile/cheeky%20suit%201_1777569591357001qjuJ.jpeg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1777570438940001jRHI
      ref: session:tru1397b
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1758133014148001fiCB
      ref: session:2025/sec1741m
  - event: event:github-universe-2024
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1715199684928001mQKz
      ref: session:2024/sec1367s
    - url: https://reg.githubuniverse.com/flow/github/universe24/attendee-portal/page/sessioncatalog/session/1724850006966001X7lz
      ref: session:2024/sec1972d
  - event: event:github-universe-2023
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe23/attendee-portal/page/sessioncatalog/session/1692906208509001tqhC
      ref: session:2023/sec2753d
  accounts:
  - gh:turbo
  - acct:linkedin/in/pierre-tempel
  - acct:x/summarity
  websites:
  - site:summarity.com
  github: gh:turbo
  github_resolution: resolved
  github_match: name
  profile: profile:pierre-tempel
  featured: false
  sessions:
  - session: session:2023/sec2753d
    role: speaker
  - session: session:2024/sec1367s
    role: facilitator
  - session: session:2024/sec1972d
    role: speaker
  - session: session:2025/sec1741m
    role: speaker
  - session: session:tru1397b
    role: speaker
  mentions:
  - target: software:github-advanced-security
    text: GitHub Advanced Security
    field: bio
    method: gazetteer
  - target: software:github-copilot
    text: Copilot
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1695047674656001ZiRw
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: turbo
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1695047674656001ZiRw
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1695047674656001ZiRw
    retrieved_at: '2026-10-24T08:03:31Z'
    snapshot: raw/editions/universe24/sessions.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1695047674656001ZiRw
    retrieved_at: '2026-10-24T08:03:37Z'
    snapshot: raw/editions/universe23/sessions.json
---
# Pierre Tempel

Director, Product Management, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2025:** speaker (confirmed)
- **GitHub Universe 2024:** speaker (confirmed)
- **GitHub Universe 2023:** speaker (confirmed)

Pierre is a director of product management at GitHub, responsible for the detection and AI-powered remediation engines that power GitHub Advanced Security, Copilot Code Review, and Copilot Autofix — helping thousands of open source projects and enterprises find and fix vulnerabilities before they ship. He partners with engineering, product, and design to expand language coverage, improve performance, and advance AI-driven autofix so that powerful application security capabilities remain both developer-friendly and freely available to the open source community.

Previously, he shaped tech strategy and supply chain security programs at SolarWinds in the aftermath of its high-profile supply chain attack, founded and advised security startups, briefed governments and media on cyber risk, and mentored emerging technical leaders. Based in Berlin, he continues to advocate for secure-by-default software development.

## Profile

- **Location:** Berlin, Germany
- **Expertise:** Security, Artificial Intelligence (AI), DevSecOps, Security, Supply Chain Security, Vulnerability Detection
- **Technologies:** CodeQL, GitHub Advanced Security, GitHub Code Security, GitHub Copilot
- **Languages:** Nim, JavaScript, C, PLpgSQL, C++
- **Interests:** GitHub Copilot, Security, GitHub Advanced Security, AI, Code quality, review, and completion, GitHub Code Security

Evidence for each item: [profile](../profiles/pierre-tempel.yaml).

## Affiliations

- Director, Product Management, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per github profile)
- [GitHub](../organizations/github.md) (current; per linkedin)
- Director, Product Management, [GitHub](../organizations/github.md) (past; per event listing)
- Staff Product Manager, [GitHub](../organizations/github.md) (past; per event listing)
- Staff Product Manager, CodeQL, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [GitHub Advanced Security: Turbocharging AppSec with AI](../sessions/2023/sec2753d.md) — Wed Nov 8 2023, 10:30 AM–10:55 AM PST
- [Copilot Autofix: Shaping the future of secure coding practices](../sessions/2024/sec1367s.md) (facilitator) — Wed Oct 30 2024, 11:30 AM–12:10 PM PDT
- [How code scanning in GitHub Advanced Security burns down security debt](../sessions/2024/sec1972d.md) — Wed Oct 30 2024, 2:30 PM–2:55 PM PDT
- [GitHub Code Security in action: Accelerating risk reduction at enterprise scale](../sessions/2025/sec1741m.md) — Tue Oct 28 2025, 3:20 PM–3:50 PM PDT
- [Agentic security for every developer](../sessions/tru1397b.md) — Wed Oct 28 2026, 2:30 PM–3:10 PM PDT

## Online

- github: <https://github.com/turbo>
- linkedin: <https://www.linkedin.com/in/pierre-tempel> (via event listing, website link)
- x: <https://x.com/summarity> (via event listing, github profile, website link)
- website: <https://summarity.com> — Summarity
