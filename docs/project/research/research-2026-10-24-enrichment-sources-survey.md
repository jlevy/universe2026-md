# Other Public Sources for the GitHub Universe Knowledge Base

A survey of public data sources, other than Bright Data, that could fill gaps in the
GitHub Universe knowledge base (`kb/`), checked on 2026-10-24.

The priority is people: interests, past work (talks, writing, publications, patents,
projects, podcasts, videos, open source), communities and recognitions.
Conference-level content (recordings, transcripts, slides, editions before 2023, side
events) comes second.

## How This Was Checked

- **Official documentation first.** Each source was checked against its own docs, terms
  or robots.txt with web search and fetch.
  Where a doc page would not load, the source was tested live with one or two read-only
  requests, and the table says so.
- **Verification markers.** In the Access column, **(docs)** means the official
  documentation or terms were read, **(live)** means an endpoint was called and
  answered, and **(secondary)** means only third-party sources were found.
- **Coverage probes.** For a few sources the kb’s own accounts were probed to measure
  coverage instead of guessing.
  The probes were read-only, ran at one request per second per service, and kept only
  counts. The kb has 187 GitHub user accounts (258 GitHub accounts including
  organizations), 78 Bluesky actors and 33 Mastodon accounts in the snapshot.
- **What the kb already uses** (event catalogs, GitHub GraphQL basics, Bluesky and
  Mastodon profiles, homepages and their feeds, registry verification, Bright Data) is
  not re-proposed, except where a clearly unused part exists.
  Those rows are marked **unused part**.

### Coverage Probe Results

| Probe | Result |
| --- | --- |
| GitHub GraphQL program flags (187 users) | 82 `isEmployee`, 8 `isGitHubStar`, 3 `isCampusExpert`, 13 `isDeveloperProgramMember` |
| GitHub Sponsors and lists (187 users) | 23 public Sponsors listings, 13 sponsor someone publicly, 10 have sponsors, 41 have star lists |
| GitHub history (187 users) | 85 started at least one discussion; 125 have 10 or more contribution years (the kb reads only the last year) |
| Bluesky (78 actors) | 47 posted in the last 6 months; 12 created starter packs |
| Mastodon (33 accounts) | 4 publish featured hashtags |
| Back-linked accounts (187 users) | DEV 36 (47 share the username; 36 name the same GitHub account); Keybase GitHub proof 27; crates.io account 10 (5 own a crate); Notist 6 |
| Profile links already in the kb and raw snapshot (unique profiles) | Medium 15, GitHub Stars 5, dev.to 4, Microsoft MVP 3, Credly 3, Substack 3, Hugging Face 2, Hashnode 2, and 1 each for Sessionize, Stack Overflow, Keybase, Hacker News and Speaker Deck |

The last row shows that direct links are rare.
Most sources below have to be found by **handle probe with back-link check**: ask the
other service for the person’s GitHub login (or X handle), and accept the account only
when that service’s profile names the same GitHub account (dev.to `github_username`,
Notist `github`, Keybase proof, crates.io GitHub OAuth, Sessionize bio link).
A shared username alone is never enough.

## Source Table

Columns: what the source adds for people and for the conference; how to access it (API
or feed, auth, price, limits, terms); how to link a record to a kb person safely; likely
coverage for this population; privacy notes.

### Talks, Video and Slides

