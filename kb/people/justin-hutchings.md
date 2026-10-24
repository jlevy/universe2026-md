---
title: Justin Hutchings
softschema:
  contract: paraverse.conference:Person/v2
  schema: ../_schemas/person.schema.yaml
  envelope: person
  status: enforced
person:
  id: person:justin-hutchings
  name: Justin Hutchings
  given_name: Justin
  family_name: Hutchings
  job_title: Senior Director of Product Management
  listed_for: event:github-universe-2023
  affiliations:
  - organization: org:cloudflare
    current: true
    basis: linkedin
    label: Cloudflare
    evidence:
    - url: https://www.linkedin.com/in/hutchingsjustin
      observed_at: '2026-10-24T08:44:35Z'
  - organization: org:github
    title: Senior Director of Product Management
    current: false
    basis: event_listing
    label: GitHub
  affiliation_label: GitHub
  bio: "Justin is a Senior Director of Product Management for GitHub's security products team and is currently\
    \ responsible for leading the team's investments in securing the software supply chain with Dependabot.\
    \ In his time at GitHub, he's been involved in launching many of our security products and features,\
    \ including code scanning and secret scanning. \n\nPrior to joining GitHub, Justin spent 11 years\
    \ at Microsoft, working on security and developer platforms in Azure Identity, Microsoft Research,\
    \ and Windows. Outside of work, he's an avid sailor, kayaker, and e-cyclist, based in the Pacific\
    \ Northwest with his wife, dog, and two cats."
  photo_url: https://static.rainfocus.com/github/universe23/att/1694702977974001Fqz9/attprofile/image_1694818979325001eXug.jpg
  inclusion_basis: published_by_event
  participations:
  - event: event:github-universe-2023
    role: speaker
    status: confirmed
    evidence:
    - url: https://reg.githubuniverse.com/flow/github/universe23/attendee-portal/page/sessioncatalog/session/1696349684498001ExAS
      ref: session:2023/sec2862g
  accounts:
  - acct:linkedin/in/hutchingsjustin
  - acct:x/jhutchings0
  websites:
  - site:jhutchings.net
  github_resolution: absent
  profile: profile:justin-hutchings
  featured: false
  sessions:
  - session: session:2023/sec2862g
    role: speaker
  mentions:
  - target: software:dependabot
    text: Dependabot
    field: bio
    method: gazetteer
  - target: org:microsoft
    text: Microsoft
    field: bio
    method: gazetteer
  - target: software:azure
    text: Azure
    field: bio
    method: gazetteer
  - target: software:windows
    text: Windows
    field: bio
    method: gazetteer
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1694702977974001Fqz9
    retrieved_at: '2026-10-24T08:03:37Z'
    snapshot: raw/editions/universe23/sessions.json
---
# Justin Hutchings

[Cloudflare](../organizations/cloudflare.md)

Listed for GitHub Universe 2023 as Senior Director of Product Management, GitHub.

- **GitHub Universe 2023:** speaker (confirmed)

Justin is a Senior Director of Product Management for GitHub's security products team and is currently responsible for leading the team's investments in securing the software supply chain with Dependabot. In his time at GitHub, he's been involved in launching many of our security products and features, including code scanning and secret scanning. 

Prior to joining GitHub, Justin spent 11 years at Microsoft, working on security and developer platforms in Azure Identity, Microsoft Research, and Windows. Outside of work, he's an avid sailor, kayaker, and e-cyclist, based in the Pacific Northwest with his wife, dog, and two cats.

## Profile

- **Expertise:** DevSecOps, Security, Supply Chain Security, Vulnerability Detection
- **Technologies:** Dependabot, Microsoft Azure, Windows
- **Interests:** Supply Chain Security, DevSecOps, GitHub Advanced Security, Security, Vulnerability Detection

Evidence for each item: [profile](../profiles/justin-hutchings.yaml).

## Affiliations

- [Cloudflare](../organizations/cloudflare.md) (current; per linkedin)
- Senior Director of Product Management, [GitHub](../organizations/github.md) (past; per event listing)

## Sessions

- [Dependencies wrangled: proven practices to secure the software supply chain](../sessions/2023/sec2862g.md) — Wed Nov 8 2023, 3:30 PM–4:10 PM PST

## Online

- linkedin: <https://www.linkedin.com/in/hutchingsjustin> (via event listing)
- x: <https://x.com/jhutchings0> (via event listing)
- website: <https://www.jhutchings.net/>
