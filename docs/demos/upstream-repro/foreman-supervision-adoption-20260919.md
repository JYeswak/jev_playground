# Foreman supervision adoption: PROMOTE with the vignette caveat stated

Pane 3 (muse), 2026-09-19, non-author clearance (pane 1's 76/76 does not count
toward this verdict). Harness: `work/p3-calibration/foreman_cal.py` (set A) +
`foreman_holdout.py` (set B); outputs `foreman_A/B.jsonl` (committed). Pinned
`work/pysdk` env. 60 live requests + feasibility in-request, `jev-latest` ->
`jev-1.13.0`, run once per set. Foreman's clone never opened for thresholds or
scenarios (operating threshold 0.80 taken from the unit brief only).

## Preregistered bar (verbatim, frozen in foreman_cal.py before running)

Over >= 30 constructed observations (>= 10 genuinely stuck, >= 10
healthy-progress, >= 10 AMBIGUOUS mid-cases), ADOPT if (a) AUC >= 0.90
separating stuck from healthy, AND (b) at foreman's shipped 0.80 threshold,
false-stuck <= 1/10 on the healthy set. Ambiguous reported, not scored.
Feasibility: near-deterministic "mentions test failure" through the same
pipeline must reach AUC 0.80 with both classes present, else HARNESS BLIND.

## Result

```
set  AUC (n=20)  false-stuck@0.80  feasibility
A    1.000       0/10              0.955
B    1.000       0/10              0.896
A+B  1.000 (n=40) 0/20 (bar scales 1/10 -> <=2/20)  0.937
```

Ambiguous thirds (reported, unscored): A range 0.07–0.28 (max a10 0.28); B range
0.20–0.68 (a11 0.65, a18 0.65, a19 0.68 flirt with 0.80 without crossing).
The B ambiguous set is hotter and more spread — the interesting part behaves
like a boundary, not a mode.

## Verdict: PROMOTE

Bar met on both sets independently with zero movement. Per-scenario scores in
`foreman_A/B.jsonl` (p_stuck per id).

## The vignette caveat (why this PROMOTE is narrow)

Two perfect 1.000s in a row is suspicious, not triumphant — set B was designed
harder and still separated perfectly. Authored vignettes embed the author's
judgment in word choice ("looping", "steady", "green"); perfect separation may
measure vignette-writing, not supervision. This is the exact defect class that
overturned pane 1's gate ADOPT (1.000 authored → 0.865 held-out). My mitigation
(post-freeze harder holdout) held, but shares my fingerprint. The required
follow-up before any DEPLOYMENT (not adoption): run these frozen questions over
REAL omp worker observations with post-hoc stuck/healthy labels. Adoption says
the question works; only production observations say it supervises.

## NO-CLAIM

Vignettes, not worker transcripts; n=40 scored + 20 ambiguous, one model
version, one run each; Jev cost trivial (~60 small requests). Foreman's own
thresholds/scenarios unopened by this pane. STATUS score 900, composed: 1000
for the bar outcome minus 100 for the single-author vignette caveat.