| Source | Provides (people; conference) | Access, price, limits, terms | Linking to a kb person | Coverage | Privacy |
| --- | --- | --- | --- | --- | --- |
| **YouTube Data API v3** | People: videos on people’s own channels (16 YouTube accounts in the kb) and talks on other channels. Conference: the @GitHub channel’s playlists tab lists playlists titled “GitHub Universe 2023”, “2024”, “2025” and “2026”; video title, description, duration, publish date | REST; an API key is enough for public data; free. Default quota is 10,000 units/day plus 100 `search.list` calls/day; most list calls cost 1 unit. **Captions:** `captions.list` (50 units) and `captions.download` (200 units) need OAuth, and download needs permission to edit the video, so there is no compliant way to get transcripts of GitHub’s or anyone else’s videos. **Terms:** Developer Policies III.E.4: data fetched without user authorization may be kept “no longer than 30 calendar days”, then deleted or refreshed; III.E.1 bars downloading or storing audiovisual content; III.E.6 bars scraping. (docs) | Universe playlist video to kb session by normalized title and edition year, then to speakers through the session (high precision for GitHub’s own playlists). People’s channels only from a YouTube URL they list (GitHub social accounts, `rel="me"`). Name search gives candidates only; accept when the channel or description links a known account | High for recordings of 2023–2025 sessions; medium for people | The 30-day rule conflicts with a committed snapshot: either refresh on every build or keep only video URLs that GitHub also publishes elsewhere. Do not store comments or subscriber counts |
| **Sessionize public speaker profiles** | People: bio, company, city, area of expertise and topics, session abstracts, and a dated **events list** (event, month, city, talk title), plus links (GitHub, LinkedIn, blog). Conference: other events where kb speakers spoke | HTML at `sessionize.com/<slug>`; free. The Sessionize API is per event: organizers create JSON or XML endpoints, no auth, cached up to 5 minutes; there is no global speaker API. Terms do not mention automated access; robots.txt disallows only `/app/` and `/submission/helper/`. (docs, live) | Profile URL the person lists (1 in the kb), or a speakers-directory name match accepted only when the profile’s GitHub or LinkedIn link equals a kb account | Medium: community speakers, MVPs and developer advocates use it heavily; GitHub staff and executives less | Skip the “Contact” form. Keep city-level location only |
| **Speaker Deck** | People: decks with title, date and event | No documented API. Per-user Atom feed (`speakerdeck.com/<user>.atom`) works, but robots.txt disallows `/*.atom*` for crawlers, so read the HTML profile page for the few people who link it. oEmbed for single decks. (live) | Only a Speaker Deck URL the person lists (1 in the kb) | Low | Public decks only |
| **Notist** | People: presentations, events, slides and video links | JSON:API at `noti.st/<user>.json` (linked as `rel="alternate"`); free, no auth; no published limits; terms page not found. (live, secondary) | The JSON carries `github` and `twitter` usernames: back-link check against kb accounts (high precision) | Low: 6 of 187 GitHub users have a Notist profile naming their GitHub account | Profile JSON includes latitude and longitude: keep city only |
| **SlideShare** | People: slide decks | The old developer API was free for non-commercial use with a key; Scribd, which owns SlideShare since 2020, no longer issues API accounts. (secondary) | Only URLs people list | Low | n/a |
| **Internet Archive Wayback CDX and snapshots** | Conference: githubuniverse.com editions 2015–2022. 2015–2019 are static sites with `speakers/`, `program/` or `schedule/`, `watch/`, `workshops/` pages and speaker photos; 2020 has about 100 per-session pages; 2021 ran on Swoogo with `2021/session/<id>/<slug>` pages; 2022 was a single-page app whose archived bundle (`static/js/main.4b67e39e.js`, 2.7 MB, captured 2022-11-04) embeds about 112 titles and speaker social links. Also 2016–2017 site blog feeds and sponsorship prospectus PDFs. People: old speaker bios; **Lanyrd** speaker profiles (2010–2018), archived at `lanyrd.com/profile/<twitter-handle>/` | CDX API `web.archive.org/cdx/search/cdx`, free, no key; fetch raw captures with the `id_` modifier. No published limit; Internet Archive staff asked the `wayback` Python library to stay under about 60 requests a minute. (live, secondary) | Universe pages: session titles and speaker names, joined to kb people by name plus edition plus company. Lanyrd: by X handle (the kb has 290 X accounts), with the name on the page corroborating | High for editions before 2023; medium for Lanyrd (long-time speakers, e.g. captures exist for `burkeholland` 2012–2013 and `jamesmontemagno` 2014–2015) | Archived pages are public but old; keep professional talk data only |
| **GitHub blog and changelog** | People: posts by GitHub staff and guest authors (title, date, category). Conference: Universe announcements, schedule guides, talk round-ups (“10 technical talks I’m excited about at GitHub Universe 2026”), recaps, and changelog entries for features launched at Universe | WordPress REST: `github.blog/wp-json/wp/v2/posts?search=…`, `/wp/v2/coauthors`, `/wp/v2/guest-author`; RSS at `github.blog/feed/`, `github.blog/changelog/feed/` and `github.blog/author/<slug>/feed/`; no auth, no stated limit. (live) | The co-author taxonomy names are GitHub logins (term `cap-andreagriffiths11`, name `andreagriffiths11`), and author pages link `github.com/<login>`: exact GitHub-login match | High for the roughly 210 people whose kb records reference GitHub the organization (82 of 187 GitHub users carry `isEmployee`); low for others | Public |
| **Other conference datasets** | confs.tech `conference-data`: conference listings only (name, dates, city, CFP, Twitter), MIT. `pyvideo/data`: Python conference talks with speakers and video links, CC0. pretalx and Sessionize per-event endpoints: past talks at events that publish them | Free. pretalx: schedule endpoints are public, tokens add data. (docs, live) | Name plus event plus company; pyvideo speaker names only | Low | Public |

### Writing and Podcasts

| Source | Provides (people; conference) | Access, price, limits, terms | Linking to a kb person | Coverage | Privacy |
| --- | --- | --- | --- | --- | --- |
| **DEV (Forem) API** | People: articles (title, tags, date, reactions), profile summary, `github_username`, `twitter_username`, `website_url` | `GET dev.to/api/users/by_username?url=<name>`, `GET /api/articles?username=<name>`; public reads work without a key; free; no published rate limit. (docs, live) | Handle probe with back-link check on `github_username` (high precision) | Medium: 36 of 187 GitHub users have a DEV account naming their GitHub login | Tags are self-chosen interests; store metadata, not bodies. DEV returned 429s at one request a second, so pace at about 1.5 seconds and back off |
| **Medium, Substack, Hashnode feeds** | People: recent posts (Medium returns 10 items; Substack `<pub>.substack.com/feed`; Hashnode `<blog>/rss.xml`) | RSS, free. Medium’s robots.txt blocks AI crawler user agents (ClaudeBot, GPTBot and others) site-wide; fetch only feeds people link, with the project’s own user agent. **Hashnode’s GraphQL API became paid on 2026-05-13** (“Every API request … now requires a Pro plan”), so use blog RSS. (live, docs) | Only feed URLs the person lists (about 15 Medium, 3 Substack, 2 Hashnode in the kb) | Medium | Keep title, link and date, as the kb does for homepage feeds |
| **Podcast Index API** | People: episodes that mention a person; `search/byperson` searches person tags, episode titles and descriptions, feed owner and feed author. Shows a person hosts | Free key and secret; SHA-1 `Authorization` header with `X-Auth-Date`; limits at Podcast Index’s discretion. **Terms 5.5:** do not “build databases, or otherwise create permanent copies”, or cache longer than cache headers allow. (docs) | Names are weak: accept an episode only when a Podcasting 2.0 person tag or the description names the person together with their company or a known handle | Medium (developer advocates, founders, executives) | Use for discovery only; store the episode GUID and feed URL and read details from the show’s own RSS feed |
| **Podcast RSS feeds directly** | People: guest appearances in episode descriptions and `podcast:person` tags. The GitHub Podcast (`feeds.simplecast.com/ioCY0vfY`, 54 episodes, 2021-05 to 2026-10, no person tags) and GitHub at Work | Public RSS, free. (live) | GitHub’s own shows: guest name plus GitHub affiliation | Medium for GitHub staff | Public |
| **Apple Podcasts (iTunes Search API)** | Finds podcasts and their `feedUrl` | No auth; about 20 calls a minute; promotional content may be used “only to promote store content”. (docs) | Discovery of feeds only | Low to medium | Use only to locate feed URLs |
| **Listen Notes API** | Full-text episode search, including people; transcripts on paid plans | Free: 150 requests a month; Pro: $200 base with 5,000 requests, then $1.60 per 1,000. Free and Pro may not store anything server-side except `id` and `pub_date`; a “Powered by Listen Notes” logo is required. (docs) | Same as Podcast Index | Medium | Storage rule makes it a poor fit |
| **Podchaser API** | 27 million host, guest and crew credits (the most direct record of guest appearances) and transcripts | Enterprise GraphQL API; prices not published; third parties report a free tier of 25,000 query points a month. It also sells a “Contacts” product. (docs, secondary) | Credits are per creator; corroborate with company or handle | Medium | Never use the contacts data |
| **Spotify Web API** | Shows and episodes, including guest names in descriptions | OAuth app; development mode allows 5 allow-listed users and needs a Premium owner; extended quota only for organizations with 250,000 monthly active users (since 2025-05-15). Developer Terms IV.3.a forbid storing or compiling “databases of Spotify Content”, and IV.2.a forbid using it for AI models. (docs) | n/a | Medium in principle | See the do-not-use list |

