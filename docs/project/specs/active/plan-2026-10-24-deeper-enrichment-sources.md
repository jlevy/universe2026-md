# Feature: Deeper Enrichment Sources for the Universe Knowledge Base

**Date:** 2026-10-24 (last updated 2026-10-24)

**Author:** Claude Code, for Joshua Levy

**Status:** Draft; the paid phase needs approval

> In this repository the records are in `kb/`, and the pipeline (`src/universe_kb/`,
> `raw/`, `curation/`, `synthesis/`, `schemas/` and `tests/`) is in `pipeline/`. Counts
> are as of the 2026-10-24 build; where this document and the data policy differ, the
> policy and the architecture doc describe the current design.

## Overview

The GitHub Universe knowledge base (`kb/`) knows who everyone is, where they work and
what they spoke about.
It knows much less about what they care about, what else they have made, and what they
are looking for.

This plan lists every additional source that could close that gap, in three layers:
1. Data already collected but not yet used.
2. Free public sources.
3. The paid Bright Data datasets that are worth their cost.

It also lists the sources not to use, and why.
For each source it says how a record is tied to a person safely, and it sets out the
model changes and phases to bring the data in.

Two research docs written for this plan hold the details:
- [Enrichment sources survey](../../research/research-2026-10-24-enrichment-sources-survey.md):
  about 60 non-Bright Data sources, each checked against its official documentation,
  with coverage probes against the kb’s own accounts.
- [Simulated conference avatars](../../research/research-2026-10-24-simulated-conference-avatars.md):
  what richer profiles would make possible, up to simulated avatars and a simulated
  conference, and the consent rules that have to come first.

## Goals

- Give each person an evidence-backed picture of their **interests**, each with a basis,
  weight and citation, from:
  - what they star and contribute to on GitHub
  - what they write and tag
  - the session topics they speak in
  - their communities
- Record **past work** beyond Universe:
  - talks at other events, with recordings and slides
  - writing and podcast appearances
  - publications, patents and books
  - packages
  - recognition programs
- Recover the **conference’s own history**:
  - editions 2015–2022 from archived githubuniverse.com pages
  - session recordings for 2023–2025 from GitHub’s YouTube playlists
- **Spend nothing new until free and already-collected data is used.** Paid runs wait
  for approval.
- Feed richer, cited persona cards to the briefing and simulation experiments in the
  avatar research brief.
- Let us add **people beyond the event listing**: anyone with a public, professional
  connection to the conference, whether or not they attend, kept in one easy-to-edit
  list, with a short, repeatable process to add more and a way for anyone to be removed.

## Non-Goals

- **Contact details and private data:**
  - email addresses, phone numbers and home addresses
  - people-search data
  - friend and follower graphs
  - private channels
  - anything a person has not published
- **Sources whose terms forbid this use.** The survey’s do-not-use list covers them.
- **Added sensitive attributes**, which the kb never adds, derives or infers from any
  source; only text a person wrote about themselves and published, kept verbatim, may
  state one:
  - job seeking
  - health, religion, politics, sexuality
  - immigration or travel status, personal safety
  - motives
- **First-person avatars of named people.** The avatar brief covers them, and they need
  the person’s opt-in.

## Background

Field coverage today, from `kb/_graph/coverage.json` as of 2026-10-24, 590 people:

| Field | Coverage | Field | Coverage |
| --- | --- | --- | --- |
| `profile.brief_bio` | 100% | `profile.recent_writing` | 29% |
| `profile.expertise` | 94% | `profile.open_source` | 25% |
| `profile.headline` | 75% | `profile.recognitions` | 4% |
| `profile.education` | 49% | `profile.packages` | 3% |
| `profile.credentials` | 46% | `profile.interests` | 1% |
| `person.github` | 32% | `profile.experience` | 1% |
| `person.websites` | 32% | Session `image_url` | 50% |

Other gaps:
- **Uneven coverage:** 167 of 183 2026 speakers have a GitHub account, against 16 of 395
  past-only speakers.
- **Little first-person text:** the avatar brief counted a median of zero words written
  by the person themselves for 2026 speakers.
  Event bios and abstracts are mostly promotional copy written about them.
- **No stated goals:** no one has stated goals, and that only comes from the person
  (Phase 4).

## Design

### Linking Rule

