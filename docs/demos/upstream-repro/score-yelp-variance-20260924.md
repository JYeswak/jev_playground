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

Bar at `d29397c`, committed before the first rerun call. Live, 2026-09-24, `[live]`. Four reruns in
sequence: 2,000 calls, 2,000 answered, 0 failed, 0 resume passes. Every Jev row reports
`jev-1.13.0`; every Haiku row reports `anthropic/claude-haiku-4-5`. Adapter debug was recorded on
all 1,000 rerun Haiku rows: 0 had `probability_errors` set, 0 were zero-mass. Row files (no review
text; sha256 at the end of this section): `rows-jev-run2.jsonl`, `rows-jev-run3.jsonl`,
`rows-haiku-run2.jsonl`, `rows-haiku-run3.jsonl`. Re-score with no key:
`python3 work/score-yelp/variance.py`.

| Arm | Run | Exact correct | MAE | Tokens in / out |
|---|---:|---:|---:|---|
| Jev | 1 (`jev-76o`) | 341/500 | 0.348 | 280,986 / 8,500 |
| Jev | 2 | 342/500 | 0.346 | 280,986 / 8,500 |
| Jev | 3 | 341/500 | 0.346 | 280,986 / 8,500 |
| Haiku | 1 (`jev-76o`) | 323/500 | 0.384 | 465,525 / 22,783 |
| Haiku | 2 | 328/500 | 0.372 | 465,525 / 22,795 |
| Haiku | 3 | 330/500 | 0.370 | 465,525 / 22,614 |

**R1, all 9 pairings** (pass rule on all rows, and with that Haiku run's zero-mass rows dropped;
there were none, so both columns agree):

| Jev run | Haiku run | Accuracy: Jev-only / Haiku-only, McNemar p | MAE: Jev lower / Haiku lower, sign p | MAE verdict | Pass rule |
|---:|---:|---|---|---|---|
| 1 | 1 | 59 / 41, 0.089 | 67 / 45, 0.047 | **WIN** | PASS |
| 1 | 2 | 58 / 45, 0.237 | 66 / 50, 0.163 | TIE | PASS |
| 1 | 3 | 54 / 43, 0.310 | 62 / 47, 0.180 | TIE | PASS |
| 2 | 1 | 60 / 41, 0.073 | 67 / 45, 0.047 | **WIN** | PASS |
| 2 | 2 | 57 / 43, 0.193 | 64 / 48, 0.156 | TIE | PASS |
| 2 | 3 | 54 / 42, 0.261 | 61 / 46, 0.176 | TIE | PASS |
| 3 | 1 | 60 / 42, 0.092 | 68 / 46, 0.049 | **WIN** | PASS |
| 3 | 2 | 56 / 43, 0.228 | 64 / 48, 0.156 | TIE | PASS |
| 3 | 3 | 52 / 41, 0.300 | 60 / 45, 0.172 | TIE | PASS |

MAE WIN in **3 of 9** pairings, with and without zero-mass rows. All 3 wins are against Haiku run 1.
Pass rule PASS in 9/9 (both constants beaten, no LOSE). Accuracy TIE in 9/9.

**R2, flips.** Jev changes 5, 7 and 6 levels between its runs (run 1 vs 2, 1 vs 3, 2 vs 3). Haiku
changes 47, 45 and 52. Every Jev pair exceeds the 1-row headroom, so the run-1 verdict depended on
which rows flipped. Haiku's flips are about eight times Jev's, and they decide the verdict.

**R3, spread.** Jev exact correct 341 / 342 / 341 (range 1), MAE 0.348 / 0.346 / 0.346 (range
0.002). Haiku exact correct 323 / 328 / 330 (range 7), MAE 0.384 / 0.372 / 0.370 (range 0.014).
Neither range reaches the run-1 gap (18 rows, 0.036), so the single-run numbers stay reportable as
point estimates. Haiku's run 1, the one `jev-76o` used, was its worst of the three.

**Descriptive, no verdict.** Per-row error averaged over each arm's three runs: Jev lower on 89
rows, Haiku lower on 58, sign test p = 0.013. Three-run mean MAE: Jev 0.347, Haiku 0.375. This
averaging was declared descriptive in the bar and does not override R1.