### Q&A and Communities

| Source | Provides (people; conference) | Access, price, limits, terms | Linking to a kb person | Coverage | Privacy |
| --- | --- | --- | --- | --- | --- |
| **Bluesky AppView, unused part** | People: posts (`app.bsky.feed.getAuthorFeed`), starter packs a person created (`app.bsky.graph.getActorStarterPacks`) and lists (`getLists`) as community signals, by name and description. Conference: posts by kb people that mention Universe | `public.api.bsky.app`, no auth, free; `searchPosts` returns 403 without login. (live) | DIDs are already in the kb | Medium: 47 of 78 posted in the last 6 months; 12 created starter packs | Derive topics; do not keep full post text longer than needed; re-fetch so deletions propagate; do not harvest follow graphs, or the members of starter packs and lists, which are other people’s data |
| **Mastodon, unused part** | People: featured hashtags (`/api/v1/accounts/:id/featured_tags`), which are interests the person chose, and posts (`/statuses`) | Each instance’s public API, no auth. (live) | Account IDs are already in the kb | Low: 4 of 33 publish featured tags | Respect accounts that opt out of discovery or indexing |
| **Stack Exchange API** | People: top tags by score (`/users/{id}/top-tags`), answers, badges, reputation; linked network accounts (`/users/{ids}/associated`); profile website | Free. Without a key the quota is 300 requests a day per IP (observed `quota_max`); with a key 10,000 a day; over 30 requests a second per IP is banned; obey `backoff`. Terms require showing Stack Exchange as the source. (docs, live) | A Stack Overflow URL the person lists (1 in the kb), or a profile `website_url` equal to a kb website | Low to medium | Content is CC BY-SA: attribute any quoted text |
| **Hacker News (Algolia search API and HN Firebase API)** | People: stories and comments by author (`tags=author_<user>`), profile `about` and karma | Free, no auth; no official rate limit published (a community client cites 10,000 requests an hour per IP). (live, secondary) | Only an HN account the person lists (1 in the kb) or a Keybase proof; never by name | Low | Comments are opinions: use for aggregate topics, do not quote |
| **Lobsters** | People: profile `about`, submissions | `lobste.rs/~<user>.json`, no auth, undocumented. (live) | Only a listed account | Low | Same as Hacker News |
| **Reddit Data API** | People: posts and comments | OAuth; since the November 2025 Responsible Builder Policy, new tokens need approval (secondary); free access is non-commercial; Data API Terms 3.2 forbid retaining data beyond the approved use case. (docs, secondary) | Only a listed account (3 in the kb) | Low | See the do-not-use list |
| **Discord and Slack (public communities)** | People: membership and messages in developer communities | Reading needs a bot or account inside each server or workspace. Discord’s Developer Policy: “Do not use API Data to: profile Discord users”. Slack’s API terms forbid “persistent copies, archives, indexes, or long-term data stores”. (docs) | n/a | Unknown | See the do-not-use list |
| **Product Hunt API v2** | People: products launched by makers | GraphQL; access token required; “must not be used for commercial purposes” without permission; fair-use rate limiting. (docs) | Maker profile linked from the person’s site | Low (founders only) | Non-commercial only |

### Research and Intellectual Property