A record from a new source attaches to a person only in one of three ways:
1. It came from an account or URL the person already lists.
2. Its profile links back to an account the kb already holds.
   The usual case: look the person’s GitHub login up on the other service, and accept
   the account only if that profile names the same GitHub account.
3. A curator confirms it in `curation/people.yaml`.

A matching name or username alone never links.
Each new link basis gets a value in `LinkBasis`. The probes found back-linked accounts
on DEV (36 of 187 GitHub users), Keybase (27), crates.io (10) and Notist (6).

The rule covers records that enrich a person.
Speaker listings from earlier editions, including archived githubuniverse.com pages, are
the conference’s own catalogs: their speakers merge with people through the identity
resolution in the
[architecture doc](../../architecture/arch-2026-10-24-conference-kb.md), as the
2023–2025 speakers did, and the risk it records for merging by name across editions
applies to them (Open Questions).

### Model Changes

All changes are additive, so the contracts can stay at `v1` (the version bump is listed
under the KB plan’s technical debt):

- **`Profile.interests`** becomes weighted claims.
  Each claim gets a `basis` (`github_stars`, `github_topics`, `post_hashtags`,
  `writing_tags`, `session_facets`, `stack_tags`, `community`, `self_reported`), a
  `weight` and citations.
  Self-reported interests outrank inferred ones.
- **`Profile.publications`**: title, venue, date, url, description, and a basis of
  `linkedin`, `openalex` or `orcid`.
- **`Profile.patents`**: title, number, date and url.
- **`Profile.speaking`**: talks outside Universe, each with event, date, title, url, and
  a source of `sessionize`, `notist`, `speakerdeck`, `lanyrd_archive`, `github_stars` or
  `youtube`.
- **`Profile.media`**: video and podcast appearances.
- **`Profile.recognitions`** gains flags from GitHub GraphQL: `isGitHubStar`,
  `isCampusExpert` and `isEmployee`. Rosters such as CNCF Ambassadors and Java Champions
  also add recognitions.
- **`Session.recording`**: url, duration, published date and chapters.
  Transcript handling waits on a decision (Open Questions).
- **`Organization`** gains:
  - `affiliated` (parent and subsidiary companies)
  - recent company `updates`
  - optional `funding` and `investors`
- **New `Event` artifacts** for editions 2015–2022. Their speakers become people with
  participations, as the 2023–2025 speakers did.

### Bright Data: The Full List

`GET /datasets/list` returns **1,881 datasets**. About 240 relate to people, companies,
content or developer platforms.
The rest are product, travel, retail and local-business catalogs that have nothing to
offer here.

