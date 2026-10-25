# GitHub Universe 2026 Dataset

This repository holds the public record of GitHub Universe 2026, GitHub’s developer
conference, with earlier editions from 2023–2025 for context.
The data is stored as plain Markdown and YAML files alongside the code that crawls the
sources and builds the files.
It is for anyone who wants the raw data on the conference: who spoke, on what, when and
where, and the people, organizations and open-source work around it.

## What It Contains

- **Editions:** GitHub Universe 2023 through 2026.
- **The program:** sessions, speakers, rooms, venues, organizations and sponsors.
- **People:** speakers, and people who said publicly that they would attend, with their
  public professional profiles.
- **Open-source work:** repositories and packages.

Every record cites the sources it was built from.

## Dataset Summary

The checked-in snapshot covers **four editions (2023–2026)** with **5,407 graph
entities**, **25,313 relationships** and **4,977 validated Markdown/YAML artifacts**. Of
the 520 sessions, 156 are in the Universe 2026 program and 364 are from earlier
editions.

| Entity type | Count |
| --- | ---: |
| Days | 14 |
| Event editions | 4 |
| Experiences | 11 |
| Taxonomy facets | 34 |
| GitHub accounts | 237 |
| Organizations | 310 |
| Packages | 134 |
| Conference pages | 9 |
| People | 577 |
| Professional profiles | 577 |
| Repositories | 1,155 |
| Rooms | 85 |
| Sessions | 520 |
| Social accounts | 1,052 |
| Software | 61 |
| Taxonomy terms | 418 |
| Venues | 58 |
| Websites | 151 |

The dataset also contains **14 FAQ entries** and a **1,899-item media index**. Days and
taxonomy terms are graph nodes within event and facet records; FAQ entries and media
items are grouped in their own collection artifacts.
Counts describe this repository snapshot, not verified attendance or live account
totals. See [graph statistics](kb/_graph/stats.json) for the generated counts.

## Agent Access and Downloads

The [Universe 2026 data skill](.agents/skills/universe2026-data/SKILL.md) downloads the
complete published knowledge base as one checksum-verified archive and explains how to
query records, relationships and search files locally.
Copy the complete skill directory, including its bundled download script.
No GitHub account, repository clone or paid collection request is needed to consume a
published package.

The [access guide](docs/data-access.md) describes the package and revision pins.
The [static site](https://jlevy.github.io/universe2026-md/) provides browsable files and
complete download archives.
The [publication guide](docs/publishing.md) describes deployment and verification.

## Sources and Collection

The dataset is built from crawled public sources and saved enrichment responses:

- **Conference crawl:** `universe-kb crawl` fetches GitHub Universe’s official website
  and RainFocus agenda portal; `crawl-editions` fetches the 2023–2025 catalogs.
  These sources establish the program, speakers, organizations and places.
- **Public professional sources:** `enrich`, `enrich-social` and `enrich-packages`
  collect GitHub profiles and repositories, professional websites, public social
  profiles and feeds, and package-registry metadata.
- **Bright Data enrichment:** `enrich-brightdata` uses
  [Bright Data](https://brightdata.com/)’s paid dataset API to collect public LinkedIn
  profiles, X profiles and their owners’ posts, and LinkedIn company pages for accounts
  already identified in the knowledge base.
  Collection needs `BRIGHT_DATA_API_KEY`; ordinary rebuilding does not need that key or
  a paid request.

Fetches save source snapshots under `pipeline/raw/`, including `raw/brightdata/`, with
source URLs and retrieval metadata in `raw/manifest.json`. Collection filters the
responses according to the [data policy](docs/data-policy.md), removing contact details,
other people’s data and scraper bookkeeping before saving.
The build combines those saved inputs with reviewed curation and generated bios to
produce `kb/` offline.
A public source or Bright Data result does not establish attendance by itself: an
attendance claim needs the person’s own public statement.

The [pipeline guide](pipeline/README.md) documents collection commands, credentials,
privacy filtering and rebuilding.
The
[source research](docs/project/research/research-2026-10-23-universe-knowledge-graph.md)
explains what the sources expose and how they are connected.

## Format

Each record is a [softschema](https://github.com/jlevy/softschema) artifact: Markdown
with YAML frontmatter, or plain YAML. Each one declares the contract it follows, such as
`paraverse.conference:Person/v2`, and points to the JSON Schema for that contract, so a
record validates wherever it is copied.

Alongside the records, `kb/` has three derived directories:

- `kb/_schemas/`: the JSON Schemas for every contract.
- `kb/_graph/`: the whole knowledge base as a graph, with nodes and edges in JSONL
  files, one JSON object per line, for graph tools, DuckDB or `jq`.
- `kb/_search/`: documents for full-text search.

## Layout

| Path | Contents |
| --- | --- |
| `README.md`, `AGENTS.md`, `LICENSE` | This page, instructions for coding agents, and the license |
| `kb/` | The built knowledge base: softschema Markdown and YAML records, `_schemas/`, `_graph/` and `_search/` |
| `pipeline/` | The crawl, enrichment and build code, a uv project named `universe-kb`: `src/universe_kb/`, `tests/`, `schemas/`, `raw/`, `curation/` and `synthesis/` |
| `docs/` | The data policy, and research, architecture docs and plans under `docs/project/` |

## Rebuilding

The build regenerates `kb/` from the saved sources in `pipeline/raw/`:

```bash
cd pipeline
make install
make build
```

[pipeline/README.md](pipeline/README.md) covers crawling, enrichment and the other
commands.

## Browsing

[Paraverse](https://github.com/jlevy/paraverse) loads this knowledge base into a graph
database and serves a browser for it.
It includes this repository as a git submodule at `vendor/universe2026-md`.

## Data Policy

Everything in this repository is public.
The [data policy](docs/data-policy.md) sets what may be included and what never is, such
as contact details, non-public sources and sensitive personal attributes.
Read it before you add or change data.

To have your data removed, open an issue, or contact a maintainer privately.

## Contributing

Agents and humans follow [AGENTS.md](AGENTS.md).
Work is tracked with [tbd](https://github.com/jlevy/tbd), and records are validated with
[softschema](https://github.com/jlevy/softschema).

## License

[MIT](LICENSE)

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
