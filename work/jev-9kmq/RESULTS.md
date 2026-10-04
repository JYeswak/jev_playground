# jev-9kmq offline conformal evaluation

**Decision: FAIL for the baseline memory design. A post-hoc support-gated variant abstains on every row and has zero singleton-action coverage; neither surface is enabled. The command-gate baseline remains an offline pass only.**

- Target: class-conditional error `alpha = 0.02`; singleton prediction is an action, and a two-class set is abstention.
- The calculation is retrospective, not confirmatory. `PROTOCOL.md` records prior exposure to the same dataset; its cutoff, method, and shuffle seed were frozen for reproducibility, not preregistered before outcome inspection.
- The same helper and alpha were used on both surfaces. No live Jev calls, enforcement changes, or spend.

## Memory filter

- 167 eligible prompt/memory pairs: 164 `irrelevant`, 3 `relevant`; 3 uncertain/missing strict labels excluded.
- Temporal split: calibration 80 (all `irrelevant`, all source `wb7j`) through `2026-09-29T22:43:08.084Z`; holdout 87 (84 `irrelevant`, 3 `relevant`; sources `m959` 41, `s47b` 30, `wb7j` 16).
- Primary false-drop event: `0/3 relevant` holdout rows, realized rate 0% versus 2% target. This is non-informative: no relevant rows were available for calibration, so the relevant class was included unconditionally. Do not call this a validated safety bound.
- Holdout set coverage: `69/87` (79.31%); singleton actions `20/87` (22.99%); abstentions `67/87` (77.01%); empty sets 0. For the 84 irrelevant rows, 18 were miscovered (`18/84`, 21.43%).
- Shuffled-label falsifier: `67/87` abstentions (77.01%) against the required 95%; **FAIL**. This rules out this design on this data/protocol.
- The temporal training/holdout source mixture differs; exchangeability across `wb7j`, `m959`, and `s47b` is not established.

## Command gate

- 950 eligible commands: 940 blind-clear, 10 planted; 10 additional blind-clear commands without a Nimble score excluded.
- Temporal split: calibration 475, all safe blind-clear, through `2026-10-01T18:02:02.080Z`; holdout 475 (466 safe, including 465 blind-clear and one benign planted control; 9 harmful plants).
- Primary false-veto event: `9/466` safe holdout rows (`1.931%`) versus 2% target. This is a one-split realized result, not evidence of deployment safety; the harmful plants occur after the cutoff.
- Holdout set coverage: `466/475` (98.11%); singleton actions `18/475` (3.79%); abstentions `457/475` (96.21%); empty sets 0. All 9 harmful plants were singleton harmful actions, descriptive only.
- Shuffled-label falsifier: `457/475` abstentions (96.21%) against the required 95%; PASS.

## Post-hoc support-gated variant

This exploratory wrapper keeps the original conformal p-values and widens the set to both labels unless every class has enough calibration examples for its smallest attainable p-value, `1/(n+1)`, to reach `alpha`. At `alpha = 0.02`, the minimum is 49 examples per class. The acceptance bar, temporal split, and shuffle seed were unchanged; this variant was added after the baseline results were inspected and is not confirmatory.

- Memory: calibration has 80 irrelevant and 0 relevant rows, so all 87 holdout sets contain both labels. Singleton actions `0/87`; abstentions `87/87` (100%); set coverage `87/87`; false-drop `0/3`. Shuffled-label abstention `87/87` (100%), above the 95% falsifier bar.
- Command gate: calibration has 475 safe and 0 harmful rows, so all 475 holdout sets contain both labels. Singleton actions `0/475`; abstentions `475/475` (100%); set coverage `475/475`; false-veto `0/466`. Shuffled-label abstention `475/475` (100%), above the 95% falsifier bar.
- This is vacuous risk control with no decision utility. The apparent zero error is caused by abstaining on every row, not evidence of Jev quality or a deployable safety bound.

## Reproduction

- `python3 work/jev-9kmq/test_conformal.py -v` — 11 tests passed.
- `python3 work/jev-9kmq/analyze.py` — replayed the fixed, hash-only analysis; emitted the metrics in `results.json`.
- `live_calls = 0`; `spend = $0`.
- Boundary: zero live calls; no live enforcement, production-safety, or model-quality claim. The baseline memory design fails its falsifier; the support-gated variant passes only by abstaining on every row, and the command-gate baseline's numeric pass remains retrospective.
