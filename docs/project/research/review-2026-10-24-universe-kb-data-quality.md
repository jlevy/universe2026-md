# Review: GitHub Universe KB Data Quality

**Date:** 2026-10-24

**Author:** Joshua Levy, with LLM assistance

**Status:** Reconciled for publication: all Blocker and High findings fixed; remaining
Medium and Low work tracked below.

> In this repository the records are in `kb/`, and the pipeline (`src/universe_kb/`,
> `raw/`, `curation/`, `synthesis/`, `schemas/` and `tests/`) is in `pipeline/`. Counts
> are as of the 2026-10-24 build; where this document and the data policy differ, the
> policy and the architecture doc describe the current design.

## Overview

This review audits the GitHub Universe knowledge base in `kb/` as built on 2026-10-24.
It covers the 2023, 2024, 2025 and 2026 editions: 591 people with 591 profiles, 520
sessions, 336 organizations, 1,286 repositories, 146 packages, 61 software entries,
1,420 accounts (258 GitHub, 1,162 social), 244 websites, 85 rooms, 64 venues, 4 events
with 14 days, 34 facets with 418 terms, 11 experiences and 9 pages (5,834 nodes and
26,380 edges in all).

**Method:** Three reviewers worked read-only, one per area: people and identity; program
and schedule; organizations, sponsors, repositories, packages and software.
Each loaded the graph into a private FalkorDB, recomputed counts from the KB payloads,
traced each finding to its evidence in `raw/` and `curation/`, and wrote read-only
Cypher checks for most findings.
Structural validation passes: `universe-kb validate` reports no failures and the
crawler’s 97 tests pass.
Severities are the reviewers’ own.

**Original verdict:** The 2026 schedule is sound: all 528 slots match the raw catalogs,
no room is double-booked, and every program session has speakers.
Identity merges hold: no account or site belongs to two people, all 86 cross-edition
people verify against their RainFocus `userRef`, and the evidence of all 4,986 profile
claims resolves. Sponsor listings match RainFocus for all 54 sponsors.
Three Blockers stop publication: 23 brief bios state a past job title at a newer
employer (P-1), IBM carries an unrelated 2-10 employee LinkedIn page’s facts (O-1), and
Figma is credited with an npm package someone else published (O-2). The 10 High findings
are wrong links and identities, wrong places and labels in the 2023–2025 schedules, and
organization records that mislead (job-title mentions, duplicates, stale size ranges).

## Severity Summary

| Area | Blocker | High | Medium | Low | Total |
| --- | --- | --- | --- | --- | --- |
| People and identity | 1 | 4 | 6 | 6 | 17 |
| Program and schedule | 0 | 3 | 7 | 6 | 16 |
| Organizations and software | 2 | 3 | 7 | 5 | 17 |
| **Total** | **3** | **10** | **20** | **17** | **50** |

## Findings

Fix locations name a crawler module in `pipeline/src/universe_kb/` (“build” is
`build.py` or the build step), a curation file in `pipeline/curation/`, or the consumer
(a site or other reader of the KB). “Known” says whether the KB plan’s Technical Debt or
Decision Log, the research doc, or an existing bead already records the issue.

### People and Identity

