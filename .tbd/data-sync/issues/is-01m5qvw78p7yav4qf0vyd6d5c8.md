---
type: is
id: is-01m5qvw78p7yav4qf0vyd6d5c8
title: "PR #5 Qodo 8 (https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488171): research says every record cites a snapshot file, but its own examples cite a post URL or a curation file"
kind: bug
status: closed
priority: 2
version: 4
delegate: claude-code@spud10.local
labels: []
dependencies: []
parent_id: is-01m5qvvbg15jk7fs2w0tbxdcds
hold: null
hold_until: null
created_at: 2026-10-24T21:08:12.693Z
updated_at: 2026-10-24T21:13:49.713Z
started_at: 2026-10-24T21:08:24.864Z
closed_at: 2026-10-24T21:13:49.712Z
close_reason: "Disposition: fixed (as suggested; also applied to the architecture doc, which had the same blanket claim). Commit 'docs: state the provenance contract instead of a blanket snapshot claim'. research-2026-10-23-universe-knowledge-graph.md and arch-2026-10-24-conference-kb.md now say a record built from a saved response cites that snapshot file, curated facts cite the curation file, and a source with neither (such as an attendee's own X post) is cited by its URL or record ID; the 'Every entity cites its sources' bullets in both say the raw/ snapshot path where there is one. Confirmed by grep (no 'every knowledge base/KB record cites the snapshot' left in docs/) and flowmark -w 88 -s --smartquotes --check (pass)."
resolution: null
duplicate_of: null
---
Severity: Medium (Qodo: Remediation recommended; Bug, Correctness). Review: https://github.com/jlevy/universe2026-md/pull/5#pullrequestreview-5639988396. PR: jlevy/universe2026-md#5. Comment: https://github.com/jlevy/universe2026-md/pull/5#discussion_r4368488171. Files: docs/project/research/research-2026-10-23-universe-knowledge-graph.md:145-147 (every knowledge base record cites the snapshot file it came from) and :1478-1485 (attendee example: an X source with a record ID and no snapshot); the same blanket claim is in docs/project/architecture/arch-2026-10-24-conference-kb.md:105-107, while :152-155 and the research's :379-382 allow the curation file for curated facts. Finding: a consumer cannot rely on the blanket statement to find every record's raw input. Qodo's suggested fix: state the actual provenance contract: raw snapshots where available, URL or record-ID evidence, and curation files.

## Notes

Disposition: fixed (as suggested; also applied to the architecture doc, which had the same blanket claim). Commit 'docs: state the provenance contract instead of a blanket snapshot claim'. research-2026-10-23-universe-knowledge-graph.md and arch-2026-10-24-conference-kb.md now say a record built from a saved response cites that snapshot file, curated facts cite the curation file, and a source with neither (such as an attendee's own X post) is cited by its URL or record ID; the 'Every entity cites its sources' bullets in both say the raw/ snapshot path where there is one. Confirmed by grep (no 'every knowledge base/KB record cites the snapshot' left in docs/) and flowmark -w 88 -s --smartquotes --check (pass).
