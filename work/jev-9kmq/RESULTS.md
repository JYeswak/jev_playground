# jev-9kmq offline conformal evaluation

**Decision: FAIL for the memory filter; gate is an offline pass only. Do not enable either surface from this result.**

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

## Reproduction

- `python3 work/jev-9kmq/test_conformal.py -v` — 9 tests passed.
- `python3 work/jev-9kmq/analyze.py` — replayed the fixed, hash-only analysis; emitted the metrics in `results.json`.
- `live_calls = 0`; `spend = $0`.
- Boundary: no live enforcement, production safety, or model-quality claim. Memory fails the acceptance falsifier; gate's numeric pass does not override the retrospective exposure or exchangeability limitations.
