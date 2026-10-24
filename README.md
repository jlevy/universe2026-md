# GitHub Universe Dataset

This repository holds the public record of GitHub Universe, GitHub’s developer
conference, as plain Markdown and YAML files, along with the code that crawls the
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

## Format

Each record is a [softschema](https://github.com/jlevy/softschema) artifact: Markdown
with YAML frontmatter, or plain YAML. Each one declares the contract it follows, such as
`paraverse.conference:Person/v1`, and points to the JSON Schema for that contract, so a
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
uv sync
uv run universe-kb build
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
