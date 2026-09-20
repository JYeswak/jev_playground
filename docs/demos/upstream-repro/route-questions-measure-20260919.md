# omp-jev-route questions: measured, both discriminate (2026-09-19)

## Method

`work/omp-jev-route/measure.mjs` (template: `work/omp-jev-failure/measure.mjs`). Nine
hand-built prompts with known tiers, run three times identically (27 systemOne calls, both
questions per call). Each question must beat its own always-no / always-yes constant.
Rule stated before running: DEGENERATE = same verdict on every case; otherwise must beat the
better constant to DISCRIMINATE, else WEAK.

## Result

- `needs_heavyweight`: 8/9, said-yes 5/9, constants 5/9 and 4/9, spread 0.83 → DISCRIMINATES.
- `mechanical`: 8/9, said-yes 4/9, constants 4/9 and 5/9, spread 0.90 → DISCRIMINATES.
- Pooled 16/18 vs coin flip 9.0. No verdict within 0.10 of threshold. Zero transport errors.
- Drift: 0 flips; per-cell spread ≤ 0.04, most cells bit-identical across runs. The model is
  near-deterministic on these inputs — convenient for measurement, and a reason not to mistake
  stability for accuracy.
- Trap (`trap-bump-version`, "Just bump the version to 2.4.1"): both HIT on prompt-only
  evidence (light). The judge stays calibrated to what the prompt supports; it does not
  hallucinate hidden difficulty.
- The one miss is shared: "What does this function do?" scores needs_heavyweight 0.62
  (MISS) and mechanical 0.13 (MISS). Read-only Q&A falls between the two questions — neither
  heavyweight work nor a mechanical edit. A WEAK spot, not a degenerate question: a third
  category exists that this pair cannot name. Noted, not cut; cutting needs a replacement
  question with its own measurement, which is a separate unit.

## Decision

Cut nothing — nothing is degenerate. `src/index.ts` and tests unchanged by this unit.
Observe-only stands regardless: this measures calibration on hand-built prompts, and our own
backtest found the upstream savings claim inverts on our corpus.

## NO-CLAIM

Nine prompts I wrote knowing the answer; my phrasing may make heavy cases legible and light
cases trivially so. Says nothing about real turn traffic. Does not show the scores predict
anything — only that they are not constants.
