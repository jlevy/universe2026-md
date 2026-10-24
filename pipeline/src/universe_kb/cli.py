"""
`universe-kb`: crawl, enrich, build and validate the GitHub Universe knowledge base.

Run from `pipeline/` with `uv run universe-kb <command>`. The knowledge base is written
to the repository's `kb/` unless `--kb` names another directory. Data goes to stdout as
JSON; progress goes to stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

PIPELINE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = PIPELINE_DIR / "raw"
# The built knowledge base sits beside the pipeline, at the repository root.
KB_DIR = PIPELINE_DIR.parent / "kb"
SCHEMA_DIR = PIPELINE_DIR / "schemas"
CURATION_DIR = PIPELINE_DIR / "curation"
SYNTHESIS_DIR = PIPELINE_DIR / "synthesis"


def cmd_crawl(args: argparse.Namespace) -> int:
    from universe_kb.crawl import crawl
    from universe_kb.snapshot import Fetcher, Snapshot

    crawl(Snapshot(args.raw), Fetcher(delay=args.delay))
    return 0


def cmd_crawl_editions(args: argparse.Namespace) -> int:
    from universe_kb.crawl import crawl_past_editions
    from universe_kb.snapshot import Fetcher, Snapshot

    counts = crawl_past_editions(Snapshot(args.raw), Fetcher(delay=args.delay))
    print(json.dumps(counts, indent=2))
    return 0


def cmd_enrich(args: argparse.Namespace) -> int:
    from universe_kb.enrich import enrich
    from universe_kb.snapshot import Fetcher, Snapshot

    report = enrich(Snapshot(args.raw), Fetcher(delay=args.delay), CURATION_DIR)
    print(json.dumps(report, indent=2))
    return 0


def cmd_enrich_social(args: argparse.Namespace) -> int:
    from universe_kb.enrich import enrich_social
    from universe_kb.snapshot import Fetcher, Snapshot

    report = enrich_social(Snapshot(args.raw), Fetcher(delay=args.delay), CURATION_DIR, args.kb,
                           steps=tuple(args.steps.split(",")))
    print(json.dumps(report, indent=2))
    return 0


def cmd_enrich_brightdata(args: argparse.Namespace) -> int:
    from universe_kb.brightdata import (
        BrightData,
        collect_to_snapshot,
        kb_profile_urls,
        load_api_key,
    )
    from universe_kb.people import social_account_id
    from universe_kb.policy import Exclusions
    from universe_kb.snapshot import Fetcher, Snapshot
    from universe_kb.web import classify_social_url

    client = BrightData(Fetcher(delay=args.delay), load_api_key(PIPELINE_DIR))
    snapshot = Snapshot(args.raw)
    report: dict[str, object] = {}
    plans = {
        "linkedin_profiles": ("linkedin", "person", {}),
        "x_profiles": ("x", "person", {}),
        "linkedin_companies": ("linkedin", "org", {}),
    }
    removed = Exclusions.load(CURATION_DIR)
    for dataset in args.datasets.split(","):
        platform, owner_kind, params = plans[dataset]
        urls = [u for u in kb_profile_urls(args.kb, platform, owner_kind)
                if (c := classify_social_url(u)) is None
                or not removed.matches(social_account_id(*c))]
        report[dataset] = collect_to_snapshot(client, snapshot, dataset, urls, **params)
    print(json.dumps(report, indent=2))
    return 0


def cmd_sanitize_raw(args: argparse.Namespace) -> int:
    """Reapply the data policy to every saved raw file, keeping its provenance."""
    from universe_kb.snapshot import Snapshot

    snapshot = Snapshot(args.raw)
    changed = []
    for rel in sorted(snapshot.entries):
        if not snapshot.has(rel):
            continue
        if rel.endswith(".json"):
            rewritten = snapshot.rewrite_json(rel, snapshot.load_json(rel))
        else:
            rewritten = snapshot.rewrite_text(rel, (snapshot.root / rel).read_text())
        if rewritten:
            changed.append(rel)
    snapshot.write_manifest()
    print(json.dumps({"files": len(snapshot.entries), "changed": changed}, indent=2))
    return 0


def cmd_enrich_packages(args: argparse.Namespace) -> int:
    from universe_kb.enrich import enrich_packages
    from universe_kb.snapshot import Fetcher, Snapshot

    report = enrich_packages(Snapshot(args.raw), Fetcher(delay=args.delay), args.kb)
    print(json.dumps(report, indent=2))
    return 0


def cmd_refresh_repos(args: argparse.Namespace) -> int:
    from universe_kb.enrich import GitHubClient, refresh_repositories
    from universe_kb.snapshot import Fetcher, Snapshot

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("refresh-repos needs GITHUB_TOKEN; try GITHUB_TOKEN=$(gh auth token)")
    github = GitHubClient(Fetcher(delay=args.delay), token)
    report = refresh_repositories(Snapshot(args.raw), github, args.kb,
                                  max_age_hours=args.max_age_hours)
    print(json.dumps(report, indent=2))
    return 0


def cmd_bio_bundles(args: argparse.Namespace) -> int:
    """Write evidence bundles for people whose bio is missing or stale, in batches."""
    from universe_kb.bios import bundle_hash, load_bios, load_kb_payloads, prune_bios
    from universe_kb.build import bundles_from
    from universe_kb.publication import publish_directory

    payloads = load_kb_payloads(args.kb)
    pruned = prune_bios(SYNTHESIS_DIR,
                        {k for k in payloads if k.startswith("person:")})
    written = load_bios(SYNTHESIS_DIR / "brief-bios.yaml")
    todo = []
    for person_id, bundle in sorted(bundles_from(payloads).items()):
        events = {p["event"] for p in payloads[person_id].get("participations") or []}
        if args.event and args.event not in events:
            continue
        digest = bundle_hash(bundle)
        if args.all or written.get(person_id, {}).get("input_sha256") != digest:
            todo.append({**bundle, "input_sha256": digest})
    out = SYNTHESIS_DIR / "bundles"
    out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".bio-bundles-", dir=out.parent) as temporary:
        staging = Path(temporary)
        for start in range(0, len(todo), args.batch):
            batch = todo[start: start + args.batch]
            path = staging / f"batch-{start // args.batch + 1:02d}.jsonl"
            path.write_text("".join(json.dumps(b, ensure_ascii=False) + "\n" for b in batch))
        publish_directory(staging, out)
    print(json.dumps({"people": len(payloads and bundles_from(payloads)), "pruned": pruned,
                      "to_write": len(todo),
                      "batches": (len(todo) + args.batch - 1) // args.batch}, indent=2))
    return 0


def cmd_bios_check(args: argparse.Namespace) -> int:
    from universe_kb.bios import check_file

    report = check_file(SYNTHESIS_DIR, args.file)
    print(json.dumps(report, indent=2))
    return 0 if not report["problems"] else 1


def cmd_bios_merge(args: argparse.Namespace) -> int:
    from universe_kb.bios import merge_bios

    report = merge_bios(SYNTHESIS_DIR)
    print(json.dumps(report, indent=2))
    return 1 if report["rejected"] else 0


def cmd_scrub(args: argparse.Namespace) -> int:
    """
    Delete the raw data and bios of people listed under `exclude` in curation. Run it
    before the next build, while the knowledge base still lists their accounts.
    """
    from universe_kb.bios import drop_bios, load_bios, load_kb_payloads
    from universe_kb.policy import Exclusions, forget_raw
    from universe_kb.snapshot import Snapshot

    exclusions = Exclusions.load(CURATION_DIR)
    payloads = load_kb_payloads(args.kb) if args.kb.exists() else {}
    removed = set()
    for person_id, person in payloads.items():
        if not person_id.startswith("person:"):
            continue
        keys = {*(person.get("accounts") or []), *(person.get("websites") or [])}
        if exclusions.covers(person_id, keys | {person.get("github") or ""}):
            removed.add(person_id)
            exclusions.add_keys(keys)
    removed.update(pid for pid in load_bios(SYNTHESIS_DIR / "brief-bios.yaml")
                   if exclusions.matches(pid))
    snapshot = Snapshot(args.raw)
    report: dict[str, object] = {"raw": forget_raw(snapshot, exclusions)}
    snapshot.write_manifest()
    report["bios"] = len(drop_bios(SYNTHESIS_DIR, removed))
    print(json.dumps(report, indent=2))
    return 0


def cmd_prune_raw(args: argparse.Namespace) -> int:
    """Keep only what the built knowledge base uses from the caches about people."""
    from universe_kb.bios import load_kb_payloads
    from universe_kb.policy import prune_raw
    from universe_kb.snapshot import Snapshot

    snapshot = Snapshot(args.raw)
    report = prune_raw(snapshot, load_kb_payloads(args.kb))
    snapshot.write_manifest()
    print(json.dumps(report, indent=2))
    return 0


def cmd_schemas(args: argparse.Namespace) -> int:
    from universe_kb.schemas import compile_schemas

    drift = compile_schemas(SCHEMA_DIR, check=args.check)
    print(json.dumps({"drift": drift}, indent=2))
    return 1 if args.check and drift else 0


def cmd_build(args: argparse.Namespace) -> int:
    from universe_kb.build import build

    stats = build(args.raw, CURATION_DIR, args.kb, SCHEMA_DIR)
    print(json.dumps(stats, indent=2))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    from universe_kb.schemas import validate_kb

    report = validate_kb(args.kb)
    print(json.dumps(report, indent=2))
    return 0 if report["invalid"] == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="universe-kb", description=__doc__)
    parser.add_argument("--raw", type=Path, default=RAW_DIR, help="Raw snapshot directory.")
    parser.add_argument("--kb", type=Path, default=KB_DIR, help="Knowledge base directory.")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests.")
    parser.add_argument("-v", "--verbose", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("crawl", help="Fetch the official site and portal into raw/.")
    commands.add_parser("crawl-editions",
                        help="Fetch past editions' catalogs into raw/editions/.")
    commands.add_parser("enrich", help="Look up GitHub accounts, repos and packages.")
    social = commands.add_parser(
        "enrich-social", help="Websites, Bluesky, Mastodon, feeds and hashtag timelines.")
    social.add_argument("--steps", default="websites,bluesky,mastodon,feeds,hashtags",
                        help="Comma-separated subset of the steps to run.")
    brightdata = commands.add_parser(
        "enrich-brightdata", help="Collect public LinkedIn and X profiles via Bright Data.")
    brightdata.add_argument("--datasets", default="linkedin_profiles,x_profiles",
                            help="Comma-separated: linkedin_profiles, x_profiles, "
                            "linkedin_companies.")
    bios = commands.add_parser("bio-bundles",
                               help="Write bio evidence bundles for missing or stale bios.")
    bios.add_argument("--batch", type=int, default=100, help="People per batch file.")
    bios.add_argument("--all", action="store_true", help="Include people with current bios.")
    bios.add_argument("--event", help="Only people who take part in this event ID.")
    commands.add_parser("enrich-packages",
                        help="Find and verify packages that people's repositories publish.")
    refresh = commands.add_parser(
        "refresh-repos", help="Read current stars and forks for every kb/ repository.")
    refresh.add_argument("--max-age-hours", type=float, default=12.0,
                         help="Skip repositories read more recently than this; 0 reads all.")
    commands.add_parser("bios-merge", help="Check written bios and merge the good ones.")
    check = commands.add_parser("bios-check", help="Check one file of written bios.")
    check.add_argument("file", type=Path)
    commands.add_parser("sanitize-raw",
                        help="Reapply the data policy to every raw file in place.")
    commands.add_parser("scrub",
                        help="Delete raw data and bios of people excluded in curation.")
    commands.add_parser("prune-raw",
                        help="Keep only what the built kb uses from caches about people.")
    schemas = commands.add_parser("schemas", help="Compile the contracts to schemas/.")
    schemas.add_argument("--check", action="store_true", help="Fail on drift; write nothing.")
    commands.add_parser("build", help="Turn raw/ into softschema artifacts in kb/.")
    commands.add_parser("validate", help="Validate every kb/ artifact against its schema.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    handlers = {"crawl": cmd_crawl, "crawl-editions": cmd_crawl_editions, "enrich": cmd_enrich,
                "enrich-social": cmd_enrich_social, "enrich-brightdata": cmd_enrich_brightdata,
                "bio-bundles": cmd_bio_bundles, "bios-merge": cmd_bios_merge,
                "bios-check": cmd_bios_check, "enrich-packages": cmd_enrich_packages,
                "refresh-repos": cmd_refresh_repos,
                "sanitize-raw": cmd_sanitize_raw, "scrub": cmd_scrub,
                "prune-raw": cmd_prune_raw,
                "schemas": cmd_schemas,
                "build": cmd_build, "validate": cmd_validate}
    try:
        return handlers[args.command](args)
    except KeyboardInterrupt:
        return 130
