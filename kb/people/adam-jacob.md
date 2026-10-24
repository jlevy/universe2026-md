---
title: Adam Jacob
softschema:
  contract: paraverse.conference:Person/v1
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: permissive
person:
  id: person:adam-jacob
  name: Adam Jacob
  given_name: Adam
  family_name: Jacob
  job_title: CEO and Co-Founder
  listed_for: event:github-universe-2026
  affiliations:
  - organization: org:swamp-club
    title: CEO and Co-Founder
    current: true
    basis: event_listing
    label: Swamp Club
  - organization: org:swamp-club
    current: true
    basis: linkedin
    label: Swamp Club
    evidence:
    - url: https://www.linkedin.com/in/adamjacob
      observed_at: '2026-10-24T08:11:31Z'
  - organization: org:system-initiative
    current: false
    basis: github_profile
    label: '@systeminit'
    evidence:
    - url: https://github.com/adamhjk
      quote: '@systeminit'
  affiliation_label: Swamp Club
  bio: Adam Jacob is the CEO and co-founder of Swamp Club, which brings deterministic automation to AI
    agents. Before that, he co-founded Chef in 2008 and spent a decade as its CTO, helping bring configuration
    management, infrastructure as code, and DevOps into the world. He calls himself a practical technologist,
    writes regularly at adamhjk.com about being an “absolute AI maximalist,” and is one of the loudest
    public voices arguing that the future of software engineering is building the machine that builds
    the machine.
  photo_url: https://static.rainfocus.com/github/universe26/att/1777675947876001stxC/attprofile/Adam_Cropped%20%281%29_1783651450465001Dcu4.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2026
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe26/attendee-portal/page/sessioncatalog/session/1781738213966001Cmya
      ref: session:bld1776b
  accounts:
  - gh:adamhjk
  - acct:bluesky/adamhjk.me
  - acct:linkedin/in/adamjacob
  - acct:x/adamhjk
  github: gh:adamhjk
  github_resolution: resolved
  github_match: name
  profile: profile:adam-jacob
  featured: false
  sessions:
  - session: session:bld1776b
    role: speaker
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1777675947876001stxC
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: adamhjk
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
---
# Adam Jacob

CEO and Co-Founder, [Swamp Club](../organizations/swamp-club.md)

- **GitHub Universe 2026:** speaker (confirmed)

Adam Jacob is the CEO and co-founder of Swamp Club, which brings deterministic automation to AI agents. Before that, he co-founded Chef in 2008 and spent a decade as its CTO, helping bring configuration management, infrastructure as code, and DevOps into the world. He calls himself a practical technologist, writes regularly at adamhjk.com about being an “absolute AI maximalist,” and is one of the loudest public voices arguing that the future of software engineering is building the machine that builds the machine.

## Profile

- **Location:** San Francisco, CA
- **Expertise:** AI: Agents, AI: MCP and other integrations, Code quality, review, and completion, Collaboration, Governance and compliance, Productivity
- **Technologies:** GitHub Copilot, GitHub Enterprise Cloud, GitHub Enterprise Server, Visual Studio Code
- **Languages:** Ruby, Vim Script
- **Interests:** AI agents, AI: MCP and other integrations, Code quality, review, and completion, Collaboration, GitHub Copilot, GitHub Enterprise Cloud

Evidence for each item: [profile](../profiles/adam-jacob.yaml).

## Affiliations

- CEO and Co-Founder, [Swamp Club](../organizations/swamp-club.md) (current; per event listing)
- [Swamp Club](../organizations/swamp-club.md) (current; per linkedin)
- [System Initiative](../organizations/system-initiative.md) (past; per github profile)

## Sessions

- [Write-only code: What happens to peer review when agents write the diffs](../sessions/bld1776b.md) — Thu Oct 29 2026, 10:00 AM–10:40 AM PDT

## Online

- github: <https://github.com/adamhjk>
- bluesky: <https://bsky.app/profile/adamhjk.me> (via event listing)
- linkedin: <https://www.linkedin.com/in/adamjacob> (via event listing)
- x: <https://x.com/adamhjk> (via event listing, github profile)
