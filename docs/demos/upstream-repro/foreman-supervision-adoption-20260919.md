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

## P3-7 appendix — PROMOTION NARROWED on real observations (pane 3, 2026-09-19)

Method: 186,449 windows of 8 consecutive tool calls mined from all 97 sessions
(`work/p3-calibration/scan_windows.py`); labels from the transcript's own
future, predicate stated verbatim: STUCK iff ≥3 consecutive identical-tool
repeats AND no write tool AND >300s elapsed AND the next user message matches
an intervention regex; HEALTHY iff a write/edit tool fired AND no intervention
match in the next 5 user messages; else AMBIGUOUS. Yield: 30 stuck / 9,776
healthy / 176,643 ambiguous (real stuck is rare — good for the fleet).
Sample: 10 + 10 + 10 spread across sessions (`real_run.py`, seed 7).
Same frozen stuck question, same 0.80 bar, same feasibility question.
30 live requests, jev-1.13.0.

Result: REAL AUC=0.750 (n=20), false-stuck 0/10, feasibility 0.783
(both classes present). Ambiguous p range 0.07–0.68.

Verdict: PROMOTION NARROWED — works on vignettes (1.000/1.000), not on real
observations (0.750 < 0.90). Two misses recorded without moving any threshold:
the primary bar missed independently of feasibility, and feasibility itself
missed its gate (0.783 < 0.80, both classes present) — the testfail regex truth
is harder on terse real outputs than on vignettes, stated as a caveat on the
arm, not a rescue of the verdict. What HOLDS on real data: the safety half
(0 FP at 0.80 in both regimes) and the ambiguous band behaving like a boundary.
Representation weakness disclosed: many real windows carry unknown ('?') tool
names from tool_execution_start rows, which may depress AUC.
UP-R7 moved off rung 5 by its author per the unit brief; vignette PROMOTE
stands as a decision-shape result only.

NO-CLAIM (P3-7): labels are predicate-mechanical (intervention regex,
write-tool list), not human review; n=20 scored; one model, one run each.

## Prevalence appendix — checked myself, it holds (pane 3, 2026-09-19)

Conductor's prevalence argument, verified from my own real_scores.jsonl rather
taken on authority: at 80% recall on the stuck sample (8/10), sample FP is 3/10.
Scaled to the mined population (30 stuck of 186,449 windows): ~24 true catches
against ~55,791 false alarms, roughly 1:2300. Even at the sample's 0-FP point
the n=10 upper bound leaves thousands-to-one. At 0.016% prevalence the 0.750
separator is unusable at any threshold that catches a meaningful fraction —
suppressing FP to parity (~30) demands a threshold that also zeroes recall.
Consequence, stated as my own conclusion: supervision on this signal needs the
base rate changed (trigger only in already-suspicious contexts) or a far
stronger separator; threshold choice cannot fix prevalence. oracle-kit
self-test green 1/1 file-level (node --test work/oracle-kit/test.mjs).
