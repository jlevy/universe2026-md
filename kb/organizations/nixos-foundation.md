---
title: NixOS Foundation
softschema:
  contract: paraverse.conference:Organization/v1
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: permissive
organization:
  id: org:nixos-foundation
  name: NixOS Foundation
  roles:
  - affiliation
  description: 'The mission of the foundation is to support the Nix ecosystem''s infrastructure, and projects
    implementing the purely functional deployment model. In particular, the foundation supports Nix, Nixpkgs,
    NixOS, and operates: cache.nixos.org - the NixOS binary cache, containing over 120TB of prebuilt Nix
    packages. hydra.nixos.org - a Nix build farm, consisting of hundreds of macOS, x86-64 (Linux) and
    aarch64 (Linux) build cores. Hydra executes over 350,000 builds each week. The NixOS Foundation is
    a registered non-profit organisation at the Chamber of commerce (Kamer van Koophandel) in Utrecht,
    The Netherlands. The KvK number is 63520583. You can contact the foundation by writing an email to
    [email removed].'
  descriptions:
  - text: 'The mission of the foundation is to support the Nix ecosystem''s infrastructure, and projects
      implementing the purely functional deployment model. In particular, the foundation supports Nix,
      Nixpkgs, NixOS, and operates: cache.nixos.org - the NixOS binary cache, containing over 120TB of
      prebuilt Nix packages. hydra.nixos.org - a Nix build farm, consisting of hundreds of macOS, x86-64
      (Linux) and aarch64 (Linux) build cores. Hydra executes over 350,000 builds each week. The NixOS
      Foundation is a registered non-profit organisation at the Chamber of commerce (Kamer van Koophandel)
      in Utrecht, The Netherlands. The KvK number is 63520583. You can contact the foundation by writing
      an email to [email removed].'
    basis: linkedin
  industry: IT Services and IT Consulting
  size: 'LinkedIn size range: 2-10 employees'
  headquarters: Utrecht
  logo_url: https://media.licdn.com/dms/image/v2/D4D0BAQEtP185dtGnZg/company-logo_200_200/B4DZc27eGAHAAI-/0/1748973249768/nixos_foundation_logo?e=2147483647&v=beta&t=c0zBEr747OID5rFWkqyydlFsHXQLnYD0Ti8bIDa-alo
  website: https://nixos.org/
  accounts:
  - acct:linkedin/company/nixos-foundation
  locations:
  - Utrecht, NL
  updates:
  - text: 'cargo (libnix) is a fork of cargo with nix built in as a build backend. three releases later
      🦀❄️ here is what changed between libnix-1.87.0+v1 and +v3: 🔌 talking to the nix-daemon directly:
      cargo no longer runs nix build as a subprocess. it speaks the nix worker protocol, so it knows exactly
      which crate failed, which ones were skipped and which ones came from a binary cache. 📋 build output
      that reads like cargo: the log renderer is now part of cargo. it prints Compiling / Downloading
      lines, rustc diagnostics, build logs for failed crates, a correct progress line and the evaluation
      time. ⚡ parallel builds again: build script flags are no longer read at evaluation time, so nix
      schedules independent crates in parallel. 📦 crates live in the nix store: in nix mode cargo never
      downloads a crate itself. the nix-daemon fetches them once (or substitutes them from cache.nixos.org
      ), and cargo and the nix build share the same store paths. ~/.cargo/registry stays empty. 🧊 flakes
      via IFD, no vendoring: cargo build write-nix-buildsystem --out-dir generates the build system from
      the local source. for offline builds the crates.io index is no longer needed: the crate tarballs
      are computed from Cargo.lock in plain nix and passed in as inputs. no network, no importCargoLock.
      🛠️ smaller things: nixpkgs 26.05, cargo --version says +libnix, nix develop works better, and there
      are clearer safety checks. it''s still slower than vanilla cargo, but sandboxed, shared and cached
      builds plus readable logs make it a pleasant way to build rust with nix. 👉 https://lnkd.in/eDrbN4df
      #nix #rust #cargo #opensource'
    date: '2026-10-16T08:52:58Z'
    url: https://www.linkedin.com/posts/activity-7515050016684523520-Oyi1
    likes: 156
  - text: We’re proud to sponsor NixCon 2026! Nix has moved well beyond being a powerful tool for individual
      developers and has become core infrastructure for companies that need software to be reproducible,
      secure, and reliable everywhere it runs. At Determinate Systems, we’re building the platform enterprises
      need to adopt Nix with confidence. See you in Kraków.
    date: '2026-09-25T10:59:16Z'
    url: https://www.linkedin.com/posts/activity-7508873514540593153-LsOL
    likes: 42
  - text: 'Coming to NixCon this week? 🙂↕️ We (read: our CTO, Akshay) are running a session on the first
      hack day, Friday the 25th at 2 pm on reproducible infra with Nix and SSH and how you can manage
      your infra too 🛠️ Look for the sheep t-shirts 🐑 or ping us here on Friday, and we''ll tell you where
      we''ve landed!'
    date: '2026-09-23T10:06:11Z'
    url: https://www.linkedin.com/posts/activity-7507755174321438722-IEYf
    likes: 32
  - text: 'We''re happy to announce that Tweag by Modus Create is sponsoring #nixcon 2026 as Silver Sponsor.
      Thank you for your support! https://www.tweag.io/'
    date: '2026-09-21T13:45:22Z'
    url: https://www.linkedin.com/posts/nixos-foundation_tweag-software-innovation-lab-activity-7507797122730156032-rotw
    likes: 35
  - text: 'We''re happy to announce that PDT Partners is sponsoring #nixcon 2026 as Gold Sponsor. Thank
      you for your support! https://pdtpartners.com/'
    date: '2026-09-21T11:13:54Z'
    url: https://www.linkedin.com/posts/nixos-foundation_pdt-partners-activity-7507759008166932480-XNML
    likes: 11
  people:
  - person:ron-efroni
  sources:
  - system: rainfocus
    url: https://events.githubuniverse.com/api/sessions
    record_id: 1686069111593001ys0A
    retrieved_at: '2026-10-24T06:46:25Z'
    snapshot: raw/rainfocus/sessions.json
  - system: brightdata
    url: https://www.linkedin.com/in/ronefroni
    record_id: sd_mvm4ih2s1a5o48n7e
    retrieved_at: '2026-10-24T08:51:28Z'
    snapshot: raw/brightdata/linkedin_profiles.json
  - system: brightdata
    url: https://www.linkedin.com/company/nixos-foundation
    record_id: sd_mvm5xmem1d1puu9zcg
    retrieved_at: '2026-10-24T08:56:11Z'
    snapshot: raw/brightdata/linkedin_companies.json
---
# NixOS Foundation

Website: <https://nixos.org/>

## People

- [Ron Efroni](../people/ron-efroni.md)
