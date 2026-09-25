# PokéJev leaf evaluator — held-out receipt

**Status:** `live-verified (N=2,274)` for the held-out Jev arm; no battle was run.

- Fit: frozen dev rows only (`N=2,060`, 95 battles), using the committed preregistration and Arm C implementation at commit `9ee47e5` plus the held-out-mode change in this receipt commit.
- Held-out: 95 whole battles, 2,274 eligible decisions; 1171 positive and 1103 negative labels; 172 fallback and 395 unusable rows excluded; 0 missing replay turns.
- Model: `jev-1.13.0`; 2,274 held-out requests, 1,439,630 input tokens, 125,070 output tokens, documented Jev spend `$0.060464460`, 0 failures.
- Bootstrap: whole-battle, 5,000 replicates, seed `20260925`.

## Frozen A/B/C comparison

| Arm | Held-out N | Battles | Positive | Negative | AUC (95% CI) |
|---|---:|---:|---:|---:|---:|
| A_action_prior | 2274 | 95 | 1171 | 1103 | 0.5642 [0.5357, 0.5929] |
| B_leaf_value | 2274 | 95 | 1171 | 1103 | 0.5663 [0.5264, 0.6075] |
| C_code_only | 2274 | 95 | 1171 | 1103 | 0.7015 [0.6119, 0.7805] |
| C_code_plus_noul | 2274 | 95 | 1171 | 1103 | 0.7132 [0.6233, 0.7893] |

## Decision

The preregistered promotion bar is held-out AUC ≥ 0.65 with bootstrap lower bound > 0.60. C code+Noul passes: AUC `0.7132`, lower bound `0.6233`. C code-only also passes the bar. A and B are deterministic comparator floors and do not meet the bar.

This receipt authorizes consideration of a separate battle preregistration; it is not a battle result. No causal claim, counterfactual leaf claim, or paid comparator is made.
