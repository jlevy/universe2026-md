---
type: is
id: is-01m5qvqz78z0vsp7d5vm0rd34h
title: "Address PR #1 review qodo-5639981352: tbd-generated hook and skill issues"
kind: task
status: in_progress
priority: 1
version: 7
delegate: claude-code@spud10.local
labels: []
dependencies: []
child_order_hints:
  - is-01m5qvsga8rfwkc1ysmybhjhmk
  - is-01m5qvsgw2y9hm7mtw8whm4cka
  - is-01m5qvshd90nrkkzwm2q0yeadk
  - is-01m5qvshx9dw945g3zz3gwypze
  - is-01m5qvsjcm03ze89aheq2yvrxj
hold: null
hold_until: null
created_at: 2026-10-24T21:05:53.382Z
updated_at: 2026-10-24T21:06:52.210Z
started_at: 2026-10-24T21:06:52.208Z
---
Address the Qodo review on jlevy/universe2026-md#1 (setup/tbd), pinned head 6d1b7eb46a3398291ced91c3d3a275b07a1d594e. Review (unmarked): https://github.com/jlevy/universe2026-md/pull/1#pullrequestreview-5639981352 ; summary comment https://github.com/jlevy/universe2026-md/pull/1#issuecomment-6389408470 . Five Medium findings, all in files written verbatim by tbd setup 0.10.0 (.claude/, .codex/, .agents/skills/tbd/). tbd setup rewrites these files and its own hook entries, so fixes belong in tbd's templates upstream (github.com/jlevy/tbd); none is a project setting. Related work bead: u26-c5v5. Counterpart review on jlevy/paraverse#1 covers findings 1, 2 and 4 with the same files.
