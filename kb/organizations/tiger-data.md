---
title: Tiger Data
softschema:
  contract: paraverse.conference:Organization/v2
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: enforced
organization:
  id: org:tiger-data
  name: Tiger Data
  aliases:
  - Tiger Data (creators of TimescaleDB)
  roles:
  - affiliation
  description: 'Tiger Data is addressing one of the largest challenges (and opportunities) in databases
    for years to come: helping developers, businesses, and society make sense of the data that humans
    and their machines are generating in copious amounts. Tiger Data is the fastest PostgreSQL cloud platform
    that natively supports full-SQL, combining the power, reliability, and ease-of-use of a relational
    database with the scalability typically seen in NoSQL systems. It is built on PostgreSQL and optimized
    for fast ingest and complex queries. Tiger Data is deployed for powering mission-critical applications,
    including industrial data analysis, complex monitoring systems, operational data warehousing, financial
    risk management, and geospatial asset tracking across industries as varied as manufacturing, space,
    utilities, oil & gas, logistics, mining, ad tech, finance, telecom, and more. Tiger Data is backed
    by NEA, Benchmark, Icon Ventures, Redpoint Ventures, Two Sigma Ventures, and Tiger Global. Documentation:
    https://docs.tigerdata.com/ GitHub: https://github.com/timescale/timescaledb Twitter: https://x.com/TimescaleDB'
  descriptions:
  - text: 'Tiger Data is addressing one of the largest challenges (and opportunities) in databases for
      years to come: helping developers, businesses, and society make sense of the data that humans and
      their machines are generating in copious amounts. Tiger Data is the fastest PostgreSQL cloud platform
      that natively supports full-SQL, combining the power, reliability, and ease-of-use of a relational
      database with the scalability typically seen in NoSQL systems. It is built on PostgreSQL and optimized
      for fast ingest and complex queries. Tiger Data is deployed for powering mission-critical applications,
      including industrial data analysis, complex monitoring systems, operational data warehousing, financial
      risk management, and geospatial asset tracking across industries as varied as manufacturing, space,
      utilities, oil & gas, logistics, mining, ad tech, finance, telecom, and more. Tiger Data is backed
      by NEA, Benchmark, Icon Ventures, Redpoint Ventures, Two Sigma Ventures, and Tiger Global. Documentation:
      https://docs.tigerdata.com/ GitHub: https://github.com/timescale/timescaledb Twitter: https://x.com/TimescaleDB'
    basis: linkedin
  - text: From the creators of TimescaleDB — the PostgreSQL platform trusted by enterprises processing
      trillions of metrics daily. Start a free trial or get a demo.
    basis: website
  tagline: The fastest PostgreSQL cloud for time series, real-time analytics, and vector workloads. Creators
    of TimescaleDB
  industry: Software Development
  size: 'LinkedIn size range: 51-200 employees'
  headquarters: New York, NY
  founded: '2015'
  logo_url: https://media.licdn.com/dms/image/v2/D4E0BAQEosnOv4vUk7w/company-logo_200_200/B4EZ3aqH0VJMAI-/0/1777489968705/tigerdata_logo?e=2147483647&v=beta&t=iuyfhq0vVVZW1FkcliCQHmLvjfTS6AC4PSkkcwmejKQ
  website: https://www.tigerdata.com
  github: gh:timescale
  accounts:
  - gh:timescale
  - acct:linkedin/company/tigerdata
  - acct:x/timescaledb
  locations:
  - New York, NY, US
  updates:
  - text: We can't wait to see what you cook up!
    date: '2026-10-22T16:54:53Z'
    url: https://www.linkedin.com/posts/tigerdata_we-cant-wait-to-see-what-you-cook-up-activity-7519078839881412608-55si
    likes: 6
  - text: Have fun hacking away!
    date: '2026-10-22T16:52:50Z'
    url: https://www.linkedin.com/posts/tigerdata_have-fun-hacking-away-activity-7519078326091812865-7sus
    likes: 2
  - text: 'We built three agent memory systems. The most expressive one wasn''t the most useful. First,
      a list of user-scoped facts. Four tools, text snippets, and recall returned everything you had ever
      saved. Useful for personal preferences, but a poor fit for shared project knowledge. Only a handful
      of power users used it. Second, a general knowledge graph. Nodes, edges, JSONB metadata, and arbitrary
      SQL so agents could experiment freely. They got surprisingly good at SQL. They also spent their
      turns on database mechanics instead of the memory task: integrating one thread summary took dozens
      of turns. Third, a tree. One table, an ltree path per memory, and tools for working with it. Agents
      still chose what to remember, where to put it, and how to search. But saving a summary and establishing
      its place in the hierarchy usually took one tool call. The lesson wasn''t that trees beat graphs.
      It was that flexibility can give agents more work without helping them do the job. Let agents decide
      what to remember and retrieve. Don''t make them invent edge semantics and operate the database to
      do it. https://lnkd.in/euPzk8Fn #AIAgents #PostgreSQL #RAG #OpenSource'
    date: '2026-10-22T12:26:27Z'
    url: https://www.linkedin.com/posts/tigerdata_we-built-three-memory-systems-the-most-expressive-activity-7519011288446844928-UbN2
    likes: 8
  - text: 'IIoT ingest on PostgreSQL has a failure mode that stays hidden until the day it matters. A
      remote site drops its uplink. The cause is someone else’s ticket. The backlog is yours. The sensors
      don’t care - they keep reading for six hours. Then the link comes back and all of it arrives at
      once. That’s when you find out two things you never tested. Whether those rows land once or twice.
      And what happens to every other site while that one pushes six hours of backlog through the same
      pipe. Most teams learn both answers in production. This article shows how to design the reconnect
      path so neither one surprises you, with the queries to prove it on a staging site first. https://lnkd.in/eYjhg4X2
      #IIoT #PostgreSQL #EdgeComputing'
    date: '2026-10-21T14:48:59Z'
    url: https://www.linkedin.com/posts/tigerdata_designing-iiot-ingest-that-survives-a-cut-activity-7518684769203699714-ToXJ
    likes: 10
  - text: 'Humans hate having to adjust search filters five times in a row. AI agents are great at it—if
      you give them the right knobs. Over the past year, as we built agent memory and RAG backends at
      Tiger Data, we kept writing the same retrieval machinery over and over. Today we’re open-sourcing
      it as searchgres.js . The idea came from watching how agents actually find answers when given raw
      data instead of complex preprocessing pipelines. Imagine an engineer asking an agent: “Why did Unit
      2 drop to 180 MW yesterday afternoon?” 1. The agent searches Unit 2’s logs for that 30-minute window
      using hybrid search (BM25 + semantic). 2. It spots a shift log referencing dispatch instruction
      “D-4821”. 3. On its next turn, it searches the dispatch collection for “D-4821”—relaxing the time
      filter because the instruction might have been issued hours or days earlier. A human rarely searches
      that methodically because tweaking filters across multiple queries is tedious. For an agent, iterating
      on search parameters is fast and cheap—provided two things are true: First, the search engine has
      to let you compose ranking (BM25, vector, or RRF hybrid) with strict filters on hierarchy, metadata,
      regex, and time in a single query. Second, the database has to pre-filter *inside* the index scans,
      so your top matches aren’t crowded out by records from the wrong unit or day. Postgres 18 (with
      pgvector, pg_textsearch, and ltree) gives us all of those primitives in a single database. searchgres.js
      wraps them—along with a reference MCP server and async embedding workers—into a small TypeScript
      library (npm install searchgres, Apache-2.0). More on how it works and a runnable example in today’s
      blog post: https://lnkd.in/gmbUg2E7'
    date: '2026-10-21T14:48:07Z'
    url: https://www.linkedin.com/posts/activity-7518306610709012480-sRlO
    likes: 9
  people:
  - person:erin-mikail-staples
  sources:
  - system: curation
    snapshot: curation/organizations.yaml
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1686678866005001uQkv
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: github
    url: https://api.github.com/graphql
    record_id: erinmikailstaples
    retrieved_at: '2026-10-24T19:17:20Z'
    snapshot: raw/github/owners.json
  - system: brightdata
    url: https://www.linkedin.com/in/erinmikail
    record_id: sd_mvm4dq2oc7qugqgby
    retrieved_at: '2026-10-24T08:51:28Z'
    snapshot: raw/brightdata/linkedin_profiles.json
  - system: brightdata
    url: https://www.linkedin.com/company/tigerdata
    record_id: sd_mvm5xmem1d1puu9zcg
    retrieved_at: '2026-10-24T08:56:11Z'
    snapshot: raw/brightdata/linkedin_companies.json
  - system: website
    url: https://www.tigerdata.com
    record_id: https://www.tigerdata.com
    retrieved_at: '2026-10-24T08:43:43Z'
    snapshot: raw/websites/org-homepages.json
---
# Tiger Data

Website: <https://www.tigerdata.com>

## People

- [Erin Mikail Staples](../people/erin-mikail-staples.md)
