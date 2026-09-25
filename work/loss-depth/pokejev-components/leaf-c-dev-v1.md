# PokéJev leaf evaluator Arm C — dev receipt

**Status:** measured dev only; no held-out rows or battle calls were used.

- Frozen split: `decision-split-v1.json`, 95 dev battles, 2,060 eligible decisions.
- Labels: 1,192 eventual wins and 868 losses; 209 fallback and 384 unusable rows excluded; 0 missing replay turns.
- Model: `sklearn` logistic regression, standardized columns, L2, `C=1.0`, `liblinear`, seed `20260925`.
- Bootstrap: whole-battle, 5,000 replicates, seed `20260925`.
- Live Nouls: 2,060 pinned `jev-1.13.0` requests, 1,306,588 input tokens, 113,300 output tokens, documented Jev spend `$0.054876696`, 0 failures.

## A/B/C table

| Arm | N | Battles | Positive | Negative | In-sample AUC (95% CI) |
|---|---:|---:|---:|---:|---:|
| A_action_prior | 2060 | 95 | 1192 | 868 | 0.5546 [0.5240, 0.5872] |
| B_leaf_value | 2060 | 95 | 1192 | 868 | 0.5371 [0.5043, 0.5718] |
| C_code_only | 2060 | 95 | 1192 | 868 | 0.6652 [0.5933, 0.7368] |
| C_code_plus_noul | 2060 | 95 | 1192 | 868 | 0.6803 [0.6156, 0.7456] |

The A/B/C logistic bootstrap AUCs are **in-sample fit scores**: the model is fit on all dev rows and scored on those same rows. They are not held-out evidence.

## GroupKFold dev diagnostics

| Arm | Mean AUC | SD |
|---|---:|---:|
| C_code_only | 0.6260 | 0.0334 |
| C_code_plus_noul | 0.6422 | 0.0333 |

Paired per-fold Noul-minus-code deltas: `+0.0170, -0.0025, +0.0272, +0.0288, +0.0109`; mean `+0.0163`, SD `0.0128.

The preregistered held-out bar remains AUC ≥ 0.65 with bootstrap lower bound > 0.60. This dev receipt does not authorize a battle. The next run fits on dev once, freezes that fit, and scores held-out battles once.

Statsmodels coefficient estimates and 95% Wald intervals are in the JSON receipt. They describe association, not causal effects.
