# Does a Jev win survive a re-run? Run-to-run variance of two live headlines (bead `jev-qbc`)

JevVariance (background agent of pane 1), 2026-09-24. Live lane, Jev pinned `jev-1.13.0`.

## Preregistered (committed before the first rerun call)

**Question.** Every live receipt of 2026-09-24 lists "one run per arm, variance not measured" in
its NO-CLAIM. Two of them report a Jev win over Claude Haiku 4.5:

| Unit | Headline under test | Committed at |
|---|---|---|
| SST-5 Score, `jev-zui` ([receipt](score-sst5-20260924.md)) | Jev MAE 0.488 vs Haiku 0.556, exact sign test on per-row absolute error 109 vs 75 rows, p = 0.0148 (MAE WIN); accuracy 273 vs 251, McNemar p = 0.092 (TIE); pass rule PASS | `576e60e` |
| Banking77 10-intent Choice, `jev-k3k` ([receipt](choice-banking77-20260924.md)) | Jev 384/400 vs Haiku 362/400, McNemar 25 vs 3, p = 2.7e-5 (WIN) | `3709ee6` |

Does each headline hold when only the Jev arm is asked again, twice, with the same code, the same
pin, the same state and question?

**Runs.** Jev arm only, two more runs per unit, written to new files beside the originals; the
committed `rows-jev.jsonl` is run 1 and no committed row file or receipt of either unit is edited.

