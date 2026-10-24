---
title: Datadog
softschema:
  contract: paraverse.conference:Organization/v1
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: permissive
organization:
  id: org:datadog
  name: Datadog
  roles:
  - affiliation
  - mentioned
  - sponsor
  description: Datadog is an observability and security platform that unifies metrics, traces, logs, and
    security signals for centralized visibility on dynamic environments.
  descriptions:
  - text: Datadog is an observability and security platform that unifies metrics, traces, logs, and security
      signals for centralized visibility on dynamic environments.
    basis: sponsor_listing
  - text: See inside any stack, any app, at any scale, anywhere.
    basis: website
  logo_url: https://corp.dd-static.net/img/og/og-image-10-25.png?fit=crop&w=1200&h=630
  website: https://www.datadoghq.com
  github: gh:datadog
  accounts:
  - gh:datadog
  - acct:x/datadoghq
  sponsorship:
    tier: bronze
    summary: Datadog is an observability and security platform that unifies metrics, traces, logs, and
      security signals for centralized visibility on dynamic environments.
    link: https://www.datadoghq.com
    logo_url: https://static.rainfocus.com/github/universe26/exh/1694599648010001zRbv/catalogtileimage/Virtual-Thumbnail_Resized_260519_1779220422184001yU0y.jpg
    exhibitor_id: 1694599648010001zRbv
  mentioned_in:
  - session:2023/dev2893d
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/exhibitors
    record_id: 1694599648010001zRbv
    retrieved_at: '2026-10-24T06:46:26Z'
    snapshot: raw/rainfocus/exhibitors.json
  - system: github
    url: https://api.github.com/graphql
    record_id: DataDog
    retrieved_at: '2026-10-24T19:09:58Z'
    snapshot: raw/github/sponsor-orgs.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1697575302521001BxX4
    retrieved_at: '2026-10-24T08:03:37Z'
    snapshot: raw/editions/universe23/sessions.json
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1697575203227001EdFI
    retrieved_at: '2026-10-24T08:03:37Z'
    snapshot: raw/editions/universe23/sessions.json
  - system: website
    url: https://www.datadoghq.com
    record_id: https://www.datadoghq.com
    retrieved_at: '2026-10-24T08:43:43Z'
    snapshot: raw/websites/org-homepages.json
---
# Datadog

**Bronze sponsor.** Datadog is an observability and security platform that unifies metrics, traces, logs, and security signals for centralized visibility on dynamic environments.

Website: <https://www.datadoghq.com>

## Mentioned in

- [Pipeline observability: The key to better software team performance](../sessions/2023/dev2893d.md)