| ID | Severity | Finding | Count | Examples | Suggested fix (where) | Known |
| --- | --- | --- | --- | --- | --- | --- |
| P-1 | Blocker | Brief bio states a past listing’s job title at a newer employer; no source supports it (`raw/brightdata/linkedin_profiles.json` `current_company.title` is null for all), and the bio is reused as `summary` in `kb/_search/documents.jsonl` | 23 bios (18 clear, 5 borderline) | `person:speaker-a` (a staff engineer title from a past listing placed at a newer employer), `person:speaker-b` (a CEO title from a 2023 listing placed at another company), and two more | Crawler `bios.py`: put `job_title` in the bundle only with its listing organization and year, or when `listed_for` is 2026; add a `check_bio` rule rejecting `<job_title> at/of <org>` unless the organization is the listing’s; rewrite the 23 bios | partly |
| P-2 | High | X handles from past catalogs were re-registered by someone else | 3 confirmed, 1 likely | `acct:x/handle-a` (created 2025-01-08 by a new owner), `acct:x/handle-b`, `acct:x/handle-c`; likely `acct:x/handle-d` | Curation `people.yaml` `rejected_links`; build: flag event-listing-only accounts created after the listing edition or whose `profile_name` disagrees with the owner | no |
| P-3 | High | One person split into two IDs, both with the same RainFocus `userRef` | 1 pair | a short and a full form of one first name (2025, and 2026, 2024, 2023) | Curation `people.yaml` `names`; build: use `userRef` as the cross-edition identity key and prefer `globalFullName` | no |
| P-4 | High | Project, employer or podcast-network accounts attached to a person through rel="me" links on a site typed personal | 12 accounts, 3 people | one speaker: 8 accounts of the open-source project they lead, via the project’s site; another: 3 accounts of a podcast network, via a show page; a third: the employer’s Mastodon account, via the employer’s site | Curation `rejected_links` for the 3 sites; build: organization and project sites must not create person accounts | partly |
| P-5 | High | Malformed source values became links to wrong pages | 3 | `site:gmail.com` (a webmail address given as a website URL), `acct:linkedin/in/m` (2023 value “M/A”), `acct:linkedin/in/in` (a truncated profile URL) | Crawler `web.classify_social_url`: reject userinfo and mailto URLs, parse `in/<slug>`, reject placeholders (N/A, M/A, single letters) | no |
| P-6 | Medium | Personal email addresses copied into profile text and search documents | 11 GitHub accounts and `site:gmail.com`; 8 webmail addresses in `kb/_search/documents.jsonl` | five GitHub accounts of speakers, not named here | Build: redact email and mailto addresses from `profile_readme`, bios and search text | no |
| P-7 | Medium | Employer or product sites typed personal | 2 exact, 3 or more product sites | `site:fly.io`, `site:msidata.com`, `site:home-assistant.io`, `site:devcycle.com`, `site:runnable.com` | Build: decide the website kind after organization enrichment | partly |
| P-8 | Medium | Non-website pages typed as personal websites | 29 | `person:speaker-c` (18 “websites”, including a podcast episode, a conference agenda and video links), `person:speaker-d` (4 short-link redirects) | Build: classify platform profiles as accounts, skip deep third-party rel="me" targets, follow short links | no |
| P-9 | Medium | X display names dropped | 290 accounts (242 have a name in `raw/`) | `acct:x/handle-e` | Build: map Bright Data `profile_name` to `display_name` | no |
| P-10 | Medium | Several current employers, or one employer split across duplicate organizations | 16 people with 2+ current organizations; 25 split across duplicates | one company under its own name and its investment arm’s; a company and its `.io` spelling; a founder’s new company split across `org:<name>` and `org:<name>-hq` | Curation `organizations.yaml` aliases (see O-4); consumer: rank affiliations by basis | partly |
| P-11 | Medium | Expertise inflated by over-tagged sessions and duplicate labels | 54 profiles; 142 duplicate-label claims in 53 profiles; 105 “high” claims in 21 profiles | two co-speakers with 47 claims each (one 2024 session has 31 topics), and two more profiles | Build: merge claims by label, count distinct base talks, down-weight sessions with more than 10 topics | partly |
| P-12 | Low | Recognition claims with quote-only evidence; a past role shown as current | 26 claims, 20 profiles | three profiles, not named here | Build: add a ref or URL; treat “served as” and year ranges as past | partly |
| P-13 | Low | Event-listing affiliations carry no evidence pointer | 648 | every event-listing affiliation | Build: add the session URL or ref and the edition | no |
| P-14 | Low | Name variants not recorded | 4 or more | speakers listed under different family names in different editions | Build: `Person.alternate_names` from `fullName` vs `globalFullName` | no |
| P-15 | Low | Two LinkedIn entities for one profile (same `linkedin_num_id`) | 3 people | three people, not named here | Build: merge by `linkedin_num_id` | yes |
| P-16 | Low | Name and field cosmetics | about 20 | a person whose given name became “Dr.”, a slug that lost a non-ASCII letter, 13 attendees without given or family name, UTM text in a website ID | Build: strip honorifics, title-case names, drop UTM parameters | partly |
| P-17 | Low | Candidate attendee inferred from a post quoting a GitHub marketing email (`raw/mastodon/hashtags.json`) | 1 | one candidate attendee | Consumer: hide `candidate` attendees, or drop the person in curation | yes |

### Program and Schedule