- SST-5: `work/score-sst5/run.py jev work/score-sst5/rows-jev-run{2,3}.jsonl` (optional output
  path added in `b53a33b`; the Jev call path is byte-identical to run 1's `ae161b6`).
- Banking77: `work/choice-banking77/run.py --out work/choice-banking77/rows-jev-run{2,3}.jsonl jev`
  (`--out` added in `9df40c7` on top of `909278f`; the Jev call is unchanged from run 1's
  `a0ed3c1`, and the ten option labels are identical, all already lowercase).
- Runs are sequential (run 3 starts after run 2 finishes), same concurrency as run 1 (8). Each run
  gets at most one resume pass for failed rows, as in the original units; a row still failed is
  scored by the original unit's rule (SST-5: incorrect, worst possible error; Banking77: wrong).
- The Haiku rows are one committed run and are held fixed; every paired test is Jev run k against
  that one Haiku run. Haiku's own variance is not measured here.

**Scorer.** `python3 work/jev-variance/score.py` (stdlib, no key, no network). It restates both
units' committed scoring rules and exits 1 unless run 1 reproduces the committed headline numbers
above. `--bar` prints only the headroom below, from committed files.

**Headroom, computed from the committed run 1 before any rerun** (`score.py --bar`). The fewest
Jev answers that would have to change to break the verdict, letting every harmful change land
where it hurts most; it is a lower bound, since not every such change is possible for every row.
A rerun that changes fewer Jev answers than this cannot move the verdict, whichever rows change.

| Verdict | Headroom (rows) | As a per-row flip rate |
|---|---:|---:|
| SST-5 headline: MAE sign test WIN vs Haiku (109 vs 75, 316 equal) | 4 | 0.8% of 500 |
| SST-5 pass rule: accuracy not LOSE vs Haiku (89 vs 67) | 44 | 8.8% |
| SST-5 pass rule: beats always-1 / always-2 on accuracy and MAE | 81 / 110 | 16.2% / 22.0% |
| Banking77 headline: McNemar WIN vs Haiku (25 vs 3) | 10 | 2.5% of 400 |
| Banking77 PASS: not LOSE (within 12 rows of Haiku's 362) | 35 | 8.8% |

The SST-5 headline is the fragile one: four changed levels, placed adversarially, turn it into a
TIE.

**Retraction rules, fixed now.**

- **R1, the verdict on every run (decides).** Re-run each unit's committed paired test with Jev
  run k against the committed Haiku rows, for k = 1, 2, 3.
  - SST-5: the headline "Jev beats Haiku on MAE" HOLDS only if the sign test is WIN on all three
    runs; one run at TIE or LOSE RETRACTS it. The unit's PASS is RETRACTED if any run fails its
    pass rule (a constant not beaten on accuracy and MAE, or a LOSE to Haiku on either).
  - Banking77: the headline WIN HOLDS only if all three runs are WIN; any run at NON-INFERIOR
    DOWNGRADES it to NON-INFERIOR (PASS kept); any run at LOSE or below the feasibility floor
    RETRACTS the PASS.
- **R2, flip count against headroom (describes).** For each pair of Jev runs, the number of rows
  whose answer differs (SST-5: rounded level; Banking77: chosen intent). A pair below the headroom
  above could not have moved the verdict by construction; a pair at or above it means the verdict
  on that run was decided by which rows flipped, and R1 is the only word on it.
- **R3, spread against the gap (magnitude).** If the range of the metric across the three runs is
  at least the committed Jev-Haiku gap (SST-5: MAE range >= 0.068 = 0.556 - 0.488; Banking77:
  correct-count range >= 22 rows), the single-run number is not reportable as a point estimate:
  the receipt reports the three-run range instead, whatever R1 says.

A retraction or downgrade is written here and reported to the owning units' receipts' authors; it
does not edit their receipts.

**Spend, planned.** 2 x 500 + 2 x 400 = 1,800 Jev calls, plus any resume calls.

## Result (live, 2026-09-24 02:37-02:38 UTC, bar at `37e6757`)

Four Jev runs, 1,800 calls, 1,800 answered, 0 failed, 0 resume passes; every row reports model
`jev-1.13.0`. Spend: 686,500 input / 113,150 output Jev tokens (the four runs), no Haiku calls.
Input tokens per run are identical to run 1's (SST-5 188,506; Banking77 154,744).
Re-score: `python3 work/jev-variance/score.py` (about 25 s, the headroom search; no key).

**Verdicts under the committed bar.**

| Unit | R1: verdict on runs 1 / 2 / 3 | R1 outcome | R3: metric across runs, range vs gap | R3 outcome |
|---|---|---|---|---|
| SST-5 headline, MAE vs Haiku | WIN / WIN / WIN (sign p 0.0148 / 0.0403 / 0.0190) | **HOLDS** | MAE 0.488 / 0.500 / 0.492, range 0.012 vs 0.068 | REPORTABLE |
| SST-5 pass rule | PASS / PASS / PASS (accuracy vs Haiku TIE on all three) | **HOLDS** | exact correct 273 / 269 / 273 | |
| Banking77 headline | WIN / WIN / WIN (McNemar p 2.7e-5 / 2.7e-5 / 3.0e-6) | **HOLDS** | correct 384 / 384 / 386, range 2 vs 22 | REPORTABLE |

Both headlines hold on every run; neither is retracted or downgraded.

**SST-5, per run** (Jev rounded level vs the committed Haiku rows, N = 500):

| Run | Rows file | Exact correct | MAE | Jev-only / Haiku-only correct | McNemar p | Jev / Haiku lower error | Sign p | MAE verdict | Pass rule |
|---|---|---:|---:|---|---:|---|---:|---|---|
| 1 | `rows-jev.jsonl` (committed `576e60e`) | 273 | 0.488 | 89 / 67 | 0.092 | 109 / 75 | 0.0148 | WIN | PASS |
| 2 | `rows-jev-run2.jsonl` | 269 | 0.500 | 89 / 71 | 0.179 | 108 / 79 | 0.0403 | WIN | PASS |
| 3 | `rows-jev-run3.jsonl` | 273 | 0.492 | 91 / 69 | 0.097 | 110 / 77 | 0.0190 | WIN | PASS |

| Pair | Level flips | Correctness flips | Class vs Haiku changes | Mean abs change of raw score | Flips < headroom (4)? |
|---|---:|---:|---:|---:|---|
| 1 vs 2 | 8 (1.6%) | 6 (1.2%) | 7 (1.4%) | 0.024 | no |
| 1 vs 3 | 8 (1.6%) | 6 (1.2%) | 7 (1.4%) | 0.024 | no |
| 2 vs 3 | 6 (1.2%) | 6 (1.2%) | 6 (1.2%) | 0.024 | no |

11 of 500 rows (2.2%) do not get the same level on all three runs. In 9 of the 11 every raw score
lies within 0.1 of a rounding boundary (x.5), e.g. row 104 at 3.49 / 3.51 / 3.49; two move
further (row 82: 0.52 / 0.47 / 0.34; row 465: 1.58 / 1.62 / 1.42).
The full list is printed by the scorer.

**Banking77, per run** (Jev choice vs the committed Haiku rows, N = 400):

| Run | Rows file | Correct | Accuracy | Jev-only / Haiku-only | McNemar p | Verdict |
|---|---|---:|---:|---|---:|---|
| 1 | `rows-jev.jsonl` (committed `3709ee6`) | 384 | 96.0% | 25 / 3 | 2.7e-5 | WIN |
| 2 | `rows-jev-run2.jsonl` | 384 | 96.0% | 25 / 3 | 2.7e-5 | WIN |
| 3 | `rows-jev-run3.jsonl` | 386 | 96.5% | 26 / 2 | 3.0e-6 | WIN |

| Pair | Choice flips | Correctness flips | Flips < headroom (10)? |
|---|---:|---:|---|
| 1 vs 2 | 2 (0.5%) | 2 (0.5%) | yes: this rerun could not have moved the verdict |
| 1 vs 3 | 2 (0.5%) | 2 (0.5%) | yes |
| 2 vs 3 | 2 (0.5%) | 2 (0.5%) | yes |

3 of 400 rows (0.8%) change choice across the three runs (rows 238, 360, 394), each between the
right intent and one wrong one.

**What this says.**

- Jev `jev-1.13.0` is not deterministic on identical input: the raw expected score moves by 0.024
  on average per row between runs, and 1.2-1.6% of SST-5 levels and 0.5% of Banking77 choices flip.
- Banking77's WIN is robust in the R2 sense: every pair of runs differs in 2 answers, below the
  10 that could move the verdict.
- SST-5's MAE WIN held on all three runs but is not robust in that sense: each pair differs in 6-8
  levels, above the 4 that could move it, and run 2 landed at sign p = 0.040 against alpha 0.05.
  It survives re-asking; it is a narrow win, and a fourth run could land at TIE.

## NO-CLAIM

- Three runs per arm estimate run-to-run variance loosely; "held on 3 of 3 runs" is not a
  probability that a future run holds.
- Haiku was not re-run: its rows are one run held fixed, so the paired tests carry no incumbent
  variance. The bead's conditional Haiku re-run was out of this unit's assignment; not run.
- All four runs sat inside about one minute on 2026-09-24 UTC; nothing here speaks to
  drift across days or a server-side change under the same pin.
- The headroom is a lower bound computed by letting every harmful change land where it hurts most;
  it is not a prediction of which rows flip.
- No claim about the full 77-intent Banking77 set (`jev-4jf`) or any other unit.

## Non-author verification — Verifier2

Verifier2 (background agent of pane 1, not an author of this unit), 2026-09-24. Oracle: the
committed row files and the fourth oracle (labelled sets we own); no live call. Everything below ran
in a `git clone --local` of the repo at `888efbe` in `mktemp -d`, not in the shared worktree.

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Bar precedes data | `git merge-base --is-ancestor 37e6757 510e804` | yes; bar 02:37:08 UTC, rows 02:40:27 UTC |
| 2 | Bar text not edited after the bar commit | `git diff 37e6757 510e804 -- <this receipt>`; `git log -- <this receipt>` | lines 1-74 byte-identical; the only hunk replaces the `## Result` NOT_RUN stub; no later commit touches the file |
| 3 | Scorer rules not edited after the bar | `git diff 37e6757 510e804 -- work/jev-variance/score.py` | +27/-8, reporting only: prints the unstable-row tables; no verdict, headroom or R1-R3 logic changed |
| 4 | Runners changed only by an output path | `git diff b53a33b^ b53a33b -- work/score-sst5/run.py`; `git diff 8851fcd^ 8851fcd -- work/choice-banking77/run.py` | SST-5: optional 2nd arg sets `OUT`, `out_path` returns `OUT or rows-<arm>.jsonl`; Banking77: `--out` sets `path = out or rows_pattern`, rejects more than one arm (64). With no new argument both behave exactly as before. Neither runner changed again before `510e804` |
| 5 | Jev call path equal to run 1's | `git log -- work/score-sst5/run.py work/choice-banking77/run.py`; `git diff a0ed3c1 909278f -- work/choice-banking77/run.py` | SST-5: only `b53a33b` after `ae161b6`. Banking77: `909278f` lowercases labels and adds `--set full`; recomputed on `subset.jsonl`, lowercasing changes none of the 10 intents, so the options sent are identical |
| 6 | Samples rebuild byte-identically | `python3 work/score-sst5/sample.py 500 20260924`; `python3 work/choice-banking77/sample.py --check` | SST-5 sha256 `522bee6e…d903` equals HEAD's; Banking77 subset "check: identical" (fetch from the pinned public sources, sha256-checked) |
| 7 | Re-score reproduces every headline | `python3 work/jev-variance/score.py` | exit 0; SST-5 273/269/273 exact, MAE 0.488/0.500/0.492, sign p 0.0148/0.0403/0.019, WIN x3, PASS x3; level flips 8/8/6; Banking77 384/384/386, McNemar 2.74e-5/2.74e-5/3.03e-6, WIN x3; choice flips 2/2/2; headroom 4 and 10; 11/500 and 3/400 unstable rows — every number in the Result section |
| 8 | Run-1 guard fires on a known-bad input | changed row `i=0` of `work/score-sst5/rows-jev.jsonl` from 2.99 to 3.99 in the clone, re-ran the scorer, restored the file byte-identically | exit 1, "SST-5 run 1 does not reproduce the committed receipt: correct 274, jev_better 110"; clone clean after restore |
| 9 | Row hand-check (own code, not the scorer's) | recomputed the expected value from each stored probability map and the rounded level for SST-5 rows 0, 30, 82, 104, 250, 458, 465, 499 on all 3 runs; checked choice = argmax of the stored map for Banking77 rows 5, 200, 238, 360, 394 | every stored `score` matches its map within 0.02 and rounds to the level the scorer reports; rows 82/465 and 238/360/394 read as the receipt describes; independent flip counts 8/8/6 and 2/2/2, correct counts 384/384/386 |
| 10 | Spend and run-shape claims | summed `usage` and `latencyMs` over the four new row files | 1,800 rows, 0 `error` rows, all `model` = `jev-1.13.0`; input 2 x 188,506 + 2 x 154,744 = 686,500; output 2 x 9,000 + 2 x 47,575 = 113,150; input per run identical to run 1; summed latency / 8 is about 38 s for the four runs, consistent with "inside about one minute" |
| 11 | Committed incumbent and run-1 rows untouched | `git log -- work/*/rows-haiku.jsonl work/*/rows-jev.jsonl` | last touched by `576e60e` and `3709ee6` |
| 12 | NO-CLAIM matches what ran | read against checks 1-11 | Haiku not re-run (no Haiku row file added); runs within minutes on one date; no 77-intent claim |

**Erratum (citation only).** The Runs section says Banking77's `--out` was "added in `9df40c7`".
The `--out` change is `8851fcd`; `9df40c7` touches only `.beads/issues.jsonl` (bead store: CLINC150,
FEVER). Check 4 was run on `8851fcd`. No number depends on it.

**Verdict: CONFIRMED.** Both headlines HOLD under the committed bar on the committed rows.
Level: `[oracle]` clean-clone re-score of committed files (N = 500 SST-5 + 400 Banking77 rows x 3
runs, `jev-1.13.0`, 2026-09-24). Not run by the verifier: no live call, so no fourth Jev run and no
Haiku re-run; the check that the live rows came from these runners rests on the committed code,
matching input-token totals and row shape, not on observing the calls.
