# QuixBugs code-Score, run-to-run variance: does the pair-ordering WIN hold on 3x3 runs? (bead `jev-kz50`)

ClaimCheckTool (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first rerun call)

**Headline under test** (`jev-2wc`, [`score-quixbugs-20260924.md`](score-quixbugs-20260924.md), bar
`6ee168c`, rows `a2bee8b`). Over the 40 QuixBugs Python program pairs, correct vs buggy, the
jev-curate `code_quality` Score (five levels, sent as an ordered list):
- **Jev separates:** W/L/T 38/2/0, sign p = 1.5e-09, AUC 0.739 [0.683, 0.812].
- **Haiku 4.5** via `system-one-adapter`: 28/10/2, AUC 0.668.
- **Pair ordering, Jev vs Haiku:** Jev-only 12, Haiku-only 2, McNemar p = 0.013, **WIN**.
- **AUC difference:** +0.070 [−0.003, +0.156], **TIE**.
- **Pass rule:** PASS.

**Headroom, from the committed run before any rerun** (`python3 work/score-quixbugs/variance.py
--bar`): **1 pair.** Moving one pair from Jev-only to Haiku-only gives 11 vs 3, p = 0.057, a TIE.
Losing Jev-only pairs without Haiku gaining any: 11 vs 2 p = 0.023, 10 vs 2 p = 0.039, 9 vs 2
p = 0.065. So 3 lost pairs end the WIN. This is the thinnest margin of any surviving Jev win.

**Runs.** Two more runs of each arm on the same 80 programs, same code path, pin, question and
state (`{"text": canon}`). Each run goes to a new file; no committed row file or receipt of
`jev-2wc` is edited.
- Jev: `run.py jev work/score-quixbugs/rows-jev-run{2,3}.jsonl`
- Haiku: `run.py haiku work/score-quixbugs/rows-haiku-run{2,3}.jsonl`. The adapter's
  `probability_errors` / `original_probabilities` are recorded as in run 1.
- The only change to `run.py` since `jev-2wc` is an optional output path (second argument). The
  call path, `QUESTION`, clients and settings are unchanged.
- Sequential order: Jev 2, Jev 3, Haiku 2, Haiku 3, each at 8 concurrent. Each run gets at most one
  resume pass for failed rows. A pair still unanswered is scored by `jev-2wc`'s rule (T, AUC at 2.0).
- Only `jev` and `haiku`, the primary arms, are re-run. `jev-flat` and `jev-asis` were descriptive
  and are not re-run.

**Scorer.** `python3 work/score-quixbugs/variance.py` (stdlib, no key). It imports `score.py`'s rules
unchanged: outcomes, sign test, AUC and bootstrap, McNemar, the paired AUC bootstrap, the pass rule
and the zero-mass drop. It exits 1 unless run 1 x run 1 reproduces every published `jev-2wc`
verdict. At the bar commit it does: 38/2/0, 28/10/2, 12 vs 2 WIN, AUC TIE, PASS.

**Rules, fixed now** (the all-pairings rule of `jev-x5k` / `jev-hg8` / `jev-91u`):
- **R1, decides: all 9 pairings** (Jev run j vs Haiku run h, j, h in 1..3). Each pairing gets
  `jev-2wc`'s full pass rule on all 40 pairs **and** with that Haiku run's zero-mass pairs dropped.
  - **HOLDS:** pair ordering WIN in 9/9 pairings, both ways.
  - **DOWNGRADED:** WIN in 5 to 8 of 9, both ways, and no LOSE. The headline becomes "Jev orders
    more pairs correctly in direction, significant in a majority of pairings, not all". PASS is kept.
  - **RETRACTED to TIE:** WIN in fewer than 5 of 9, and no LOSE. PASS is kept.
  - **PASS RETRACTED:** any pairing fails the pass rule. That happens if a Jev run fails to separate
    (W>L, sign p < 0.05, AUC CI above 0.5) or either comparison is a LOSE.
  - A `NEGATIVE_EVIDENCE.md` row with a retry condition follows any outcome other than HOLDS.
- **The published AUC TIE** is re-checked in all 9 pairings. It is not upgraded here even if every
  pairing shows WIN, because this bar only tests the published verdicts.
- **R2, describes: flips.** For each pair of runs of the same arm: pair outcomes (W/L/T) that change,
  and program scores whose rounded level changes. Compare these with the 1-pair headroom.

**Spend, planned.** 160 Jev + 160 Haiku calls, plus resume calls.

**NO-CLAIM.** Three runs per arm on one small public set (40 pairs), one question wording, one Jev
version, one Haiku configuration, all within one hour. This measures sampling variance of the served
models, not drift across days or versions.