**Verdict under the bar at `d29397c`: RETRACTED to TIE.** "Jev beats Haiku on Yelp MAE" was
significant only against Haiku's first run. Across all nine pairings, it is significant in 3 of 9,
fewer than the 5 the bar needed for a downgrade. The Yelp headline becomes: **Jev's MAE is lower
than Haiku's in every pairing (by 15 to 22 rows on the sign test, 0.022 to 0.038 in MAE), but the
difference is not reliably significant at N = 500. On exact accuracy it is a TIE.** The unit's
PASS stands: Jev beats both constants and never loses to Haiku, in all nine pairings. Jev is the
steadier arm: 5 to 7 level changes per re-run, against Haiku's 45 to 52. Written as
`NEGATIVE_EVIDENCE.md` R88. The `jev-76o` receipt now carries a pointer to this section.

Row sha256: `rows-jev-run2.jsonl` `88fd3e32…e0b77a`, `rows-jev-run3.jsonl` `3c3f364f…57dc3e`,
`rows-haiku-run2.jsonl` `820dd6d1…9f51cb1`, `rows-haiku-run3.jsonl` `c8d997db…797f51b`.

**Spend.** 2,000 live calls. Jev: 1,000 calls, 561,972 input / 17,000 output tokens. Haiku: 1,000
calls, 931,050 input / 45,409 output (adapter totals). [INFERENCE] The Haiku reruns are about
$1.16 at list price. Jev's billed units were not read.

**NO-CLAIM.** Three runs per arm, one sample of 500, one wording, one version per arm, all within
about an hour on 2026-09-24. The three-run average is descriptive and was not a decision rule. SST-5
(`jev-qbc`) re-ran only Jev against one Haiku run, so its "3/3 WIN" answers a narrower question
than the 9-pairing rule here; this receipt does not re-judge it. A non-author spot-check is still
pending.

## Non-author verification (BillingUnits, 2026-09-24, zero model calls)

Oracle: committed rows, re-scored without a key in a clean clone. Clone:
`git clone --local` → `/tmp/bu-91u-clone` @ `abe14d9`. `work/score-yelp/` is unchanged between
`1b94085` and that HEAD.

- **Order.** The bar `d29397c` (21:16:49) is an ancestor of the rows commit `1b94085` (21:20:58).
- **Runner diff.** `git diff 52d94c2 d29397c -- work/score-yelp/run.py` changes only the output
  path: an `OUT` global, `out_path` returning `OUT or rows-<arm>.jsonl`, and argv accepting an
  optional third argument. The question, the state, the model pin and the retry policy are
  untouched. `run.py` has no later commit.
- **Scorer.** `env -u TYPESAFE_API_KEY -u ANTHROPIC_API_KEY python3 work/score-yelp/variance.py`
  exits 0. It reproduces run 1 (Jev 341/500 MAE 0.348, Haiku 323/500 MAE 0.384), MAE WIN in 3/9
  pairings (every WIN is against Haiku run 1), pass rule PASS in 9/9, 0 pairings with a LOSE,
  headline `RETRACTED to 'MAE TIE with Haiku'`. Accuracy is TIE in all 9 pairings.
- **Independent recount** (my own script, not `variance.py`: level = floor(score + 0.5), clamped;
  exact sign test). Exact correct per file: Jev 341 / 342 / 341, Haiku 323 / 328 / 330. MAE 0.348 /
  0.346 / 0.346 and 0.384 / 0.372 / 0.370. Every one of the 9 sign-test splits matches the table:
  67/45 p 0.0467, 66/50, 62/47, 67/45 p 0.0467, 64/48, 61/46, 68/46 p 0.0487, 64/48, 60/45. That
  gives WIN 3/9. All 6 files hold 500/500 answered rows, one model each (`jev-1.13.0`,
  `anthropic/claude-haiku-4-5`), and every probability map sums to 1 within 0.05.
- **Row hashes.** sha256 of the four rerun files matches the prefixes and suffixes quoted above.
- **Ten rows by hand** (seed 20260924, three each from Jev runs 2 and 3 and Haiku run 2, one from
  Haiku run 3). The score, the rounded level and the sample label agree with the scorer's reading in
  all ten: Jev run 2 rows 7 (4→4), 419 (2 vs 2.83→3), 480 (1→1); Jev run 3 rows 338 (0→0),
  467 (3→3), 279 (2 vs 3.78→4); Haiku run 2 rows 323 (2→2), 359 (1→1), 74 (0→0); Haiku run 3 row
  286 (2→2).
- **One observation, not a defect.** Jev's returned `score` differs from the expected value of its
  own 2-decimal `probabilities` by up to 0.03 on 4 / 7 / 9 rows per run. On exactly 1 row per run,
  rounding the recomputed value would pick a different level. The prereg names the returned score as
  primary, so the verdict is unaffected. A reader who recomputes from `probabilities` will see
  1-row differences.

**Verdict:** reproduced. The retraction to TIE stands under the committed rule.
