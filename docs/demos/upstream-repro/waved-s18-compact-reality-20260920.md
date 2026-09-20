# §18 compact reality: 13→8 reproduces; no session prune exists to claim (2026-09-20)

Level: `live` (keyed replay, 3 runs).

## Live reduce, re-observed with pinned inputs

`fixtures/omp-session-big-20260917.jsonl` (sha in `runs/rerun-20260920.json` as
`transcript_sha256`) → messagesBefore 13, messagesAfter 8, 1 request, 871–1610ms
across 3 runs, 6/6 invariant checks PASS, 0 failures. Same numbers as the 2026-09-17
receipt. This is a reduce of a RECORDED transcript through the live model — the
instrument working as designed, not a session prune.

## What has never been observed (stated, not implied)

- No live SESSION prune: the installed hook yields `undefined` by design (a returned
  pruning "would arrive malformed" — hook header). Nothing claims otherwise; verified
  no prune language in the README beyond the replay numbers.
- No hook firing is observable at all: `compaction/src/omp-binding.ts` has no
  telemetry (no log, no row, no counter). Invocations leave zero trace.
- Reproducibility gap found while re-running: the replay receipt records
  `transcript_sha256` but NOT the model version. Live numbers without a model are
  unciteable next week. Next command: add `model` to the receipt JSON.

## NO-CLAIM

Transcript replay only; 3 runs; one fixture; model version unrecorded (gap above).
The instrument measures; it does not compact live sessions.
