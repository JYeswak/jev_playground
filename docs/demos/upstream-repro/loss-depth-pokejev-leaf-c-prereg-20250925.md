# PokéJev loss-depth: leaf evaluator Arm C preregistration

Status: **PREPARED-NOT-MEASURED**. Commit this file before the first Jev Noul call.

## Question

Can a leaf evaluator built from explicit battle-state features plus a small fixed set of Jev Nouls predict the eventual battle outcome better than the existing absolute leaf value (Arm A) or the state-augmented leaf loop (Arm B), without using held-out battles during fitting?

Pattern: **composite scoring** (the local code features and Nouls are independent signals combined by a logistic model). Primary source: `docs-mirror/typesafe/patterns/composite-scoring.md`. Prior art: TypeSafe's cookbook patterns in `docs-mirror/typesafe/cookbooks/consistency_noul_cookbook.md` and the existing Stage B harness at `work/poke-jev/stage_b.py`.

## Frozen data and split

- Source: committed `work/poke-jev/stage-b/decisions-abyssal.jsonl`, `results-abyssal.jsonl`, and replay HTML referenced by the result rows.
- Eligible row: Stage B decision with `fallback` absent, a finished boolean battle result, and a chosen leaf value. Each decision row gets the eventual `won` label; rows from the same battle are clustered.
- Split: `work/loss-depth/pokejev-components/decision-split-v1.json`, whole battles only. Fit/dev uses `stage_b.dev_battles`; score/held-out uses `stage_b.heldout_battles`. No held-out row, replay, label, or Noul answer is used while fitting or selecting the model.
- Existing baselines are frozen: Arm A is the chosen absolute leaf value; Arm B is the preregistered state-augmentation dev loop. Report their existing held-out AUCs beside C; do not retune them after seeing C.

## Arm C features

The feature extractor is deterministic and keyless. It reads replay events only up to the start of each decision turn, never future events. Features are numeric and standardized using dev rows only:

1. `hp_weighted_remaining`: sum of known own-team current-HP fractions, divided by six; fainted is 0 and unseen roster entries are not imputed as healthy.
2. `status_count`: number of known own-team nonvolatile status conditions at the decision boundary, divided by six.
3. `hazard_count`: own-side active hazards among Stealth Rock, Spikes, Toxic Spikes, and Sticky Web, divided by four.
4. `speed_order_rate`: Laplace-smoothed fraction of prior turns in which the own side's first observed action preceded the opponent's first observed action; 0.5 when no paired action exists.
5. `ko_threat`: `1` when the committed damage-calculator control (`decision.tool`) supplied a legal damage-calculator order at this decision, otherwise `0`; this is a harness signal, not a claim that the move always KOs.

Boundary: replay HTML does not expose a complete hidden state for unseen Pokémon, so the first feature is known-team HP only. The extractor must report parse coverage and exclude a row rather than fabricate a feature when its turn boundary cannot be located.

## Fixed Jev Nouls

For each eligible row, one pinned `jev-1.13.0` request asks these three Nouls over the exact serialized code-feature state, current legal-option labels, chosen damage-calculator signal, and decision turn:

- `ko_now`: “Can our active Pokémon secure a knockout with a legal action this turn?”
- `danger_now`: “Is our active Pokémon in immediate danger of being knocked out this turn?”
- `switch_needed`: “Is switching necessary to avoid a materially worse position this turn?”

Each uses `criteria={"true": "...", "false": "..."}` frozen here. A missing key, failed request, malformed answer, or non-finite value excludes that row from the Noul arm and is reported; it is never imputed. Noul outputs are the three numeric probabilities in `[0,1]`. The API lane is live only; code features and all scoring remain keyless.

## Model and analysis

- Fit `sklearn.linear_model.LogisticRegression` with an intercept, standardized numeric columns, `penalty="l2"`, `solver="liblinear"`, `C=1.0`, and `random_state=20260925`. These settings are fixed before Noul calls; no hyperparameter search.
- Run a 5-fold `GroupKFold` diagnostic on dev battles only and report mean/std ROC AUC. It does not select a model or alter the held-out fit.
- Fit once on all eligible dev rows, then score held-out rows once. Primary metric: row-level ROC AUC with battle-cluster bootstrap (5,000 resamples, seed `20260925`) for a 95% interval. Also report battle count, rows, parse/Noul exclusions, class counts, and model calls/input tokens/spend.
- Fit a `statsmodels.api.Logit` with the same standardized columns on dev rows for coefficient estimates and 95% Wald intervals. These intervals describe the fitted association; they are not causal evidence and do not replace held-out AUC.
- Use SHAP only as a descriptive audit of the fixed held-out fit, with a dev-row background, explicit probability output, additivity check, feature means, and SHAP version. It cannot select features or change the model.

## Promotion bar and stop rules

C is a useful leaf evaluator only if held-out AUC is at least `0.65` and its bootstrap lower bound is above `0.60`; otherwise report the model limit and do not use it in a battle. A/B/C are reported side by side regardless of the result. No battle arm may start until this table is sent to pane 1 and a new battle preregistration is written.

Stop the Noul run on HTTP 402/billing exhaustion, malformed schema, or an unbounded retry; commit partial rows as `PREPARED-NOT-MEASURED` with exact exclusions. Spend is reported at the documented `$0.042 / 1M input tokens`; no comparator is used.

Boundary: this is a component evaluator, not a battle result. It does not establish causal value, does not label unchosen counterfactual leaves, does not compare to a paid LLM, and does not authorize the 200-battle arm.