| Source | Provides (people; conference) | Access, price, limits, terms | Linking to a kb person | Coverage | Privacy |
| --- | --- | --- | --- | --- | --- |
| **OpenAlex** | People: works, topics, institutions, co-authors, ORCID crosswalk | REST; basic queries need no key (10 requests a second); a free key gives $1 of usage a day and 30 requests a second, and is required for cursor paging. Data has long been published as CC0 (confirmed by secondary sources on this pass). (docs) | ORCID iD the person lists, or name plus institution or employer plus topic; OpenAlex author disambiguation is imperfect | Low to medium (GitHub Next, Microsoft Research and university speakers) | Public scholarly record |
| **Semantic Scholar API** | People: papers, author profiles, citations | Most endpoints public; unauthenticated pool shares 1,000 requests a second; new keys start at 1 request a second; license requires attribution to Semantic Scholar. (docs) | As OpenAlex | Low to medium | Public |
| **ORCID Public API** | People: employment, education, works, other identifiers | Anonymous reads work at `pub.orcid.org/v3.0`; credentials are free. The Public APIs license is non-commercial (“may not make use of the public APIs in connection with any revenue-generating product”). (docs, live) | Only an ORCID iD the person lists or Wikidata states | Low | Only fields the researcher marked public |
| **dblp** | People: computer-science publications | The search API returned an Anubis bot check to scripted requests on 2026-10-24; the monthly XML dump is on Dagstuhl DROPS. (live) | Name plus affiliation; dblp has its own disambiguation | Low | Public |
| **Crossref REST API** | People: works by author name | No sign-up; add `mailto` for the polite pool (observed limit 3 requests a second); metadata may be used “for any purpose”. (docs, live) | Names only: use through ORCID | Low | Public |
| **arXiv API** | People: preprints | One request every 3 seconds, one connection; metadata is CC0; do not serve PDFs. (docs) | Name plus topic plus affiliation | Low | Public |
| **Google Patents public data (BigQuery)** | People: patents as inventor, with assignee and dates | BigQuery `patents-public-data`; the first 1 TiB of queries a month is free, then per-TiB on-demand pricing. **PatentsView’s API has been paused since 2026-03-20** for its move to the USPTO Open Data Portal, whose API key requires a USPTO.gov account (ID.me verification per secondary sources). (docs, secondary) | Inventor name plus assignee equal to a kb employer plus city: still only medium precision, so mark as candidate unless the person lists the patent | Low to medium (engineers and executives at large companies) | Inventor addresses: keep city and country at most |
| **Open Library and Google Books** | People: books authored | Open Library: 1 request a second (3 with a User-Agent and email), bulk via monthly dumps, “do not use our APIs to bulk download”. Google Books: API key or token required; `inauthor:` search; results vary by IP location. (docs) | Name plus subject plus a bio mention of the book | Low | Public |

### Recognition Programs

| Source | Provides (people; conference) | Access, price, limits, terms | Linking to a kb person | Coverage | Privacy |
| --- | --- | --- | --- | --- | --- |
| **GitHub Stars profiles** | People: bio, links and dated **community contributions** by type: Speaking, Video/Podcast, Blog posts, Articles, Open source, Event organization | HTML at `stars.github.com/profiles/<login>/`; no API found (`api-stars.github.com` did not answer); free. (live) | Path is the GitHub login; confirm with GraphQL `isGitHubStar` | Low: 8 current Stars among 187 users, but each profile is rich | Public |
| **GitHub GraphQL program flags** | People: `isGitHubStar`, `isCampusExpert`, `isEmployee`, `isDeveloperProgramMember`, `isBountyHunter` | Same token and query the kb already runs. (docs, live) | Exact | High (see probe) | Public flags |
| **CNCF people (`cncf/people`, `people.json`)** | People: 5,635 records with categories Kubestronaut 4,653, Golden-Kubestronaut 569, Mentee 653, Ambassadors 302, Staff 44, Governing Board 29, TOC 13, End User TAB 12; fields `github` (3,551 filled), `twitter`, `linkedin`, `website`, `youtube`, `company`, `bio` | Raw JSON from GitHub, MIT, updated daily. (live) | `github` field equals a kb login | Medium for cloud-native speakers | Drop `slack_id` and `wechat` |
| **Java Champions (`aalmiray/java-champions`)** | People: membership and status (alumni, retired, honorary), social links including `github`, `bluesky`, `mastodon`, `sessionize`; `podcasts.yml` | Raw YAML from GitHub. (live) | `github` or other listed handle | Low | The file records country of birth and citizenship: never collect those |
| **Microsoft MVP and Regional Director profiles** | People: award categories, award years, and public activities (talks, blogs, videos) | `mvp.microsoft.com/<locale>/mvp/profile/<id>`; robots.txt allows `/*/mvp/profile/*`; the site’s backend API (`mavenapi-prod.microsoft.com`) is undocumented, so do not call it. (live) | Only profiles people link (3 in the kb), or bio claims verified by visiting the profile | Low to medium | Public |
| **Google Developer Experts, AWS Heroes, Docker Captains** | People: program membership, expertise area | Public directories, JavaScript-rendered, no API: GDE profiles at `developers.google.com/community/experts/directory/profile/…`, AWS Heroes now inside AWS Builder Center, Docker’s captains page. (live, secondary) | Use only to verify a claim a person makes, one profile at a time | Low | Public |
| **Credly public badges** | People: certifications and badges with issuer, dates, expiry and skill tags | `credly.com/users/<slug>/badges.json` answers without auth (undocumented); single badge pages (`credly.com/badges/<uuid>`) are public HTML with the badge name, issuer and description; robots.txt disallows only `/talent-match`; terms could not be found. (live) | The Bright Data LinkedIn records already hold 273 Credly badge URLs from people’s own certification lists, so those link exactly; user profiles only when listed (2 in the kb) | Medium through LinkedIn certifications; low otherwise | Earners choose what is public; adds skills and expiry to certifications the kb already has, so the gain is small |
| **Hacktoberfest and similar** | No public participant directory was found | n/a | n/a | n/a | n/a |

