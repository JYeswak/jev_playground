# PokéJev leaf-value dev loop

**Lane:** offline; committed Stage B data only. No live requests and no new battles.
The score is the chosen leaf value against the eventual `results-abyssal.won` outcome.
Bootstrap resamples whole battles (5,000 replicates, seed `20260927`) to avoid treating
correlated decisions from one battle as independent.

| Component | Decisions | Battles | Positive | Negative | AUC (95% CI) | Fallback decisions |
|---|---:|---:|---:|---:|---:|---:|
| leaf value | 2,060 | 95 | 1,192 | 868 | 0.5371 [0.5042, 0.5700] | 209 |

The Stage B dev pool contained 2,653 decisions. The component score excludes 209 fallback
decisions and 384 missing/unusable decision rows. This is a descriptive dev signal only;
no battle-level conclusion or live-arm authorization follows from it. Candidate values not
chosen are not treated as counterfactual labels.

Machine-readable receipt: `leaf-value-dev-v1.json`.