| ID | Severity | Finding | Count | Examples | Suggested fix (where) | Known |
| --- | --- | --- | --- | --- | --- | --- |
| G-1 | High | Fort Mason rooms placed at “external” venues with a building name as the street address: `curation/venues.yaml` aliases are exact-match (`match_venue`, `build.py:944`), so these labels fall to the external branch (`build.py:986-993`) | 8 rooms, 55 sessions (2024: 26, 2025: 29) | `room:cowell-theater-gateway-pavilion-level-1` → `venue:cowell-theater` (address “Gateway Pavilion (Level 1)”, 11 sessions), `room:sandbox-stage-general-s-residence` → `venue:sandbox-stage` (13 sessions), `room:discussions-lounge-fort-mason-building-d`, `room:universe-plaza` | Curation `venues.yaml`: aliases for “Gateway Pavilion (Level 1)” and “(Level 2)”, “Fort Mason Building A” and “D”, and “Greens”; add General’s Residence and Universe Plaza as campus venues. Build: move a trailing “(Level N)” into `location_note` before matching | no |
| G-2 | High | Past-edition day labels follow date order instead of the catalog: 2025 is off by one, and 2023’s “Day 1” is (by inference) a pre-event workshop day | 4 days (2025), 3 days (2023) | `day:2025-10-27` “Day 1” (catalog `dayDisplayName` “Day 0”, 2 socials), `day:2025-10-28` “Day 2” (catalog “Day 1”, opening keynote), `day:2023-11-07` “Day 1” (4 Hyatt workshops vs 43 sessions on 11-08) | Build: take the label from `dayDisplayName` when it is “Day N”; otherwise number from the first main-program day and label lighter leading and trailing days “Pre-event” and “Post-event”, as 2026 does | no |
| G-3 | High | Catalog placeholder capacities published as real capacities; the build treats only “0” as unknown (`build.py:981`, `build.py:1043`) | 18 rooms, 57 slots (2025: 43 × 9999; 2023: 14 × 1,000,000); 2 of the rooms are also used in 2026 | `room:ybca-main-stage` (1,000,000), `room:bats-theatre-fort-mason-building-b` (9999, 10 sessions), `room:bar-darling-2263-chestnut-st` (9999, also shown on its 2026 session) | Build: treat 9999 and values of 100,000 or more as unknown (capacity `null`) for slots and rooms | no |
| G-4 | Medium | The same place under several venue or room IDs | Venues: Left Door ×3, Figma ×3, San Francisco Brewing ×2, Subpar ×2, and Cowell Theater, Discussions Lounge and Radhaus duplicated as external venues. Rooms: Barrio ×3, BATS Theatre ×2, For the Record ×2, Cowell Theater ×2 | `venue:left-door` / `venue:left-door-san-francisco` / `venue:left-door-sf`; `venue:figma-hq` / `venue:figma-sf-hq` / `venue:figma-office`; `room:bats-theatre-fort-mason-building-b` / `room:bats-theatre-fort-mason-building-b-3rd-floor` | Curation `venues.yaml`: a `same_as` or alias map for outside venues. Build: key a room by venue and normalized room name, keeping label variants in `source_ids` | no |
| G-5 | Medium | A venue merge keeps the first address seen (`build.py:991`), so a 2025 social shows the 2026 location | 1 venue, 1 session | `session:2025/1937` (Syntax Meetup, Salesforce Park, 425 Mission St) → `venue:barebottle-beer-garden` with address “1525 Cortland Ave” | Build: key outside venues by name and address, or curate the two Barebottle sites | no |
| G-6 | Medium | `Term.session_count` undercounts tracks taken from the fallback attribute | 3 terms, 6 sessions | `term:track/build-software-not-code` (99 vs 102 linked), `term:track/trust-every-commit` (37 vs 39), `term:track/lead-through-what-s-next` (52 vs 53) | Build (`build_facets`): count from the built sessions’ facet values, not from raw attributes | no |
| G-7 | Medium | External venues without a usable street address; addresses also omit “San Francisco, CA” | 25 (15 with none, 10 with non-street text, 8 of them G-1’s venues); 1 used in 2026 | `venue:redwood-empire-whiskey` (2026 social `session:2089`), `venue:pier-43-1-2` (“Fisherman’s Wharf”), `venue:tipsy-pig`, `venue:white-rabbit-bar` | Curation `venues.yaml`: addresses for outside venues, with city and state | no |
| G-8 | Medium | Room labels split the wrong way into venue names (`split_room_label`) | 5 venues | `venue:level-1` (“Level 1”, address “GitHub HQ”), `venue:hotel-zoe-tiburon-room`, `venue:hyatt-gallery-ballroom-ii` (10 sessions, 2023), `venue:motoring-coffee-1525-union-st`, `venue:virtual-room-day-1` (a livestream as a physical venue) | Curation: `places` prefixes and aliases (“Hyatt - ”, “Hotel Zoe, ”) and a GitHub HQ place with its address. Build: split on `@` with optional spaces; mark virtual rooms `kind: virtual` or drop them from venues | no |
| G-9 | Medium | Event `start` and `end` mean different things per edition | 4 events | `event:github-universe-2025` spans all sessions (2025-10-27T17:00 to 10-30T17:00, including pre-event socials and the post-event HQ day); `event:github-universe-2026` uses the JSON-LD main days (10-28 09:00 to 10-29 16:30) although its days run 10-26 to 10-30 | Build: use the main-program days for past editions, or add `program_start` and `program_end` beside the session span | no |
| G-10 | Medium | Sponsored past-edition sessions without a host organization: hosts come only from the 2026 sponsor list (`build.py:1110-1118`) | 30 (2024: 23, of which 12 are special events with no speakers; 2025: 7) | `session:2024/ai2035d` (Docker speaker), `session:2025/bld1722d` (PayPal), `session:2024/ai2102e` (“Pints & pizza with Docker”) | Build: for past editions, accept the speaker’s listed organization as host of a sponsored session. Curation `organizations.yaml`: `session_hosts` for the 12 special events | no |
| G-11 | Low | Experiences: free-text schedule, no edition link, one non-place entry, names lower-cased from slugs | 11 experiences | `experience:hack-your-badge` (schedule “Oct 28 8am–5pm; Oct 29 8:30am–5pm”, no year), `experience:curated-agendas` (no category, location or venue) | Build (`pages.py`): keep the structured `data-explore-add` days as `schedule_days`, add `event`, title-case names from the card text | no |
| G-12 | Low | Page content gaps and raw slug headings | 9 pages | `page:attendee-portal/sponsors` (no sections), `page:attendee-portal/speakers` (one heading, no text); 4 githubuniverse.com pages share the title “GitHub Universe 2026”; headings such as “oct27_day0” and “learn-and-build/” | Build: a display title from the H1 or path and a `display_heading` normalized from the slug, or leave both to the consumer | no |
| G-13 | Low | Media kinds and attributions | about 22 organization “logos”, 7 avatars, 8 homepage portraits | `org:grafana-labs`, `org:datadog`, `org:astral` (“logo” is a 1200×630 Open Graph card); `acct:x/handle-d` (X default avatar); homepage portraits used only by `page:githubuniverse.com/home`, not by the people shown | Build: classify og:image as `banner`, skip default avatars, link featured portraits to the featured people. Docs: the KB plan says 1,432 images; `kb/media.yaml` has 1,970 | no |
| G-14 | Low | Repeats and watch parties modeled differently across editions | 2 repeat pairs, 5 watch-party sessions | `session:2023/ai2748w` and `session:2023/ai2852w`, `session:2024/dev1677s` and `session:2024/dev1974o` (separate sessions, no `related`; 2026 uses one session with several slots, as in `session:2153b`); 2024 “Viewing Area (Keynote)” sessions are typed Keynote with no speakers | Build: add `related` (or `repeat_of`) for same-title, same-abstract pairs; link watch parties to the keynote at the same start | no |
| G-15 | Low | Highlight titles are video filenames | 5 | `event:github-universe-2026` highlights “github u-2025 opening keynote” and “idea to impact” | Curation display titles, or the consumer shows the thumbnail only | no |
| G-16 | Low | Two FalkorDB query pitfalls for browser and admin-UI authors | n/a | `count(*)` over `SCHEDULED_ON` returns 527 but `count(r)` returns 528 (the parallel edges of `session:2153b` collapse); concatenating a string with an aggregate in one `RETURN` yields `null` | Consumer: count relationships with `count(r)`, and aggregate in a `WITH` before concatenating, as the review checks do | no |

