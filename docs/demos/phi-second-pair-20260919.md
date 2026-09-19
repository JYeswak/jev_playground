# jev-4uy: phi below 0.5 did not pay — the boundary is insufficient, not wrong

Pane 3 (muse), 2026-09-19. Harvested-from:88fd55b. Offline replay only, zero live
calls, no key. `ensemble/decorrelation.py` unchanged; clone read, never edited.

## The one new pair (sec-bench, NOT spam-eval)

`upstream/Gaurav-Gosain/jev-sec-bench/results/injection.json` vs
`injection_no_context.json`: 662 shared items, texts verified identical in order
(0 mismatches), truth = `label` (263 phish / 399 benign). Scorer A = P(attack) with
context, scorer B = P(attack) without. Same model (`jev-1.13.0` family run), so this
tests context-ablation as the second scorer — paired and fair, weaker-construct
than two independent classifiers, stated here not hidden.

```
n=662  A acc 0.965 (13fn/10fp)   B acc 0.897 (66fn/2fp)
avg acc 0.959   phi 0.343   disagreement 0.092   gain -0.0060   AVERAGE_DID_NOT_PAY
gain 95% CI (B=2000 bootstrap, seed 20260919): [-0.0196, +0.0060]
phi  95% CI: [0.213, 0.469]   <- entirely below the 0.5 line
phish-only (n=263): phi 0.394, gain -0.0456, DID_NOT_PAY
benign-only (n=399): phi 0.443, gain 0.0000, DID_NOT_PAY
```

## What this says about ~0.5

Three populations, all phi below 0.5, none paid. The recipe-4 rule (phi >= 0.5 flags
suspicion; below it payment expected) is **insufficient, not wrong**: low phi did not
imply pay. The visible mechanism is the accuracy gap — averaging a 0.965 scorer with
a 0.897 one dilutes the strong one, and no amount of decorrelation within 9.2%
disagreement overcomes 6.8 points of gap. The rule needs an accuracy-gap term; that
is a hypothesis for recipe 4, NOT a claim (one pair + its strata cannot fit it).

Combined with the source NO-CLAIM (one sign change near 0.5, three pairs, no CIs):
the line still has no calibration behind it, and now has three non-paying points
underneath it. The honest table row, if recipe 4 extends: `sec-bench ctx/noctx,
n=662, phi 0.343 [0.213,0.469], gain -0.006 [-0.020,+0.006], DID_NOT_PAY`.

## Why no second pair (outcome (b), surveyed)

- phishing `metrics.json`: aggregates only (tp/fp/fn + CIs, no per-item arrays).
- rerank `batching.json`: per-query probs but no truth labels.
- agent-failure `text.jsonl`: one judgment per question, no second scorer.
- iammrduncan `live/local-stub.json`: latency aggregates.
- router `tasks.json`/`backtest-sample-results.json`: expects without scorer probs.
- commit-miner CSVs: single classifier.
- themsquared/jev-benchmark (the natural second pair — 60 shared ids): clone absent
  from this tree, and upstream-first forbids rebuilding its numbers from memory.
- sec-bench `code.json` (400 items): single condition; `severity` (0-2.92) is not a
  classifier score — rejected, not shoehorned.

No file was written outside this receipt; `decorrelation.py` untouched.
