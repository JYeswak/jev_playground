# Does the Yelp Score MAE win survive re-runs of both arms? (bead `jev-91u`)

ConfidenceCascade (background agent of pane 1), 2026-09-24. Live lane, Jev pinned `jev-1.13.0`.
Follows `jev-76o` ([receipt](score-yelp-20260924.md)) and the method of `jev-qbc`
([receipt](jev-variance-20260924.md)). Unlike `jev-qbc`, the Haiku arm is re-run too.

## Preregistered (committed before the first rerun call)

**Headline under test** (`jev-76o`, rows committed at `df13f17`): on 500 Yelp test reviews, Jev MAE
0.348 against Haiku 4.5's 0.384. The exact sign test on per-row absolute error is 67 vs 45, p = 0.0467
(MAE WIN). Accuracy is 341 vs 323, McNemar 59 vs 41, p = 0.089 (TIE). Pass rule: PASS.

**Headroom, from committed run 1 before any rerun** (`python3 work/score-yelp/variance.py --bar`):
**1 row.** Moving one row from "Jev lower error" to "Haiku lower error" gives 66 vs 46,
p = 0.072, a TIE. On SST-5, `jev-qbc` measured 6 to 8 level flips per Jev re-run, so this headline is
expected to be at risk.

**Runs.** Two more runs of each arm, same 500 rows, same code path, same pin, same question, same
state. Each run goes to a new file; no committed row file or receipt of `jev-76o` is edited.
- Jev: `work/score-yelp/run.py jev work/score-yelp/rows-jev-run{2,3}.jsonl`
- Haiku: `work/score-yelp/run.py haiku work/score-yelp/rows-haiku-run{2,3}.jsonl`, with the
  adapter's `debug.probability_errors` / `original_probabilities` recorded as in run 1.
- The only change to `run.py` since `52d94c2` is an optional output path (second argument). The
  call path, `QUESTION`, clients and settings are byte-identical.
- Runs are sequential: Jev 2, Jev 3, Haiku 2, Haiku 3, each at 8 concurrent. Each run gets at most
  one resume pass for failed rows. A row still failed is scored by `jev-76o`'s rule (wrong, worst
  possible error).
- Review text comes from the gitignored `texts.jsonl`, checked against each row's sha256. No text is
  committed.

**Scorer.** `python3 work/score-yelp/variance.py` (stdlib, no key, no text). It imports
`score.py`'s rules unchanged and exits 1 unless run 1 reproduces the headline numbers above.

**Rules, fixed now.**
- **R1, decides: all 9 pairings (Jev run j vs Haiku run h, j, h in 1..3).** Each pairing gets
  `jev-76o`'s full pass rule on all 500 rows **and** with that Haiku run's zero-mass rows dropped.
  - **HOLDS:** the MAE sign test is WIN in 9/9 pairings, both ways.
  - **DOWNGRADED:** WIN in 5 to 8 of 9, both ways, and no LOSE. The headline becomes "Jev's MAE is
    lower in direction and significant in a majority of pairings, not all". PASS is kept.
  - **RETRACTED to TIE:** WIN in fewer than 5 of 9, and no LOSE. The headline becomes "MAE TIE with
    Haiku". PASS is kept.
  - **PASS RETRACTED:** any pairing fails the pass rule (a constant not beaten, or a LOSE to Haiku on
    accuracy or MAE). A `NEGATIVE_EVIDENCE.md` row with a retry condition follows.
- **R2, describes: flips against headroom.** For each pair of runs of the same arm, the number of
  rows whose rounded level differs. More than 1 means the run-1 verdict depended on which rows
  flipped.
- **R3, magnitude: spread against gap.** If an arm's three-run range is at least the run-1 gap
  (exact correct: 18 rows; MAE: 0.036), the single-run numbers are not reportable as point
  estimates, and the receipt gives the three-run ranges instead.
- **Descriptive, no verdict.** Per-row absolute error averaged over each arm's three runs, with a
  sign test between arms.

**Spend, planned.** 1,000 Jev + 1,000 Haiku calls, plus resume calls. [INFERENCE] The Haiku arm is
about $1.2 at list price.

**NO-CLAIM.** Three runs per arm on one sample of 500, one question wording, one Jev version and one
Haiku configuration, all within one hour. This measures sampling variance of the served models, not
drift across days or versions.

## Result

Pending the reruns.
