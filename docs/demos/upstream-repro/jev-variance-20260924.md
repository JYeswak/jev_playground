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

## Result

NOT_RUN. Filled in after the four runs.
