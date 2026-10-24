---
title: Sam Morrow
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:sam-morrow
  name: Sam Morrow
  given_name: Sam
  family_name: Morrow
  job_title: Staff Software Engineer
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:github
    title: Staff Software Engineer
    current: true
    basis: event_listing
    label: GitHub
  - organization: org:github
    current: true
    basis: linkedin
    label: GitHub
    evidence:
    - url: https://www.linkedin.com/in/sammorrow
      observed_at: '2026-10-24T08:15:32Z'
  - organization: org:github
    title: Senior Software Engineer
    current: false
    basis: event_listing
    label: GitHub
    evidence:
    - observed_at: '2025'
  affiliation_label: GitHub
  bio: Sam is a passionate full-stack engineer, official MCP Maintainer and coauthor of the GitHub MCP
    server, dedicated to building seamless interfaces between humans, agents, and code. With a track record
    of leading innovative projects at GitHub and a deep background in both open- and closed-source development,
    Sam brings a unique perspective to the intersection of AI and developer experience. He has helped
    shape the future of agentic workflows on GitHub, collaborating closely with the open source community
    and industry pioneers. Outside of tech, Sam is a former professional drummer and enjoys blending creativity
    with engineering—whether on stage or in the codebase.
  photo_url: https://static.rainfocus.com/github/universe26/att/1685606809874001rJOG/attprofile/IMG_9812%20%281%29%20%281%29_1785441766445001jNRL.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1790875955550001cVXm
      ref: session:bld2008d
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1777512208544001YnaL
      ref: session:tru1338w
  - event: event:github-universe-2025
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe25/attendee-portal/page/sessioncatalog/session/1745619400904001YKhB
      ref: session:2025/bld1168d
  accounts:
  - gh:sammorrowdrums
  - acct:bluesky/sammorrowdrums.bsky.social
  - acct:linkedin/in/sammorrow
  - acct:x/sammorrowdrums
  websites:
  - site:sam-morrow.com
  - site:sam-morrow.com/blog
  github: gh:sammorrowdrums
  github_resolution: resolved
  github_match: name
  profile: profile:sam-morrow
  featured: false
  sessions:
  - session: session:2025/bld1168d
    role: speaker
  - session: session:bld2008d
    role: speaker
  - session: session:tru1338w
    role: facilitator
  mentions:
  - target: software:model-context-protocol
    text: MCP
    field: bio
    method: gazetteer
  - target: software:github-mcp-server
    text: GitHub MCP server
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1685606809874001rJOG
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: SamMorrowDrums
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1685606809874001rJOG
    retrieved_at: '2026-10-24T08:03:23Z'
    snapshot: raw/editions/universe25/sessions.json
---
# Sam Morrow

Staff Software Engineer, [GitHub](../organizations/github.md)

- **GitHub Universe 2026:** speaker (confirmed)
- **GitHub Universe 2025:** speaker (confirmed)

Sam is a passionate full-stack engineer, official MCP Maintainer and coauthor of the GitHub MCP server, dedicated to building seamless interfaces between humans, agents, and code. With a track record of leading innovative projects at GitHub and a deep background in both open- and closed-source development, Sam brings a unique perspective to the intersection of AI and developer experience. He has helped shape the future of agentic workflows on GitHub, collaborating closely with the open source community and industry pioneers. Outside of tech, Sam is a former professional drummer and enjoys blending creativity with engineering—whether on stage or in the codebase.

## Profile

- **Location:** Amsterdam, Netherlands
- **Expertise:** AI (Agentic AI, Generative AI, Fine-tuned modeling, Models), IDE Integration, Open source, AI: Agents, AI: MCP and other integrations, Security (RASP, supply chain, threat modeling, vulnerability detection)
- **Technologies:** GitHub Code Security, GitHub Copilot, GitHub Copilot CLI, GitHub MCP Server, Microsoft Azure, Model Context Protocol, Visual Studio Code
- **Languages:** Python
- **Interests:** GitHub Copilot, golang, mcp, python, remarkable-tablet, AI

Evidence for each item: [profile](../profiles/sam-morrow.yaml).

## Affiliations

- Staff Software Engineer, [GitHub](../organizations/github.md) (current; per event listing)
- [GitHub](../organizations/github.md) (current; per linkedin)
- Senior Software Engineer, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [Extending AI Agents: A live demo of the GitHub MCP Server](../sessions/2025/bld1168d.md) — Wed Oct 29 2025, 12:00 PM–12:15 PM PDT
- [Connecting Copilot](../sessions/bld2008d.md) — Wed Oct 28 2026, 4:30 PM–4:45 PM PDT
- [Securing MCP: Real exploits, what actually mitigates them, and what doesn't](../sessions/tru1338w.md) (facilitator) — Wed Oct 28 2026, 10:30 AM–12:00 PM PDT

## Online

- github: <https://github.com/SamMorrowDrums>
- bluesky: <https://bsky.app/profile/sammorrowdrums.bsky.social> (via event listing)
- linkedin: <https://www.linkedin.com/in/sammorrow> (via event listing, github profile)
- x: <https://x.com/SamMorrowDrums> (via event listing, github profile)
- website: <https://sam-morrow.com> — Sam Morrow
- website: <https://www.sam-morrow.com/blog> — Blog | Sam Morrow
