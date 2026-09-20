# §8 prevalence-first — PASS (2026-09-20)

Level: `live` (31-call re-run) + `test` (3/3 offline).

## What was built

`work/jev-prevalence-first/`: SPEC.md, prevalence-check.mjs (near count → own-constant
bar → verdict, order enforced in code and asserted per test arm), prevalence-check.test.mjs
(3/3), p3-commit-31.mjs (embedded 31×3 recorded scores + drift finding), BASE-RATES.md
(bv 20/50 @ 2026-09-20T07:04:54Z; §19 0/20 promoted).

## The two findings that matter more than the package

1. Transcribed scores rot: the first P3 transcription matched neither the Unit-2 run
   nor the re-run (omits near 2 vs 4 vs 4, yes 2 vs 2 vs 4). Corrected from
   `/tmp/score31-rerun.log` (31 live calls, just now); tallies confirmed exact.
2. The emblematic near-miss flipped: 48eecdf omits 0.49 MISS → 0.50 HIT on re-run.
   Verdicts stable (DEGENERATE/WEAK/WEAK), the single most-quoted row inverted on
   threshold noise. Near-threshold rows must be re-measured, never quoted — §14e
   biting our own receipt.

## Ledger line

SECTION 8 prevalence-first — PASS — `verdict: 28/31 vs best-constant 30 + near 4 → WEAK` + 48eecdf flip 0.49→0.50 + bv base 20/50 live — NO-CLAIM: tooling + one re-run; verdicts stable, rows move.

## NO-CLAIM

Checker standardises order, not truth. Tallies verified against a same-hour live
run; any later quote must re-run. Bead jev-vbh.6 ready to close.