### Identity Hubs

| Source | Provides (people; conference) | Access, price, limits, terms | Linking to a kb person | Coverage | Privacy |
| --- | --- | --- | --- | --- | --- |
| **Keybase** | People: cryptographic proofs tying GitHub, X, Reddit, Hacker News accounts and domains to one identity | `keybase.io/_/api/1.0/user/lookup.json?github=<login>` (also `twitter=`, `hackernews=`, `domain=`); one login per request; free, no key; still answering on 2026-10-24, though the service has seen little development since Zoom bought it in 2020. (docs, live) | Proofs are strong evidence | Medium as a crosswalk: 27 of 187 GitHub users have a Keybase GitHub proof | Skip public keys: their user IDs often contain emails |
| **Gravatar REST API v3** | People: display name, job title, company, location, up to 4 verified accounts without a key | `GET /profiles/{slug or SHA-256 email hash}`; 100 requests an hour unauthenticated, 1,000 with a free key; links and interests need a key. (docs) | Only a Gravatar slug the person lists | Low | Never hash email addresses to look people up |
| **Wikidata and Wikipedia** | People: employer (P108), awards (P166), notable work (P800), and identifiers: GitHub username (P2037), X username (P2002), ORCID (P496), Mastodon address (P4033) | SPARQL, REST and entity JSON; CC0; send a descriptive User-Agent and back off on 429. Wikipedia REST page summaries. (docs, live) | Item whose GitHub or X identifier equals a kb account; e.g. Thomas Dohmke is Q109414016 | Low to medium (executives, founders, well-known engineers) | Public, but avoid personal-life properties (spouse, birthplace) |
| **Linktree, about.me, Bento** | Link-in-bio pages | Linktree and about.me terms forbid scraping; Bento, which Linktree bought, announced its shutdown for 2026-02-13. (docs, secondary) | n/a | n/a | See the do-not-use list |

### More GitHub

| Source | Provides (people; conference) | Access, price, limits, terms | Linking to a kb person | Coverage | Privacy |
| --- | --- | --- | --- | --- | --- |
| **GitHub GraphQL, unused part** | People: starred repositories with topics (interests; the kb stores only the count), user star `lists` (curated interests), `sponsoring`, `sponsors`, `sponsorsListing`, `repositoryDiscussions`, `gists`, `contributionsCollection(from:, to:)` with `contributionYears` for history before the last year, and the program flags above | The kb’s existing token and client. GitHub’s Acceptable Use Policies (section 7) treat API collection as distinct from scraping and forbid spam and selling personal information; section 8 limits personal information to the purpose the user authorized. (docs, live) | Exact | High: 41 of 187 have star lists, 85 started discussions, 125 have 10 or more contribution years | Only public sponsorships are visible; do not infer private ones. Sponsorship amounts are financial details and stay out. Organization memberships are already read (public ones only) |
| **GitHub REST events API** | People: recent public activity | `GET /users/{username}/events/public`: “only events from the past 30 days”, up to 300. (docs) | Exact | High but shallow | Push payloads can carry commit emails: drop them |
| **GH Archive and its BigQuery dataset** | People: full public event history since 2011-02-12 (pushes, pull requests, issues, reviews, releases) to compute long-run contribution profiles | Hourly JSON files at `data.gharchive.org` or BigQuery `githubarchive` (year, month, day tables), queried in your own project; 1 TiB a month free. (docs) | `actor.login` and `actor.id` equal the kb account | High | Payloads include commit author emails: never select them |
| **Employer history (`cncf/gitdm`)** | People: GitHub login to employer with date ranges (“PerkinElmer Inc. until 2014-08-01”) | Raw text files in a public repository, updated about monthly; used by CNCF DevStats. (live) | Exact GitHub login | Medium for cloud-native contributors | Lines include email addresses: strip them on read |
| **Package maintainer lookups** | People: everything a person publishes, not just packages in their top 5 repositories. npm `/-/v1/search?text=maintainer:<user>`; crates.io `/api/v1/users/<github-login>` (accounts are GitHub OAuth) and crates by `user_id`; ecosyste.ms packages by maintainer, repositories by owner, a GitHub Sponsors index and a papers index | npm search: public. crates.io: at most 1 request a second with a User-Agent, or the database dump. ecosyste.ms: free, data CC BY-SA 4.0, 5,000 requests an hour anonymous (observed headers), commercial licences offered. (docs, live) | crates.io by GitHub login is exact; npm usernames differ from GitHub logins, so accept a package only when its repository URL names a kb repository | Medium overall; crates.io alone is low (10 of 187 have accounts, 5 own a crate) | ecosyste.ms maintainer records include emails: drop them |
| **Hugging Face Hub API** | People: models, datasets, Spaces, papers, organizations (`/api/users/<user>/overview`, `/api/models?author=`) | Public reads, free; tokens optional. (docs, live) | Only a Hugging Face username the person lists (2 in the kb) or a profile that links their GitHub | Low to medium, rising with AI-focused speakers | Public |
| **GitLab, Codeberg, Open Collective** | People: projects on other forges; collectives and contributions | GitLab `/api/v4/users?username=` public; Open Collective GraphQL v2 answers public queries without a token. (live) | Listed accounts, or social links on the profile that name the kb GitHub account | Low | Public |

### Companies

