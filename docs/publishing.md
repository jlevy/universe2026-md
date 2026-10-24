# Publish the Dataset on GitHub Pages

The intended public site is `https://jlevy.github.io/universe2026-md/`. Treat it as
pending until a successful Pages deployment and a live manifest have been verified.
See [data access](data-access.md) for the complete skill and download procedure.

## Build and Deployment Boundary

The [Pages workflow](../.github/workflows/pages.yml) checks Python lint, types and
tests, then validates and packages the committed public knowledge base and complete
agent skill. It uses the frozen pipeline lockfile and wheel dependencies; it runs no
crawls, paid APIs or data collection commands.

Pull requests run this build with repository read permission and upload the assembled
site as a workflow artifact.
They receive no Pages deployment or OIDC permission.
Only a successful build from a push to `main`, or a manual run selecting `main`, can
reach the separate deployment job.
That job has `pages: write` and `id-token: write`, uses the `github-pages` environment,
and serializes deployments.
It executes no repository code.

The uploaded directory contains only the publisher’s output: validated `kb/` files, the
complete public skill under `skills/universe2026-data/`, manifests, archives and static
navigation.
Repository files, raw snapshots, curation, credentials and caches are outside
that directory. The publisher rejects unexpected inputs and symlinks before making the
package visible.

## Enable Pages

A repository maintainer must:

1. Merge the corrected pipeline, public data, contracts and access skill before enabling
   this workflow on `main`.
2. In **Settings → Pages**, select **GitHub Actions** as the build and deployment
   source.
3. Allow the pinned official actions in the repository or organization Actions policy.
   Keep the `github-pages` environment’s deployment branch restriction on `main`; apply
   any required environment approval before the deployment job runs.
4. Run **Public Dataset Pages** on `main`, or push a reviewed change to `main`. Confirm
   the build and deployment jobs pass, then fetch `dataset.json` from the intended site
   and verify its revision matches the deployed commit.

The workflow reads existing Pages configuration with `enablement: false`; it does not
enable Pages or change repository settings.
A personal access token is unnecessary.
For GitHub’s setup and permission requirements, see
[custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Public Files and Archives

Paths below are relative to the public site root:

| Path | Access |
| --- | --- |
| `index.html` | Browse the entity index and download links |
| `kb/README.md` | Read the KB guide and follow direct links to Markdown and YAML records |
| `dataset.json` | Read the deployed revision, entity counts, and archive paths, sizes and SHA-256 checksums |
| `files.json` | Find individual record and export paths |
| `skills/universe2026-data/SKILL.md` | Read the skill; download its complete bundle using the manifest’s `skill` archive |

Download every KB file through the archive named by `dataset.json`’s `archive` entry.
Resolve archive paths against the site root and verify the compressed size and SHA-256
before extraction. The archive preserves the `kb/` directory and its relative schema
references.

The publisher copies KB bytes unchanged and adds `.nojekyll`. The upload includes this
marker, and Pages serves the static files without a Jekyll build, preserving
`_schemas/`, `_graph/`, `_search/` and Markdown frontmatter.

Each deployment contains its current revision’s versioned archives and release manifest.
An archive’s revision in its filename identifies its content; it does not guarantee the
archive remains hosted after the next deployment.
Save the manifest and archive with results that need long-term reproducibility, or
arrange separate archive retention.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
