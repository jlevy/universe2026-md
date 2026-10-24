# universe2026-md Docs

Start with the data policy; it sets what this public repository may contain.

- [Data policy](data-policy.md): what may and may not be committed, how generated text
  is handled, and how removal requests work.

## Architecture

- [Conference knowledge base](project/architecture/arch-2026-10-24-conference-kb.md):
  the crawl, enrichment and build pipeline in `pipeline/`, the softschema records in
  `kb/`, the people model, and how the build enforces the data policy.

## Research

- [GitHub Universe knowledge graph](project/research/research-2026-10-23-universe-knowledge-graph.md):
  where GitHub Universe’s data lives, what each source exposes, the data and people
  models, and worked examples.
- [Enrichment sources survey](project/research/research-2026-10-24-enrichment-sources-survey.md):
  further public sources for people’s interests and past work, with access, terms,
  coverage and what not to use.
- [KB data-quality review](project/research/review-2026-10-24-universe-kb-data-quality.md):
  defects that pass structural validation, by area and severity, and the checks that
  find them.
- [Simulated conference avatars](project/research/research-2026-10-24-simulated-conference-avatars.md):
  what the KB can support about people, from cited persona cards to simulated agents,
  and the consent rules that come first.

## Plans

Active:

- [Deeper enrichment sources](project/specs/active/plan-2026-10-24-deeper-enrichment-sources.md):
  unmapped, free and paid sources for interests, past work and conference history.
- [KB hardening](project/specs/active/plan-2026-10-24-kb-hardening.md): CI, data fixes
  and readiness for a second conference.

Done:

- [Universe knowledge base](project/specs/done/plan-2026-10-24-universe-knowledge-base.md):
  the run that built the KB, with its decisions and technical debt.

## Related

[Paraverse](https://github.com/jlevy/paraverse) mounts this repository as a git
submodule and loads `kb/` into a FalkorDB graph with a read-only browser; its
[docs index](https://github.com/jlevy/paraverse/blob/main/docs/README.md) covers the
graph database.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
