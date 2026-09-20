# Hardening: turning tonight's mistakes into commands that fail loudly `[pending]`

One session produced 26 silent-zero greps, 8 moved denominators, 4 lost-file
branch-switches, 4 shaless callbacks, and 4 pipeline exit-status misreads.
Classes we turned into code stopped recurring. Classes we turned into prose
did not. So we built commands for the mechanizable ones and wrote down why
for the rest.

## The measurement that justifies it

```
GATED classes, recurrences     TESTS.md 1 · numerals 0 · readme-counts 3 caught
UNGATED classes                selector/silent-zero 26 · denominator drift 8
```

## The four guards (run them)

- [`scripts/selftest-vgrep.sh`](../../../scripts/selftest-vgrep.sh) — a grep
  that matches nothing exits 3 (inconclusive), never reads as clean. 8 arms.
- [`scripts/selftest-pinned-denominator.sh`](../../../scripts/selftest-pinned-denominator.sh) —
  a claimed count disagreeing with its regeneration command exits 3
  ("the sentence is wrong even though nobody edited it"). 11 arms.
- [`scripts/selftest-denominator-sweep.sh`](../../../scripts/selftest-denominator-sweep.sh) —
  all 8 pinned claims in one pass, plus refusal when copied elsewhere
  (eight false DRIFTs are worse than no report). 3 arms.
- [`scripts/selftest-pin-liveness.sh`](../../../scripts/selftest-pin-liveness.sh) —
  a digest pinned to a file with ≥10 commits in 24h exits 3. Non-author
  reviewed, fires both directions.

## The three refusals (why no guard, and what would change that)

- **R46 staged-file loss on branch-switch** — git has no pre-checkout hook
  (verified from the git binary); a dirty-tree refusal would nag every
  legitimate switch. Trigger: a hook point, or a 50-switch wrapper log.
- **R47 callback sha omission** — a callback is a runtime string no hook
  sees; sha-presence checks false-positive on legitimate BLOCKED format.
  Trigger: sender-side grammar check or a file-backed outbox.
- **R48 pipeline exit-status misread** — the misread lives in transient
  tool calls; a wrapper is opt-in *and* defeats truncation, so it would
  be routed around when needed. Trigger: harness per-stage pipeline codes.

## Honest limits

*Wired* means a command exits nonzero, not that a class is eradicated:
`vgrep` closes one of three selector-failure shapes, and its header says
so. Refusals are decisions with triggers, not surrender — each names the
exact observation that would overturn it.