The families below cover all 240. Many entries are pre-filtered subsets or bulk dumps of
the same scraper, and the targeted scrapers are the ones to use.
Field lists come from `GET /datasets/{id}/metadata`, fetched 2026-10-24. Pricing is per
record, pay-as-you-go
([Scraper API FAQs](https://docs.brightdata.com/products/scrapers/scrapers-library/faqs)).

#### A. Already Collected, Not Yet Used (Free)

| Data | Where it sits in `raw/brightdata/` | Amount |
| --- | --- | --- |
| LinkedIn publications | `linkedin_profiles.json` `publications` | 371 entries, 99 people |
| LinkedIn patents | `linkedin_profiles.json` `patents` | 189 entries, 35 people |
| LinkedIn education details | `educations_details` | 358 profiles |
| Company recent posts | `linkedin_companies.json` `updates` | 189 companies |
| Affiliated companies | `linkedin_companies.json` `affiliated` | 118 companies (`related_organizations` is at 1%) |
| Company locations | `formatted_locations` | 177 companies |
| X posts: text and hashtags | `x_profiles.json` `posts` | 5,950 posts, newest 2025-11-15 |
| X account category | `category_name`, `is_business_account` | 35 and 50 accounts |
| Credly badge links | LinkedIn certification URLs | 273 |

#### B. Recommended Paid Datasets

Each run starts with a test of three inputs to check fields and cost.

| Priority | Dataset (ID) | Inputs | Gives us | Records |
| --- | --- | --- | --- | --- |
| 1 | YouTube videos (`gd_lk56epmy2i5g7lzu0k`), discover by URL | GitHub channel’s Universe 2023–2026 playlists; people’s talk links | Title, description, chapters, length, views, tags, **transcript** | ~600 |
| 2 | LinkedIn posts (`gd_lyy3tktm25m4avu764`), discover by profile URL | 178 LinkedIn accounts of 2026 participants, 10 posts each | Full post text, hashtags, tagged companies, document posts | ~1,780 |
| 3 | X posts (`gd_lwxkxvnf1cynvib9co`), discover by profile URL, 2026 window | 113 X accounts of 2026 participants, 20 posts each | Current posts and hashtags; a person’s own post saying they will attend can count as attendance evidence again | ~2,260 |
| 4 | YouTube channels (`gd_lk538t2k2p1k3oos71`) | 16 people’s channels | About text, subscribers, top videos, podcast flag | 16 |
| 5 | G2 product overview (`gd_l88xp4k01qnhvyqlvw`) | The 61 software entities | Categories, competitors, features, pros and cons | ~60 |
| 6 | Threads profiles (`gd_mde7jg3ld2h3hnnf2`) | 5 linked accounts | Bio, website, followers | 5 |
| Optional | LinkedIn jobs (`gd_lpfll7v5hcqtkxl6l`), discover by company | 54 sponsors, 20 jobs each | “Hiring at Universe” for sponsor pages | ~1,080 |
| Optional | Crunchbase companies (`gd_l1vijqt9jfj7olije`) | Organizations found by name (no LinkedIn company record carries a Crunchbase URL) | Funding, investors, founders, acquisitions | ~150 |
| Optional | Glassdoor overview (`gd_l7j0bx501ockwldaqf`) or Owler (`gd_l1vilaxi10wutoage7`) | Organizations | Size, revenue range, ratings | ~200 |

Posts collected from LinkedIn and X are the person’s own public posts, which the
[data policy](../../../data-policy.md) allows; other people’s posts and reactions in the
records are stripped before saving.
The policy takes organization facts from an organization’s own pages, so G2, Crunchbase,
Glassdoor and Owler, which describe organizations and products from outside, need a
policy decision before any run.

Two clarifications:
- **YouTube transcripts:** the free YouTube Data API cannot provide them.
  Captions need OAuth and edit rights on the video, so priority 1 is the only route to
  transcripts, and storing them raises a terms question (Open Questions).
- **Crunchbase:** collected by name, so it is lower-precision and has a licensing caveat
  (Open Questions).

#### C. Examined and Not Recommended

| Family | Datasets (examples) | Why not |
| --- | --- | --- |
| People-search | Truepeoplesearch (`gd_ln1sml5e13vypm0wb7`) | Home addresses and relatives; never |
| Contact enrichment | LinkedIn profiles, contact fields enriched (`gd_me5ppxjr2ge6icjuh0`); B2B Contacts and Companies (`gd_m2a6waqv18439a8thq`); Instagram business emails (`gd_la0rn1c71tmkulbspw`) | Contact harvesting; never |
| Social graphs | Facebook Friends (`gd_lo2vq1dl1t5uv6ebqx`) | Other people’s data; never |
| Company contacts | ZoomInfo companies (`gd_m0ci4a4ivx3j5l6nx`) | `top_contacts`, `org_chart` and `email_formats` are contact data; company fields are available elsewhere |
| Personal social | Instagram, TikTok and Facebook profiles, posts and reels | Mostly personal life, with low professional value; few people link them (Instagram 11) |
| Bulk and filtered LinkedIn | “Users Last Week”, profiles by country, company or title, Italian profiles, and other subsets | Not targeted; the plain profile scraper covers our inputs |
| Free equivalents | Bluesky posts (`gd_m6hn4r5s27zfhc7w4`), Wikipedia articles (`gd_lr9978962kkjr3nx49`), GitHub repository (`gd_lyrexgxc24b3d4imjt`), arXiv, Goodreads | The public AppView, Wikipedia API, GitHub GraphQL, arXiv API and Open Library give the same for free |
| Weak linking | Reddit posts and comments, Quora posts, Vimeo videos, Stack Overflow users | Few people list these accounts, and usernames alone may not link; use only for accounts people list (Stack Exchange is free) |
| Needs separate setup | Google SERP, Google News, Bing SERP | The SERP API and Web Unlocker need their own setup (Open Questions) |
| Not relevant | Job boards beyond sponsors, news sites, app stores, reviews (Trustpilot, Yelp), e-commerce | Nothing about these people or this conference |
| Dataset metadata not found | Crunchbase people, Pitchbook people, Stack Overflow users, arXiv | `metadata` returned 404; possibly retired. A three-input test would confirm |

### Free and Other Sources

The survey ranks these by value for interests, past work and recordings, then by link
precision, coverage and cost:

| Rank | Source | Gives us | Links by |
| --- | --- | --- | --- |
| 1 | GitHub GraphQL, unused fields | Star lists and starred topics, Sponsors, discussions, contribution history across years, and Star, Campus Expert and employee flags | The accounts we hold |
| 2 | YouTube Data API | Universe 2023–2026 playlists on GitHub’s channel, matched to sessions by title; no transcripts; refresh within 30 days | Session title |
| 3 | Wayback CDX for githubuniverse.com | Editions 2015–2022: static speaker pages 2015–2019, about 100 session pages in 2020, Swoogo pages in 2021, an archived JS bundle in 2022 | The archived pages themselves |
| 4 | Sessionize public profiles | Dated past talks and events, with topics | Back-link to GitHub |
| 5 | GitHub blog and changelog | Posts by the roughly 210 GitHub-affiliated people | Co-author GitHub logins |
| 6 | DEV API; Medium, Substack and blog RSS | Writing history and self-chosen tags (Hashnode’s API went paid 2026-05-13, so use its RSS) | DEV `github_username`; feeds people list |
| 7 | Bluesky author feeds and starter packs | Current interests (47 of 78 active) and communities (12 made starter packs) | The accounts we hold |
| 8 | Wayback for Lanyrd profiles | Speaking history 2010–2018 | The X handles we hold |
| 9 | GitHub Stars profiles | Dated talks, videos, podcasts and posts | Star profile’s GitHub link |
| 10 | Podcast Index and show RSS | Podcast appearances; Podcast Index for discovery only, its terms forbid stored copies | Person search, confirmed by the show’s own RSS |
| 11 | CNCF `people.json`; Java Champions YAML | Recognitions and employer history | GitHub login |
| 12 | npm maintainers, crates.io, ecosyste.ms | All published packages, not just top repositories | GitHub login |
| 13 | Notist and Speaker Deck | Slides with event names | Notist `github` field; links people list |
| 14 | Wikidata | Identifier crosswalk, employers, awards | GitHub, X or ORCID identifiers |
| 15 | OpenAlex with ORCID | Publications for researchers | ORCID iDs, never names |

Runners-up:
- Keybase proofs: a crosswalk for 27 people.
- GH Archive.
- Hugging Face Hub.
- Stack Exchange top tags.
- `cncf/gitdm` employer history.
- Google Patents on BigQuery (the PatentsView API has been paused since 2026-03-20).
- Sponsors’ own pages for side events.

The survey has the full table, the coverage probes and the documentation links.

**Do not use:**
- **People-search and background-check sites.**
- **Contact harvesters:** Hunter, RocketReach, Apollo, ZoomInfo contacts, Lusha and
  similar.
- **Emails found inside useful data:** commit emails, ecosyste.ms maintainer emails,
  Keybase key IDs. Never look up Gravatar by email hash.
- **Sources whose terms forbid this use:**
  - Spotify: no databases, no AI use.
  - Linktree and about.me: no scraping.
  - Discord and Slack: no profiling, no copies.
  - Reddit: only with approval.
  - Listen Notes: IDs only.
- **Sources with no API that sit behind bot walls:** Google Scholar, ResearchGate.
- **YouTube downloads and unofficial caption endpoints.**

### Terms That Clash With a Git Snapshot

The kb stores raw snapshots in Git, and some terms do not allow that:
- **YouTube API data:** must be refreshed or deleted within 30 days.
- **Podcast Index:** forbids permanent copies.
- **Bright Data scrapes of YouTube and Crunchbase:** the platforms’ own terms restrict
  stored copies, even though the data is public.

These sources keep raw responses in a Git-ignored cache.
The kb stores only what the build derives: metadata, topics and short cited summaries.
Verbatim transcripts stay out of Git unless the transcript decision says otherwise.
A rebuild from a fresh clone cannot re-derive those fields without the cache, while the
architecture doc requires the KB to rebuild offline from committed inputs; how the build
reconciles the two is open (Open Questions).

### Adding People Beyond the Event

Today a person enters the kb in one of three ways:
- from an event listing (speakers)
- from public posts saying they will attend
- from `curation/people.yaml`

Every curated entry must name a role at the event, and `Person.participations` requires
at least one.
There is no place for someone with a public, professional connection to the
conference who is not known to attend, for example:
- maintainers of projects the program features
- authors of work a session builds on
- people who publicly work with a speaker, such as co-authors and co-maintainers
- organizers’ and sponsors’ staff, as their own organization’s public pages list them
- community leaders

Removal already has a path: anyone may ask, as the data policy’s
[Removal Requests](../../../data-policy.md#removal-requests) section says, and a
maintainer then adds the person to the person-exclusion field in `curation/people.yaml`,
as the architecture doc’s
[Adding or Removing a Person](../../architecture/arch-2026-10-24-conference-kb.md#adding-or-removing-a-person)
section says. Neither gives that field’s format, and the new list below is one more
source it must override, so **Removal** below specifies both.

Everything below follows the repository’s [data policy](../../../data-policy.md): only
public, professional information, no attendance a person has not stated publicly, and a
removal path that works.

**The list.** `curation/additional-people.csv` holds one row per person, so it opens in
any spreadsheet and is easy to paste into.
The file is committed to a public repository, so every cell must be public and
professional.

| Column | Required | Meaning |
| --- | --- | --- |
| `name` | yes | As the person writes it |
| `reason` | yes | Why they belong in the kb, in one line, stated as a public professional fact that `source_url` supports; no private context, opinion or sensitive attribute |
| `relation` | yes | One of `maintainer`, `author`, `colleague`, `organizer_staff`, `sponsor_staff`, `community` |
| `target` | no | What the relation is to: a kb ID (`software:…`, `org:…`, `session:…`, `repo:…`, `person:…`) or a URL |
| `source_url` | yes | A public page that shows the association, such as a repository’s maintainer list, a paper, or an organization’s team page |
| `github`, `linkedin`, `x`, `bluesky`, `mastodon`, `website` | at least one | The person’s own professional GitHub, LinkedIn, X, Bluesky and Mastodon accounts and their own professional site, used for identity matching and enrichment |
| `organization`, `title` | no | Their current role, if public |
| `attendance_source` | no | A public post in which the person says they are attending; nothing else counts |
| `added_by`, `added_on` | yes | The GitHub handle of whoever added the row, and the date |

No column holds contact details, and `people-check` rejects a row with an email address
or phone number in any cell.

**The model.** A person can have `associations` instead of, or as well as,
participations. An association has a relation, a target, the reason, its source and who
added it. A person needs at least one of the two.
Attendance stays a participation: only a row with an `attendance_source` becomes a 2026
attendee participation, through the same rule as other public attendance posts.
Everyone else is associated but not attending.
The kb records, search documents, graph and bios never label them as attendees, and in
the graph an association is its own edge type, never a participation.
Their bios say how they relate to the conference, cite `source_url`, and never say or
suggest that they attend.
As for everyone, the pipeline never adds or infers a sensitive attribute: only bio text
the person wrote and published themselves, such as a profile bio, states one, and it is
kept verbatim. Every added person gets `inclusion_basis: curated`.

**Removal.** The person-exclusion field is an `excluded` list in `curation/people.yaml`,
keyed by person ID or by account.
The build drops an excluded person, their accounts, websites and profile from every
source, including the event listing and `curation/additional-people.csv`, and the bio
pipeline prunes their bio.
The person must then be absent from the kb records, search documents, graph exports, raw
snapshots committed in Git and test fixtures, and a test checks this.
An exclusion records only the ID and the date, never a reason.
Requests arrive as the data policy describes: an issue, or privately through a
maintainer. A removal is committed promptly, and rewriting earlier history is decided
case by case.

**The process.** To add someone:
1. **Add a row,** either by editing the CSV or with `universe-kb add-person --name …
   --reason … --relation … --source-url … --github …`, which validates and appends.
   `universe-kb add-people FILE.csv` merges a whole list.
2. **Check the list:** `universe-kb people-check`.
   - It fails a row that is missing its name, reason, relation, source or an account.
   - It fails a row with contact details in any cell.
   - It reports rows that already match a kb person, by account or by name with an
     account in common.
   - It reports rows that match an exclusion.
3. **Enrich:** `universe-kb enrich` and `universe-kb enrich-social`. They are free and
   pick up new accounts from the kb on their own.
   LinkedIn and X details for the new rows come from the paid run, `universe-kb
   enrich-paid --datasets linkedin_profiles,x_profiles`, which needs approval.
   That command is incremental, so only new URLs are fetched.
   The mapping keeps only the profile owner’s own data and strips other people’s data,
   such as “people also viewed” lists and other people’s posts.
4. **Bios and checks:**
   - Run `universe-kb build`.
   - Write bios: `bio-bundles`, a writer, then `bios-merge`.
   - Run `universe-kb validate` and `pytest`.
   - Commit, with the data policy’s review checklist in the pull request.

**Identity.** The usual rules apply: accounts first; a name only with an account in
common. A row that matches an existing person adds its association to that person and
does not create a duplicate.

## Implementation Plan

### Phase 1: Use What We Already Have (Free, No New Fetching)

- [x] Map LinkedIn publications and patents into the profile (371 and 189). The
  education details turned out to be a school-name string that duplicates `education`.
- [x] Map company updates, affiliated companies and locations into organizations, and
  fill `related_organizations`
- [x] Build the weighted interest model from what we already hold:
  - session facets
  - X post hashtags
  - LinkedIn and blog writing
  - GitHub topics of owned and contributed repositories
- [x] Add the GitHub GraphQL fields we don’t yet use:
  - star lists and starred-repository topics
  - Sponsors
  - contribution years
  - the `isGitHubStar`, `isCampusExpert` and `isEmployee` flags
- [x] Redact emails and phone numbers from free text in every committed folder, and test
  that none remain
- [x] Regenerate stale bios (127 rewritten, `synthesis/bios/round-8`)

### People Intake (Independent of the Other Phases)

- [ ] `Association` model and `Person.associations`; a person needs a participation or
  an association
- [ ] `curation/additional-people.csv` with the columns above, plus a header comment row
  explaining them
- [ ] `universe-kb add-person`, `add-people` and `people-check`
- [ ] The build reads the CSV:
  - it merges matching rows into existing people
  - it creates the rest
  - only rows with an `attendance_source` become attendee participations
- [ ] An `excluded` list honored across every source and output, with bio pruning, once
  its format is settled (see Open Questions)
- [ ] README section “Adding and removing people”, written as the four-step process and
  the removal steps above
- [ ] Tests:
  - validation errors, including a missing `source_url` and contact details in a cell
  - merging into an existing person
  - an associated person never appearing as an attendee in records, search documents,
    graph or bios
  - an excluded person being absent everywhere

### Phase 2: Free Public Sources

- [ ] Session recordings: YouTube Data API playlist metadata into `Session.recording`
  (needs a Google API key and the offline-rebuild decision in Open Questions)
- [ ] Editions 2015–2022 from the Wayback CDX API, as `Event`, session and person
  artifacts with participations
- [ ] Speaking history, every link through the linking rule:
  - Sessionize
  - Notist and Speaker Deck
  - GitHub Stars profiles
  - Lanyrd archive pages
- [ ] Writing history:
  - DEV API, by back-link
  - the GitHub blog, by co-author login
  - Medium, Substack and blog feeds that people list
- [ ] Current interests and communities: Bluesky author feeds and starter packs, and
  Mastodon featured tags
- [ ] Recognitions:
  - CNCF and Java Champions rosters
  - GitHub flags from Phase 1
  - MVP and similar profiles only to verify claims people make
- [ ] Packages by GitHub login: npm maintainers, crates.io, ecosyste.ms
- [ ] Publications through ORCID and OpenAlex; Wikidata crosswalk
- [ ] Podcast appearances: discover with Podcast Index; store from show RSS
- [ ] Regenerate stale bios

### Phase 3: Paid Bright Data Runs (Needs Approval)

- [ ] Run a three-input test of each dataset in table B that may run; G2, Crunchbase,
  Glassdoor and Owler wait on the data-policy decision about outside organization facts
  (Open Questions)
- [ ] Run priorities 1 to 4 and 6
- [ ] Priority 5 (G2) only if that policy decision allows it
- [ ] Optional rows only if approved separately, and Crunchbase, Glassdoor and Owler
  only if the same policy decision allows them
- [ ] Map transcripts according to the transcript decision; map posts into writing and
  interests; map a current X post into attendance evidence only when its author says in
  it that they will attend, as the data policy requires; other posts and hashtags feed
  writing and interests only
- [ ] Regenerate stale bios

### Phase 4: Ask People Directly (Not Yet Designed)

- [ ] A claim-your-profile flow, in which people see and correct every claim, opt in or
  out, and state goals (asks, offers, “looking for”). The avatar brief explains why this
  is the only good source of goals.

## Testing Strategy

- **Parsers:** each new source gets a parser test against a small saved snapshot, as the
  existing sources do.
- **Linking:** tests show that a matching name or username alone never links, and that
  back-links do.
- **Privacy:** a new kb-wide test scans for emails, phone numbers, street addresses and
  the banned inference categories.
- **Acceptance:** coverage gains in `coverage.json`. Targets:
  - `profile.interests` above 60%
  - `profile.speaking` above 40% of speakers
  - `Session.recording` above 80% for 2023–2025
  - every 2015–2022 edition present
- **Checks:** `universe-kb validate` (0 invalid), `pytest`, `ruff` and `basedpyright` on
  every change.

## Rollout Plan

Each phase is committed as it lands, and pull requests that change data carry the data
policy’s review checklist.
Paid runs wait for approval.

## Open Questions

- **Paid runs:** approve Phase 3 priorities 1 to 4 and 6, and say which optional rows to
  run?

- **Outside organization facts:** G2, Crunchbase, Glassdoor and Owler describe
  organizations and products from outside, and the data policy takes organization facts
  from an organization’s own pages.
  Change the policy to allow them, or leave them out?
  Priority 5 and those optional rows wait on this decision.

- **Transcripts:** how should YouTube transcripts from Bright Data be kept?
  - (a) not collected
  - (b) a Git-ignored cache plus derived topics, chapters and short cited summaries in
    the kb (recommended)
  - (c) verbatim in the kb

  The platform’s terms and speakers’ expectations argue against (c).

- **Search APIs:** should a Bright Data SERP API or Web Unlocker zone be set up?
  It would find talks and articles by search, but search results link people by name and
  need careful confirmation.

- **Crunchbase:** use Crunchbase data, given its licence terms and the data policy’s
  rule that organization facts come from the organization’s own pages?
  The free company sources may be enough.

- **Pre-2023 editions:** should 2015–2022 speakers become people?
  That would add several hundred past-only speakers, each needing a bio.
  Where an archived page lists no account, its speaker would merge with an existing
  person by a unique name alone; should such a match need a curator’s confirmation
  instead?

- **YouTube API key:** a Google Cloud project with the YouTube Data API enabled is
  needed for Phase 2’s recordings.

- **Time-limited sources and the offline rebuild:** YouTube API data must be refreshed
  or deleted within 30 days, but `Session.recording` would come from it and the KB must
  rebuild from committed inputs.
  The survey’s options: refresh those fields on every build, or keep only video URLs
  that GitHub also publishes elsewhere.
  Phase 2’s recordings wait on this decision.

- **Avatars:** the consent decisions in the avatar brief come before any feature that
  uses the richer profiles.

- **Added people:**
  - Should their LinkedIn and X details be collected by default with the paid run, or
    only on request?
  - Is the relation list above the right one?
  - Who may add rows: any contributor through a reviewed pull request, or maintainers
    only?
  - What format should the public `excluded` list use, so that it does not republish the
    names it removes? A plain hash of each ID or account is not enough: IDs and handles
    are predictable, so anyone can hash candidate names and match them.
    Settle this before the list is built.

## References

- [Enrichment sources survey](../../research/research-2026-10-24-enrichment-sources-survey.md)
- [Simulated conference avatars](../../research/research-2026-10-24-simulated-conference-avatars.md)
- [Universe knowledge graph research](../../research/research-2026-10-23-universe-knowledge-graph.md)
- [Universe knowledge base plan](../done/plan-2026-10-24-universe-knowledge-base.md)
- Bright Data:
  [Scraper API FAQs](https://docs.brightdata.com/products/scrapers/scrapers-library/faqs),
  [YouTube discover videos by URL](https://docs.brightdata.com/api-reference/scrapers/social-media-apis/youtube-videos-discover-by-url)

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
