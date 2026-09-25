# PokéJev loss-depth next-arm preregistration

Status: **PREPARED-NOT-MEASURED**. This file must be committed before the first live request for the arm below. It is the preregistration recommended by `loss-depth-pokejev-20260925.md`.

## Question

Does the loss-depth ordering observed against the committed Abyssal run persist against a different, fixed opponent policy, or is the large opponent-model bucket specific to Abyssal's move distribution?

The keyless autopsy's four-way counts among 85 Jev-active first-faint rows were:

- action prior: 31/85 (36.5%);
- opponent model: 30/85 (35.3%);
- leaf value: 19/85 (22.4%);
- missing state: 5/85 (5.9%).

The top two are a tie for practical purposes. The next arm therefore changes the opponent policy, not the Jev prompt or player code, to test whether opponent-model attribution generalizes.

## Fixed arm

- Opponent: `onestep` (`poke_env`'s pinned `OneStepPlayer`), not a chat-model comparator.
- Battles: **200**, using the existing Stage B `PAIR_SEED` and ordered `k=0..199`.
- Jev model: **`jev-1.13.0`**, explicit model id.
- Player implementation: unchanged from the committed Stage B player.
- Decision deadline/retry behavior: unchanged from the committed Stage B player.
- Data paths: `work/poke-jev/stage-b/results-onestep.jsonl`, `decisions-onestep.jsonl`, and `replays-onestep/`.
- Analysis command after the run: `python3 work/loss-depth/pokejev/autopsy.py --arm onestep --json`.
- No paid comparison arm. Jev service spend is the only live spend.

The observed Abyssal arm used 33,250,699 input tokens for 200 active battles, or approximately `$1.40` at the recorded `$0.042/M` input rate. The planned arm estimate is **$1.40**, with a preregistered expected ceiling of **$3.00**. This is an estimate, not a result.

## Acceptance and analysis

The arm is analysis-eligible only if all 200 result rows are present and finished, there are zero harness errors, zero own-side time losses, and the live decision log records the pinned model. Any TypeSafe 402/credit fallback, timeout fallback, or other service failure is reported separately and excluded from the four-way denominator; it does not become a model hypothesis.

For every loss, use the first own-side faint as the turning point and apply the exact fixed rules in the autopsy script. Report:

1. total battles, wins, losses, finished rows, time losses, and fallbacks;
2. Jev-active loss denominator and all four counts with Wilson 95% intervals;
3. the complete per-loss table and replay paths;
4. model id, Jev call count, input tokens, spend, p50/p95/max decision latency, and wall time;
5. the comparison with the Abyssal 31/30/19/5 counts.

No success threshold is assigned to a category share after seeing this arm. The predeclared interpretation is:

- **Replication signal:** action prior and/or opponent model remains the top two categories in the new arm, with the new counts and intervals reported.
- **Opponent-specific signal:** opponent model drops below both action prior and leaf value, or its direct-surprise rate materially shifts while the action-prior/leaf relationship remains similar.
- **No causal claim:** this arm is observational. It cannot prove that changing the named component improves win rate. A causal intervention requires a separate preregistration.

## Boundary

This arm does not compare Jev to an LLM, does not alter the action prior or opponent candidate policy, and does not reuse the Abyssal battle outcomes as labels. It is a held-out opponent-policy replication of the diagnostic taxonomy, not a win-rate improvement claim.