| Source | Provides (people; conference) | Access, price, limits, terms | Linking to a kb person | Coverage | Privacy |
| --- | --- | --- | --- | --- | --- |
| **SEC EDGAR** | Organizations: filings, financial facts. People: officers and directors in proxy statements and Forms 3, 4 and 5 | `data.sec.gov` submissions and company-facts APIs; no key; free; at most 10 requests a second; bulk ZIPs nightly. (docs) | Company by ticker or CIK; people only by name plus role plus company | Low (executives of public sponsors) | Use roles only; skip holdings and transaction details |
| **OpenCorporates** | Organizations: legal entities, officers, filings | API plans from £2,250 a year (500 calls a month, 200 a day); data is offered as share-alike open data or under a commercial licence; the site has sections for public-benefit, NGO, journalism and academic users, whose terms were not checked. (docs) | Organization by name plus jurisdiction | Organization-level only | Officer records can include home addresses: avoid people data |
| **Crunchbase** | Organizations: funding, people, investments | Basic API discontinued (“no longer offering”, no new keys); paid packages through sales; attribution required. (docs) | n/a | Organization-level | Only if purchased; never scrape |
| **Careers pages via ATS APIs** | Organizations: open roles, departments, offices (hiring areas and technology stack) | Greenhouse Job Board API: GET endpoints need no auth (`boards-api.greenhouse.io/v1/boards/<token>/jobs`); Lever and Ashby have similar public posting endpoints. (docs) | Organization only | Medium for sponsors | No people data |

### Side Events

| Source | Provides (people; conference) | Access, price, limits, terms | Linking to a kb person | Coverage | Privacy |
| --- | --- | --- | --- | --- | --- |
| **Sponsor and partner event pages** | Conference: side events around Universe week, e.g. Cloudsmith’s “Universe Git-Together” on 2026-10-28 and Sentry x Syntax in the Festival Pavilion | The kb already fetches organization homepages; follow their events pages and read schema.org `Event` JSON-LD. (live) | Hosts by organization | Medium | Public |
| **Meetup** | Conference: meetups in San Francisco during Universe week | GraphQL `api.meetup.com/gql-ext`; OAuth; only Meetup Pro subscribers can create OAuth consumers; 500 points per 60 seconds; `eventSearch` and `groupSearch`. (docs, secondary) | Organizers by name plus group | Low to medium | No RSVP or member lists |
| **Eventbrite** | Conference: events by known organizer or venue | Public event search “was shut down” on 2019-12-12; only by event, organization or venue ID; private token. (docs) | Organization IDs | Low | No attendee data |

## Top 15 for This Knowledge Base

Ranked by value for the kb’s goals (interests, past work, recordings), then by link
precision, coverage and cost.

1. **GitHub GraphQL, unused fields.** Star lists, starred topics, Sponsors, discussions,
   older contribution years and the Star, Campus Expert and employee flags, for 187
   users at no new cost and with exact links.
2. **YouTube Data API for GitHub’s Universe playlists.** The only route to 2023–2025
   session recordings; match videos to sessions by title, but refresh within 30 days and
   expect no transcripts.
3. **Wayback CDX for githubuniverse.com 2015–2022.** Recovers every pre-2023 edition,
   including 2022 from its archived JavaScript bundle and 2021 from Swoogo pages.
4. **Sessionize public profiles.** Dated lists of past talks and events with topics,
   accepted only when the profile links a kb account.
5. **GitHub blog and changelog.** Writing by the roughly 210 GitHub-affiliated people,
   linked by GitHub login through the co-author taxonomy, plus Universe announcement
   posts.
6. **DEV API plus Medium, Substack and Hashnode RSS.** Writing history and self-chosen
   tags; DEV links 36 of 187 GitHub users by `github_username`, the rest come from feed
   URLs people list.
7. **Bluesky author feeds and starter packs.** Current interests for 47 active accounts
   and community curation by 12; Mastodon featured tags add a few more.
8. **Wayback for Lanyrd profiles.** Speaking history from 2010 to 2018 keyed by the X
   handles the kb already holds.
9. **GitHub Stars profiles.** Dated talks, videos, podcasts, posts and events for the 8
   current Stars.
10. **Podcast appearances.** Podcast Index for discovery, show RSS feeds (including The
    GitHub Podcast) for the stored record.
11. **Recognition rosters as open data.** CNCF `people.json` and the Java Champions YAML
    link by GitHub login; MVP profiles verify claims.
12. **Package maintainer lookups.** npm maintainer search, crates.io by GitHub login and
    ecosyste.ms show all published work, not just the top repositories.
13. **Notist and Speaker Deck.** Slides with event names; Notist links by its `github`
    field.
14. **Wikidata.** An identifier crosswalk (GitHub, X, ORCID, Mastodon) plus employers
    and awards for executives and well-known engineers.
15. **OpenAlex with ORCID.** Publications for the researchers among the speakers, linked
    through ORCID iDs rather than names.

Runners-up: Keybase proofs (an identity crosswalk for 27 of 187 GitHub users, which
speeds up linking for everything above), GH Archive (long-run contribution profiles, but
heavy), Hugging Face Hub (AI work), Stack Exchange top tags, `cncf/gitdm` employer
history, Google Patents on BigQuery, and sponsor pages for side events.

## Do Not Use

- **People-search and background-check sites:** Spokeo, Whitepages, BeenVerified,
  Intelius, PeopleFinders, TruePeopleSearch, FastPeopleSearch, Radaris, Pipl.
  They sell home addresses, phone numbers, relatives and records unrelated to
  professional life, and their use for decisions about people falls under consumer
  reporting law.
- **Contact and email harvesting:** Hunter.io, RocketReach, Apollo.io, ZoomInfo, Lusha,
  ContactOut, SignalHire, HubSpot (Clearbit) enrichment, and Podchaser’s “Contacts”
  product. The kb has no use for contact details, and GitHub’s Acceptable Use Policies
  forbid using its data for spam or selling it to recruiters.