### Organizations and Software

| ID | Severity | Finding | Count | Examples | Suggested fix (where) | Known |
| --- | --- | --- | --- | --- | --- | --- |
| O-1 | Blocker | IBM merged with an unrelated LinkedIn page (“Knowledge Stream”, which names itself “IBM”): IBM shows 2-10 employees, industry “Software Development”, tagline “Digital Transformation”, no headquarters, the LinkedIn placeholder logo and Knowledge Stream’s description. `profile_sources.organization_details()` overwrites every scalar (even with null) for each page, so the last page wins | 1 organization (a Signal sponsor); any organization with 2+ LinkedIn pages is exposed | `org:ibm`, `acct:linkedin/company/knowledgestream` | Build: one canonical LinkedIn page per organization (website-domain match or a curated `linkedin:` pin); never merge scalars across pages; drop pages whose website domain differs. Curation: reject `company/knowledgestream` for `org:ibm` | no |
| O-2 | Blocker | npm `plugin-samples`, someone else’s copy that kept Figma’s `repository` field, is credited to Figma via `PUBLISHES` (`raw/packages/repo-packages.json`) | 1 | `pkg:npm/plugin-samples`, `org:figma`, `repo:figma/plugin-samples` | Crawler (`enrich-packages`): pointing back to the repository does not prove the publisher; also require npm maintainers or PyPI owners to match the organization, or a publish workflow in the repository; reject sample and template repositories | no (the point-back rule is deliberate; this case gets past it) |
| O-3 | High | “Principal” is a gazetteer organization name (from one past listing), so every “Principal Engineer/Researcher/Architect” text mentions the company; “Sonar” matched in “Sonar Batman suits” | 30 mention edges (29 Principal, 1 Sonar) | two people’s bios and `session:2024/dev1936m` → `org:principal`; `session:2025/1781` → `org:sonar` | Curation: add `Principal` to `software.yaml` `ambiguous_org_names` and alias it to `principal-financial-group` in `organizations.yaml`. Crawler: skip an organization-name match followed by a role noun (Engineer, Architect, Researcher) | no |
| O-4 | High | Duplicate organizations from legal suffixes, longer spellings and combined strings; 19 of 26 candidate pairs share a person, and mentions often land on the empty record | 24 redundant records over 20 companies | `org:cathay-pacific` / `-airlines` / `-airways`; `org:kpmg` (mentions, no people) / `org:kpmg-us` (3 people, LinkedIn); `org:entire` / `org:entire-hq` (which holds `gh:entirehq`); `org:otto` / `org:otto-gmbh-co-kg` / `org:otto-gmbh-co-kgaa`; unsplit `org:accenture-and-avanade` | Curation `organizations.yaml`: `aliases` per pair (keep the record with LinkedIn data), `split` for “Accenture and Avanade” and “CREATE / University of Washington”. Crawler: strip a trailing Group, Airways, Airlines, Insurance, US, USA, HQ, `.io` or `.com` when a shorter record exists. Merge only on evidence: Prudential plc and Prudential Financial are different companies | no |
| O-5 | High | LinkedIn’s self-reported size ranges are published verbatim and are stale for well-known companies, including the organizer | 15 records whose LinkedIn member count is more than twice the top of the range | `org:github` “501-1,000 employees” (6,979 LinkedIn members), `org:anthropic` 501-1,000 (6,244), `org:postman` (Platinum sponsor) 501-1,000 (3,591); OpenAI 1,001-5,000 (11,490) | Consumer: label size as “LinkedIn size range” or hide it. Crawler: keep `employees_in_linkedin` beside it. Curation: override the organizer’s size | no |
| O-6 | Medium | Platinum sponsor Postman and sponsor Rubrik have no GitHub organization: the search used the raw exhibitor names “Postman, Inc.” and “Rubrik, Inc.”, which return no candidates | 2 (9 sponsors lack a GitHub organization in all) | `org:postman` (expected `postmanlabs`), `org:rubrik` (expected `rubrikinc`) | Crawler (`enrich`): search with the normalized name. Curation: `github:` pins, verified first | partly (the research doc notes sponsor recall; this cause is new) |
| O-7 | Medium | Sponsors without LinkedIn industry, size or headquarters. JFrog and Accenture have a LinkedIn company account whose page was never fetched; GitProtect’s fetched page (`xopero-software`) was never attached, and GitProtect has no website | 25 of 54 sponsors, and 1 without a website | `org:jfrog` (Platinum), `org:accenture`, `org:gitprotect-io` | Crawler: fetch LinkedIn company pages for every sponsor (exhibitor `linkedinLink`, homepage or GitHub links). Curation: `linkedin: xopero-software` and `website: https://gitprotect.io` for `gitprotect-io` | no |
| O-8 | Medium | Organization `website` is a careers page, URL shortener or tracking link, taken from LinkedIn’s website field | 17 | `org:google` (goo.gle/3DLEokh), `org:meta` (metacareers.com), `org:moderna` (`?tc=soc_…`), `org:coursera` (bit.ly) | Crawler (`profile_sources._homepage`): prefer the GitHub organization’s `websiteUrl` or the homepage crawl’s `final_url`, drop query strings, reject careers and jobs paths and shortener hosts. Curation `website:` for the rest | no |
| O-9 | Medium | `MAINTAINS` includes pinned forks of other people’s projects and archived repositories; repositories carry no fork parent | 60 maintains edges (36 forks, 24 archived); 47 archived `TOP_REPOSITORY` edges | three speakers’ pinned forks (of GitHub Security Lab, a sample application and Home Assistant); IBM’s only top repository is `ibm/css-gridish` (archived, last push 2019) | Build (profiles): map pinned forks to `pins`, not `maintains`; add `parent { nameWithOwner }` to the GraphQL repository fields; flag archived repositories in `open_source` | no (the Decision Log covers only pins of others’ repositories) |
| O-10 | Medium | Gazetteer packages have no `PUBLISHED_FROM` or `PUBLISHES` edge, although 5 name a repository already in the KB | 7 | `pkg:npm/@github/copilot` (`repo:github/copilot-cli` is present), `pkg:npm/typescript`, `pkg:pypi/homeassistant` | Build (`build_software`): set `Package.repository` when the repository is in the KB, and the publisher to the repository owner or the software vendor | no |
| O-11 | Medium | Strings that are not organizations, and one person’s personal brands, become organization records | 3 | `org:self-employed` (one person’s current affiliation), and two records for one speaker’s personal brands | Curation `organizations.yaml`: add “Self Employed”, “Self-employed” and “Freelance” to `none`; alias the two brands | no |
| O-12 | Medium | Go modules with only a pseudo-version, and archived, sample or workshop repositories, count as published packages | 20 (11 Go pseudo-version modules) | a Go workshop module, a Go module with only `v0.0.0-2019…`, and an npm package archived in 2019 | Crawler: for Go, require a tagged `@latest` (not `v0.0.0-…`) or record `released: false`. Consumer: label archived packages | no (they meet the deliberate rule) |
| O-13 | Low | Parent and subsidiary pairs lack `RELATED_TO`; some software lacks its vendor or names the wrong one; one curation entry is dead | about 7 relations, 3 vendors, 1 entry | `org:amazon-web-services` / `org:amazon`, `org:google-deepmind` / `org:google`, `org:develocity` / `org:gradle`; `software:docker` (no vendor), `software:aws` (vendor `org:amazon`, not `org:amazon-web-services`), `software:ios` (no vendor); curation `nixos` is never applied, so `org:nixos-foundation` has no GitHub organization | Curation: `related` lists, `vendor:` fields, and repoint `nixos` to `nixos-foundation` | no |
| O-14 | Low | Organization names keep a listing’s odd casing or punctuation | 7 | “Linkedin Learning”, “Cathay Pacific airways”, “Fork Around and find Out”, “the LEGO Group”, “Xebia\|Xpirit”, “Otto GmbH &Co. KGaA” | Curation `name:` overrides, or prefer the attached LinkedIn page’s name | no |
| O-15 | Low | Descriptions carry LinkedIn page boilerplate, an HTML entity or a README badge | 3 | `org:experimental-machines` (“\| 18 followers on LinkedIn.”), a personal-brand record (`I&#39;m`), `pkg:npm/p5` (badge Markdown) | Crawler: use `about` before `description`, strip the follower boilerplate, unescape HTML, skip a first line that is only badges | no |
| O-16 | Low | Copilot sub-products matched as GitHub Copilot (“Copilot Autofix”, “Copilot Workspace”, “Copilot Spaces”), and “Copilot Code Review” with a capital R misses `software:copilot-code-review` | about 20 mentions | `session:2024/sec1175b` and two people’s bios | Curation `software.yaml`: entries or aliases for these products | partly (gazetteer recall is listed; the mis-attribution is not) |
| O-17 | Low | Speakers who gave a company account as their GitHub handle produce `MAINTAINS` and `PUBLISHES` edges from that account | 7 people, 2 maintains, 1 publishes | a speaker → a company’s user account → a PyPI package | Already tracked | yes |

