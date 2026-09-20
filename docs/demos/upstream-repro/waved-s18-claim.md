# §18 CLAIM STUB — jev-compact reality (pane 3, 2026-09-20)

Claiming this section per the Wave D protocol. Read before building (per the brief):

- `compaction/` measures transcript replay through fast-jev-compaction (adapter +
  keyed live replay + A/B with retracted n=1 verdicts), NOT live session pruning.
- The installed hook (`.omp/hooks/pre/jev-compact.ts`) declines by design (yields
  `undefined` always; "a returned pruning would arrive malformed").
- The binding (`compaction/src/omp-binding.ts`) has NO telemetry — hook firings
  leave no trace anywhere.

Target: re-run the keyed big-fixture replay to confirm the 13→8 live reduce still
reproduces (inputs pinned), and state plainly what has never been observed (a live
session prune). Full receipt follows; this stub is the claim only.