- **Emails inside otherwise useful data:** commit author emails in GitHub events, GH
  Archive and `.patch` URLs; the email field in ecosyste.ms maintainer records;
  addresses in `cncf/gitdm`; user IDs on Keybase public keys; Gravatar lookups by email
  hash. Drop them on read and never compute hashes from emails.
- **Spotify Web API:** the Developer Terms forbid storing or compiling “databases of
  Spotify Content” and using it to train or feed AI models; extended quota is only for
  organizations with 250,000 monthly active users.
- **Linktree and about.me:** their terms forbid scraping or crawling profiles; Bento
  announced its shutdown for February 2026.
- **Discord and Slack:** Discord’s Developer Policy forbids using API data to “profile
  Discord users”; Slack’s API terms forbid persistent copies or indexes of workspace
  data; both need joining the community.
- **Reddit Data API:** approval-gated since late 2025, non-commercial free tier, and
  data must be deleted once outside the approved use; only 3 kb accounts.
- **Listen Notes (free and Pro):** no server-side storage except IDs and dates.
- **Google Scholar and ResearchGate:** no API; Scholar’s robots.txt disallows `/scholar`
  searches and its CAPTCHAs block automated access, which must not be bypassed.
  Use OpenAlex, Semantic Scholar, ORCID or dblp instead.
- **YouTube downloads and unofficial caption endpoints:** downloading videos to
  transcribe them, or reading the web player’s caption track, breaks Developer Policies
  III.E.1 and III.E.6.
- **Undocumented internal APIs:** the Microsoft MVP backend, RainFocus endpoints for
  logged-in features, and similar; use the public pages instead.
- **Crunchbase without a licence:** scraping it is prohibited, and the free Basic API
  has ended.
- **Private or semi-private data:** the logged-in Universe attendee directory, event
  guest lists, Meetup RSVPs and member lists, non-public Discord or Slack channels,
  Sessionize contact forms, private sponsorships, and follower or following graphs
  beyond counts.
- **Sensitive fields in open data:** country of birth and citizenship in the Java
  Champions YAML, coordinates in Notist profiles, home addresses in patents or company
  registries, and personal-life properties in Wikidata.

## Surprising Finds

- **The 2022 edition is recoverable.** githubuniverse.com/2022 was a JavaScript app, but
  the Wayback capture of its 2.7 MB bundle embeds about 112 titles and speaker social
  links; 2021 lives on archived Swoogo session pages; 2015–2020 have plain speaker and
  session pages.
- **Lanyrd lives on in the Wayback Machine,** keyed by Twitter handle, so the kb’s 290 X
  handles unlock 2010–2018 speaking histories.
- **GitHub exposes program flags in GraphQL.** `isGitHubStar`, `isCampusExpert` and
  `isEmployee` would replace bio-text parsing for those recognitions; 82 of 187 users
  are GitHub employees by this flag.
- **GitHub blog co-authors are GitHub logins,** which makes blog authorship an exact
  join.
- **Keybase is still useful:** 27 of the kb’s 187 GitHub users have a Keybase proof,
  which ties their GitHub account to X, Hacker News, Reddit and domains with
  cryptographic evidence.
- **Sessionize profiles carry dated event histories,** and GitHub Stars profiles carry
  typed, dated contribution logs.
- **Several APIs changed recently:** Hashnode’s GraphQL API went paid on 2026-05-13;
  PatentsView’s API has been paused since 2026-03-20; dblp’s API now sits behind an
  Anubis bot check; Crunchbase ended its Basic API; the GitHub events API covers only 30
  days; Spotify’s extended quota is limited to large organizations; Bento announced its
  shutdown.
- **Terms that bite:** YouTube API data must be refreshed or deleted within 30 days, and
  Podcast Index forbids permanent copies, so both suit discovery better than storage.
- **CNCF publishes its whole people roster as MIT-licensed JSON** (5,635 people, 3,551
  with GitHub logins), and `cncf/gitdm` publishes dated employer histories by GitHub
  login.
- **Speaker Deck’s robots.txt disallows the Atom feeds it publishes,** and Medium’s
  robots.txt blocks AI crawlers site-wide.

## Documentation Relied On

**Talks, video and slides**

- YouTube: https://developers.google.com/youtube/v3/getting-started,
  https://developers.google.com/youtube/v3/docs/captions/list,
  https://developers.google.com/youtube/v3/docs/captions/download,
  https://developers.google.com/youtube/terms/developer-policies, and the @GitHub
  playlists tab https://www.youtube.com/@GitHub/playlists (viewed once to confirm
  playlist titles)
- Sessionize: https://sessionize.com/playbook/api,
  https://sessionize.com/terms-of-service, https://sessionize.com/robots.txt, sample
  profile https://sessionize.com/david-pereira/
- Speaker Deck: https://speakerdeck.com/robots.txt,
  https://speakerdeck.com/camilamaia.atom
- Notist: https://be.noti.st/2018/update-notes-july-2018,
  https://noti.st/rachelandrew.json
- SlideShare (historical):
  https://webarchive.library.unt.edu/web/20131004154346mp_/http://www.slideshare.net/developers
- Wayback: https://web.archive.org/cdx/search/cdx (queried live),
  https://wayback.readthedocs.io/en/latest/_modules/wayback/_client.html (rate-limit
  note)
- GitHub blog: https://github.blog/wp-json/wp/v2/, https://github.blog/feed/,
  https://github.blog/changelog/feed/, https://github.blog/author/kdaigle/
