# Calibration answers (jev-2zbl, 2026-10-02; script calibrate.py, seed 20261002)

Full table: calibration.json (7 tasks, dev-fitted cut + isotonic/Platt on held).

| task | n | base | Brier | ECE | AUC | mean_p | dev-cut->held acc |
|---|---|---|---|---|---|---|---|
| msax-v1 | 81 | 0.556 | 0.370 | 0.326 | 0.377 | 0.250 | 0.561 (cut 0.05; bar 0.70 NO) |
| m959-noul | 50 | 0.220 | 0.460 | 0.520 | 0.521 | 0.740 | 0.720 (cut 0.95) |
| webscreen-rowmax | 423 | 0.811 | 0.228 | 0.336 | 0.968 | 0.474 | 0.889 (cut 0.10) |
| d1-read | 248 | 0.230 | 0.268 | 0.243 | 0.446 | 0.453 | 0.750 (cut 0.85; bar 0.60 PASS*) |
| triage-ignore | 250 | 0.608 | 0.260 | 0.231 | 0.732 | 0.795 | 0.712 (cut 0.90; bar 0.75 NO) |
| ztfe-ignore | 250 | 0.616 | 0.278 | 0.254 | 0.704 | 0.815 | 0.648 (cut 0.40; bar 0.75 NO) |
| v10-inapplicable | 118 | 0.475 | 0.191 | 0.230 | 0.928 | 0.705 | 0.831 (cut 0.75) |

Isotonic/Platt on dev cut Brier everywhere (e.g. webscreen 0.251->0.085, msax
0.373->0.242, v10 0.201->0.096); Platt lifted msax held AUC 0.35->0.65.

## (1) Is the default-answer bias systematic?

Yes in level, no single direction. Every task is miscalibrated in level
(ECE 0.23-0.52): d1 over-predicts read 2x (0.45 vs 0.23 base); m959 over-predicts
relevant 3x (0.74 vs 0.22); triage/ztfe over-predict ignore (~0.80 vs ~0.61);
msax UNDER-predicts retry (0.25 vs 0.556, cautious fix_first default, AUC 0.377
inverted). The bias follows neither wording polarity nor caution uniformly; it is
task-specific overconfidence toward the question's posited or safe option.

## (2) Does a dev-fitted cut turn any FAIL into a PASS on held-out?

One, with a plain caveat: d1-read dev cut 0.85 -> held (seeded half, n=124)
accuracy 0.750 >= 0.60 bar. Caveat: this reframes the 8-way router as a binary
P(read) cut on a seeded half of the original held set -- a new decision rule that
passes, not a rescue of the argmax router. All others: NO (msax 0.561, triage
0.712, ztfe 0.648 stay below bars; m959 keep-precision untouched by accuracy cuts).

## (3) Which tasks are well calibrated (likely our wins)?

None in level (ECE floor 0.23). Well-DISCRIMINATING: webscreen-rowmax (AUC 0.96)
and v10-inapplicable (AUC 0.93) -- ranking is excellent while thresholds/harm
bounds are the failure point. These are exactly the enforced/near-win surfaces.
Triage/ztfe middling (AUC 0.70-0.76); msax/m959/d1 at or below chance in rank.
