# Part A: where Jev wins — cross-experiment theory (jev-2zbl, 2026-10-02)

Evidence base: `table_draft.json` (LedgerSweep extraction, 39 measured rows R79–R147;
EVAL/live receipts; all counts below from that file). 3 verdict=win rows are ALL
external-comparator benchmarks (Banking77/SciFact/FEVER vs Haiku — a pairing now off-limits).
Own-vein record: **0 wins in 36 measured experiments** (27 loss, 9 tie, ties mostly
variance-retracted or n.s.).

## Loss rate by task feature (own veins, n=36, Wilson 95%)

- direction=route: 9/9 loss [0.70, 1.00]; keep: 4/4 [0.51, 1.00]; flag: 7/8 [0.53, 0.98];
  predict: 7/15 [0.25, 0.70] — the only direction that ever ties.
- future/counterfactual question: 6/6 loss [0.61, 1.00]; present-tense: 21/30 [0.52, 0.83].
- answer NOT visible in state: 9/10 loss [0.60, 0.98]; visible: 18/25 [0.52, 0.86].
- primitive=Choice: 10/11 loss [0.62, 0.98]; Noul 9/11 [0.52, 0.95]; Score 2/6 [0.10, 0.70].

## Simplest separating model (decision rule)

PREDICT-LOSS iff direction in {route, keep, flag} AND (future OR answer-invisible);
else TIE-or-better. Illustrative only at n=36 (CIs wide; claiming more is overfit).

## Named features (with honest uncertainty)

1. **Acting vs predicting.** Every route/keep decision lost (13/13 combined with flag 20/21).
   Jev scores text; our wins would need acting on unobserved state (fleet, bead, future).
2. **Counterfactual/future questions.** 6/6 losses (retry-will-succeed R142, long-runner R141,
   next-tool R147, triage-action R140, applicability-suppression R143, state-enriched R145).
   Labels depend on outcomes outside the judged text.
3. **Answer visibility + primitive.** The only non-losses pair visible evidence with Score
   (uncertainty-preserving) or pure prediction; Choice forces a commitment the evidence
   cannot support (10/11 loss).

## Rival explanations (not ruled out)

- Bars set too high / margins too strict (we demand +8pp, zero-miss harm bounds).
- Baseline authorship: our heuristic baselines are strong (regexes at 0.65–1.00), built by
  the same people who write the questions — home-field advantage for the baseline.
- Small N: with 36 experiments, the true own-vein win rate could be as high as ~10%
  (rule of three) — absence of wins is not proof of impossibility.

## What would change the theory

A single own-vein win with a preregistered bar on held-out data, or a Part B invariance
violation showing decisions track surface form (which would explain losses mechanically).