- Datasets: https://github.com/tech-conferences/conference-data,
  https://github.com/pyvideo/data, https://docs.pretalx.org/api/fundamentals/

**Writing and podcasts**

- DEV: https://developers.forem.com/api/v1
- Hashnode: https://hashnode.com/announcements/graphql-api
- Medium and Substack: https://medium.com/robots.txt, https://substack.com/robots.txt
- Podcast Index: https://github.com/Podcastindex-org/docs-api
  (`api_src/paths/search/byperson.yaml`,
  `api_src/components/securitySchemes/Authorization.yaml`),
  https://github.com/Podcastindex-org/legal/blob/main/TermsOfService.md
- The GitHub Podcast feed: https://feeds.simplecast.com/ioCY0vfY
- Apple: https://performance-partners.apple.com/search-api
- Listen Notes: https://www.listennotes.com/api/pricing/
- Podchaser: https://api-docs.podchaser.com/docs/overview,
  https://www.podchaser.com/api, https://rephonic.com/blog/podchaser-api/ (secondary)
- Spotify: https://developer.spotify.com/documentation/web-api/concepts/quota-modes,
  https://developer.spotify.com/terms

**Q&A and communities**

- Bluesky: `public.api.bsky.app` endpoints tested live (the developer-guidelines page
  did not render)
- Mastodon: instance APIs tested live
- Stack Exchange: https://api.stackexchange.com/docs/throttle,
  https://api.stackexchange.com/docs/top-tags-on-users,
  https://stackoverflow.com/legal/api-terms-of-use
- Hacker News: https://hn.algolia.com/api, https://github.com/HackerNews/API
- Reddit: https://redditinc.com/policies/data-api-terms; Responsible Builder Policy
  reported at
  https://r.datuan.dev/r/redditdev/comments/1oug31u/introducing_the_responsible_builder_policy_new/noc31sg
  (secondary mirror of r/redditdev)
- Product Hunt: https://www.producthunt.com/v2/docs
- Discord:
  https://support-dev.discord.com/hc/en-us/articles/8563934450327-Discord-Developer-Policy
- Slack: https://slack.com/terms-of-service/api

**Research and IP**

- OpenAlex: https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication,
  https://help.openalex.org/access/pricing
- Semantic Scholar: https://www.semanticscholar.org/product/api,
  https://www.semanticscholar.org/product/api/license
- ORCID: https://info.orcid.org/documentation/features/public-api/,
  https://info.orcid.org/public-client-terms-of-service/
- dblp: https://dblp.org/faq/How+to+use+the+dblp+search+API.html (blocked by Anubis),
  https://drops.dagstuhl.de/entities/collection/10.4230/dblp.xml
- Crossref: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- arXiv: https://info.arxiv.org/help/api/tou.html
- Patents:
  https://www.uspto.gov/subscription-center/2026/patentsview-migrating-uspto-open-data-portal-march-20,
  https://cloud.google.com/bigquery/pricing,
  https://docs.cloud.google.com/bigquery/public-data
- Books: https://openlibrary.org/developers/api,
  https://developers.google.com/books/docs/v1/using

**Recognition and identity**

- GitHub Stars: https://stars.github.com/profiles/,
  https://stars.github.com/profiles/frenck/
- CNCF: https://github.com/cncf/people; Java Champions:
  https://github.com/aalmiray/java-champions
- Microsoft MVP: https://mvp.microsoft.com/robots.txt,
  https://mvp.microsoft.com/en-US/search
- GDE: https://developers.google.com/community/experts/directory; AWS Heroes:
  https://aws.amazon.com/developer/community/heroes/; Docker Captains:
  https://www.docker.com/community/captains/
- Credly: https://www.credly.com/robots.txt
- Keybase: https://keybase.io/docs/api/1.0/call/user/lookup
- Gravatar: https://docs.gravatar.com/api/profiles/rest-api/
- Wikidata: https://www.wikidata.org/wiki/Wikidata:Data_access
- Linktree: https://linktr.ee/s/terms; about.me: https://about.me/legal/terms; Bento:
  https://alternativeto.net/news/2025/12/bento-to-shut-down-in-2026-as-linktree-takes-over-and-offers-migration-path/
  (secondary)

**GitHub and open source**

- GitHub: https://docs.github.com/en/graphql/reference/users,
  https://docs.github.com/en/rest/activity/events,
  https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies
- GH Archive: https://www.gharchive.org/
- gitdm: https://github.com/cncf/gitdm
- crates.io data access policy:
  https://github.com/rust-lang/crates.io/blob/main/svelte/src/routes/data-access/+page.svelte
  (source of https://crates.io/data-access)
- ecosyste.ms: https://ecosyste.ms/
- Hugging Face: https://huggingface.co/docs/hub/api

**Companies and side events**

- SEC: https://www.sec.gov/search-filings/edgar-application-programming-interfaces,
  https://www.sec.gov/about/developer-resources
- OpenCorporates: https://api.opencorporates.com/, https://opencorporates.com/pricing/
- Crunchbase: https://data.crunchbase.com/docs/crunchbase-basic.md,
  https://data.crunchbase.com/docs/api-packages-overview.md
- Greenhouse: https://docs.greenhouse.io/job-board.html
- Meetup: https://www.meetup.com/api/guide/,
  https://help.meetup.com/hc/en-us/articles/41454853218317-Which-API-authentication-should-I-choose
- Eventbrite: https://www.eventbrite.com/platform/api
- Side events: https://cloudsmith.com/events/in-person-events/github-universe-2026,
  https://sentry.io/events/github-universe-2026/

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