## What Checked Out

**People and identity:**

- No account or site is shared between people; all 1,664 owner links are consistent, and
  display names match owners except 8 plausible nickname handles.
- All 86 cross-edition merges verify (78 share one `userRef`); no within-edition
  duplicates.
- All 183 2026 speakers have a current affiliation and a matching title.
- All 13 attendees are `public_self_report` with a post URL and quote.
- The injection text exists only in `raw/mastodon`, not in any bio or `kb/` file; no
  hidden zero-width or bidi text.
- No Enterprise Managed User logins and no phone numbers in `kb/`.
- All 591 bio bundles reproduce their hash (none stale); bios use no gendered pronouns
  or sensitive bundle details, and every year, organization and number they cite matches
  the bundle.
- 18 random, 13 attendee and about 60 targeted bios are accurate apart from P-1.
- The evidence of all 4,986 profile claims resolves; curation `rejected_links` and
  `names` are all applied.

**Program and schedule:**

- All 528 slots equal the raw catalog’s UTC start and end, local time and date; offsets
  are America/Los_Angeles (PDT in October, PST on 2023-11-07 to 2023-11-09).
- Slot days match local start dates and the event’s days; every end is after its start;
  durations (15–300 minutes, plus one 540-minute HQ day) match the glossary except one
  30-minute 2025 fireside chat and the five 30-minute 2026 Speakeasy breakout slots.
- No room is double-booked; watch parties have their own rooms.
- Every session’s `event` matches its ID namespace and start year; every session has
  slots, a room and a type.
- Every catalog row is in the KB except the two 2025 test records, which are correctly
  dropped.
- Only Social, Special Event and keynote viewing-area sessions have no speakers; no
  speaker appears twice on a session; `order` is 0..n-1.
- Speaker roles match the raw catalog for 777 of 791 links (the other 14 are intended
  renames and `userRef` merges); `Person.sessions` and `Session.speakers` agree.
- Taxonomy: 34 facets, no duplicate term IDs or labels, no zero-session terms, no
  cross-edition term links; all 29 terms with a glossary entry carry its description.
- Every room has a session, `Room.sessions` matches `HELD_IN`, room capacity equals the
  largest slot capacity, and every campus building has
  `parent: venue:fort-mason-center`.
- The FAQ’s 14 entries match the raw page; all 1,970 media URLs are unique absolute
  https URLs and every `used_by` ID resolves.
- Event offers, 8 tour stops and 8 featured speakers (all with 2026 sessions) are
  correct; after-party sessions link to their main-stage session.

**Organizations and software:**

- All 54 sponsors match `raw/rainfocus/exhibitors.json` (tier, summary, logo, and links
  once UTM tracking is stripped); only 1Password has a booth in the source.
- The 54 `SPONSORS` edges carry the right tier; the 81 `HOSTS` edges equal
  `hosted_sessions`.
- All 71 organizations with a GitHub account have a plausible GitHub name and website,
  including curated pins.
- A LinkedIn spot check of 40+ short or ambiguous organization names found every page
  plausible except IBM (O-1).
- Repository owners are consistent for all 913 owned repositories; IDs and URLs match
  `full_name`.
- All 436 `MAINTAINS` edges come from the person’s own GitHub account; no person is
  linked to an organization-type GitHub account.
- `PINNED`, `pinned_by` and `PINS` agree (657 each); `pins` and `maintains` never
  overlap; star counts agree, and none is implausible (maximum `vinta/awesome-python`,
  329k).
- 139 of 146 packages point back to a repository in the KB; package and software links
  agree.
- Software vendors are correct where set; all 12 `CATALOG_TERM` links are valid; spot
  checks of common product mentions (Git, Rust, Docker, bare “Copilot”) are correct.
- Every organization has a relationship, and every role is backed by its edge.

## Review Checks in the Browser

The reviewers’ checks are in
[`review.py`](https://github.com/jlevy/paraverse/blob/main/db/src/paraverse_graph/review.py)
in Paraverse (33 read-only Cypher checks, each returning `id`, `name` and `detail` so
every row links to its entity).
The KB browser (`paraverse-graph serve`, documented in
[Paraverse’s `db/README.md`](https://github.com/jlevy/paraverse/blob/main/db/README.md))
shows them in its `#/review` view and serves them at `/api/review`. Row counts below are
on the KB as built on 2026-10-24, with the findings each check detects.

- **Graph:** `isolated_entities`, `accounts_without_owner`, `people_same_name`
- **Program:** `slot_day_mismatch` (0), `session_edition_mismatch` (0),
  `room_double_booked` (0), `day_one_is_pre_event` (2, G-2), `term_session_count_drift`
  (3, G-6), `campus_room_at_external_venue` (8, G-1),
  `external_venue_without_street_address` (25, G-7), `possible_duplicate_places` (11,
  G-4), `placeholder_capacity` (18, G-3), `program_session_without_speakers` (0)
- **Organizations:** `org_multiple_linkedin_pages` (1, O-1),
  `org_name_prefix_duplicates` (26, O-4), `org_mention_is_job_title_word` (29, O-3),
  `org_size_implausible` (1), `org_website_not_homepage` (17, O-8),
  `sponsor_missing_core_data` (30, O-6 and O-7), `person_maintains_fork_or_archived`
  (60, O-9), `package_unlinked` (7, O-10), `package_unlikely_release` (20, O-2 and
  O-12), `org_without_profile_data` (97)
- **People:** `brief_bio_past_title_at_new_employer` (25, P-1),
  `past_title_paired_with_new_employer` (107, P-1), `possible_split_person` (1, P-3),
  `listed_account_created_after_listing` (4, P-2), `malformed_or_email_link` (3, P-5),
  `personal_email_in_text` (12, P-6), `rel_me_only_account_on_person` (30, P-4),
  `employer_site_typed_personal` (4, P-7), `several_current_employers` (16, P-10),
  `overbroad_session_expertise` (54, P-11)

No check detects O-5 yet: the KB does not store LinkedIn’s member count
(`employees_in_linkedin`). A check’s severity in `review.py` can differ from its
finding’s: `package_unlikely_release` is medium but includes Blocker O-2, and
`rel_me_only_account_on_person` is medium but includes High P-4.

## Notes

- Findings are as of the KB built on 2026-10-24; rerun the checks after each KB build.
- Counts from a check and a hand review can differ.
  P-1’s check returns 25 rows, of which 20 were confirmed by hand; the bio-by-bio review
  counts 18 clear and 5 borderline bios, so the fix covers 23. O-3’s check misses the
  Sonar edge, and O-4’s 26 check rows reduce to 24 redundant records.
- Out of slice: the program reviewer also saw a person with `acct:linkedin/in/in`, a
  LinkedIn account whose slug is “in”; it is one of P-5’s three cases.
- Overlaps: P-10 is the people side of O-4; P-7 and P-4 share `site:fly.io` and
  `site:home-assistant.io`; G-13’s default-avatar case `acct:x/handle-d` is P-2’s likely
  re-registered handle.
- Deliberate choices not counted as findings: lowercase “hosted by” in abstracts does
  not set a host (G-10); `CONTRIBUTES_TO` counts any commit or opened pull request;
  organizations added from LinkedIn or GitHub company fields get no mentions, since the
  gazetteer is collected before those sources run.
- Related plan: [the KB plan](../specs/done/plan-2026-10-24-universe-knowledge-base.md)
  (Technical Debt and Decision Log).

## Publication Reconciliation

The tables above retain the original review baseline.
The sanitized import resolves all three Blockers and ten High findings.
The remaining Medium and Low items stay open under their individual beads; their
dependency is the focused follow-up named below, rather than a future date.
The review parent is `u26-9kht`.

Verification covers the full pipeline suite (144 tests), Ruff, type checking, schema
validation, independent offline rebuilds, byte comparison, contact and exclusion scans,
and stored-bio validation.
Regression coverage is in `pipeline/tests/test_data_quality.py`, `test_bios.py`,
`test_people.py`, `test_ids.py`, `test_web.py`, `test_policy.py`, `test_privacy.py` and
`test_publication.py`. No new source acquisition was needed.

| Finding | Disposition | Bead | Evidence or follow-up dependency |
| --- | --- | --- | --- |
| P-1 | fixed | `u26-neyr` | Scoped listing roles; unsupported title/employer pairings fail bio checks; affected derived text corrected. |
| P-2 | fixed | `u26-fnsr` | Catalog-only X identity checks; persistent owner/link fingerprints hold after raw pruning. |
| P-3 | fixed | `u26-fcfd` | Cross-edition identity uses catalog userRef and global names; no duplicate userRefs remain. |
| P-4 | fixed | `u26-4yuf` | Site links corroborate attributed accounts; they cannot establish new person-account ownership. |
| P-5 | fixed | `u26-q7w7` | Validated provider/profile paths reject credentials, placeholders, truncated LinkedIn paths and webmail sites. |
| P-6 | fixed | `u26-ieaj` | Contact redaction and full publishable-input/output scans report zero reachable contacts. |
| P-7 | deferred | `u26-sku3` | Broader website-kind classification and source review. |
| P-8 | deferred | `u26-6r4j` | Additional platform and redirect classification. |
| P-9 | fixed | `u26-1qad` | X display names use profile_name with a name fallback; profile-source tests cover the mapping. |
| P-10 | deferred | `u26-lxm2` | Affiliation ranking and further evidence-backed organization reconciliation. |
| P-11 | deferred | `u26-6lv3` | Expertise scoring and distinct-talk weighting. |
| P-12 | deferred | `u26-1310` | Recognition evidence and historical-status modeling. |
| P-13 | deferred | `u26-zhlu` | Event-listing affiliation evidence pointers. |
| P-14 | deferred | `u26-c2a7` | An alternate-names model and source mapping. |
| P-15 | deferred | `u26-pmo9` | LinkedIn numeric-ID reconciliation. |
| P-16 | deferred | `u26-qk3b` | Name and URL display normalization. |
| P-17 | fixed | `u26-2cuy` | Opaque suppression remains effective in offline rebuilds; no identifying strings remain in publishable files. |
| G-1 | fixed | `u26-tzrj` | Campus venue aliases and level parsing remove the incorrect external-venue assignments. |
| G-2 | fixed | `u26-ehfp` | Catalog day labels are preserved; the earlier workshop day is labeled Pre-event. |
| G-3 | fixed | `u26-9ua5` | Sentinel capacities are unknown in slots and rooms; final output contains none of the placeholders. |
| G-4 | deferred | `u26-y19i` | Further evidence-backed venue and room identity reconciliation. |
| G-5 | deferred | `u26-vmh1` | Edition-specific outside-venue addresses. |
| G-6 | deferred | `u26-i6qt` | Facet counts derived from built sessions. |
| G-7 | deferred | `u26-x7dd` | Public-source verification of outside-venue addresses. |
| G-8 | deferred | `u26-8bhq` | Remaining outside/virtual room parsing rules. |
| G-9 | deferred | `u26-17f8` | Explicit program-date versus session-span semantics. |
| G-10 | deferred | `u26-1vse` | Past-edition sponsor-host attribution. |
| G-11 | deferred | `u26-3w9g` | Structured experience schedules and edition links. |
| G-12 | deferred | `u26-rpsi` | Page display-title extraction. |
| G-13 | deferred | `u26-i9c3` | Media-kind, attribution and count reconciliation. |
| G-14 | deferred | `u26-7qu5` | Explicit repeat/watch-party relationships. |
| G-15 | deferred | `u26-vegd` | Curated highlight display titles. |
| G-16 | deferred | `u26-pw1e` | Consumer query guidance and query-specific checks. |
| O-1 | fixed | `u26-34ea` | One canonical LinkedIn company page supplies organization scalars; unrelated page links are rejected. |
| O-2 | fixed | `u26-i93b` | Sample/template metadata retains no unsupported repository or publisher attribution. |
| O-3 | fixed | `u26-c2pi` | Ambiguous organization words do not create job-title mention edges. |
| O-4 | fixed | `u26-9hh0` | Eighteen supported redundant records are merged; potentially distinct legal/parent entities remain separate. |
| O-5 | fixed | `u26-q8g4` | Size is explicitly labeled LinkedIn size range; it is not presented as a verified headcount. |
| O-6 | deferred | `u26-uuwz` | Verified GitHub organization pins for remaining sponsors. |
| O-7 | deferred | `u26-aui8` | Additional sponsor LinkedIn source coverage. |
| O-8 | deferred | `u26-fsrs` | Organization homepage normalization and source precedence. |
| O-9 | deferred | `u26-0cdd` | Pinned-fork versus maintainer semantics. |
| O-10 | deferred | `u26-yaso` | Gazetteer package repository/publisher mapping. |
| O-11 | deferred | `u26-bria` | Additional organization-label curation. |
| O-12 | deferred | `u26-3xez` | Go pseudo-version and remaining package-release semantics. |
| O-13 | deferred | `u26-sszv` | Parent/subsidiary and software-vendor relationships. |
| O-14 | deferred | `u26-daty` | Organization display-name curation. |
| O-15 | deferred | `u26-4hks` | Organization description cleanup. |
| O-16 | deferred | `u26-y247` | Copilot sub-product aliases. |
| O-17 | fixed | `u26-tep1` | Company GitHub handles remain organization accounts; they do not become person-owned publishing accounts. |

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
