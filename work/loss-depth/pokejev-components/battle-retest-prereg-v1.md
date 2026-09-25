# PokéJev LOSS DEPTH step 4: frozen-alpha battle retest

**Status:** `PREPARED-NOT-MEASURED`. This file is committed before any battle arm
using the frozen mixtures. No live request or battle is authorized by this file alone.

## Question

Does replacing Jev's raw distributions with the frozen development-fit mixtures improve
or preserve the Stage B battle result against Abyssal, under the same local Gen 9 OU Clock
harness and the same 70% kill line?

## One design change

Only the distributions consumed by the existing search are changed:

- action-prior slot: `p = 0.40 * p_jev + 0.60 * p_usage_floor`;
- opponent-model slot: `p = 0.25 * p_jev + 0.75 * p_usage_floor`;
- leaf-value slot: unchanged from the committed Stage B implementation.

The alphas are not fit during the battle run. They are read from
`frozen-alpha-v1.json`, fit on the Stage A dev side only and committed at
`c762a9b`. The held-out component result is recorded in `heldout-v1.json`; it is not
used to alter either alpha.

`p_usage_floor` is the existing deterministic usage-frequency floor, normalized over the
current legal option set with the same calibration constants as the component scorer.
No prompt, candidate set, search depth, tie-break, clock, team, or leaf evaluator changes.

## Fixed protocol

- opponent: pinned `AbyssalPlayer`;
- live battles: **200**;
- zero-call control: **200** control battles on the identical ordered `(k, team pair)`
  list and the same new seed;
- pair seed: **20260926**, intentionally different from Stage B's `PAIR_SEED=20260925`;
- team pairing: the existing Stage B `teams_for(k)` protocol, with the pair seed changed
  only for this arm;
- clock: existing `gen9ouclock` format and Stage B per-decision deadline;
- model: explicit `jev-1.13.0`, recorded on every live decision row;
- outputs: `work/loss-depth/pokejev-components/battle/stage-b/results-abyssal-mix-v1.jsonl`, `decisions-abyssal-mix-v1.jsonl`,
  `replays-abyssal-mix-v1/`, plus matching `-control` paths; each result and decision row records
  the SHA-256 map of the imported Stage B modules.
- budget: **USD 3 maximum** for Jev input-token spend; expected spend is approximately
  the Stage B live-arm estimate, USD 1.40 for 200 battles;
- stop rule: stop the live arm immediately on any TypeSafe HTTP 402 / credit-exhaustion
  response. Do not retry past the 402 or silently continue with a new model. Record the
  partial receipt and mark the arm not analysis-complete.

## Fallback rule

Every fallback decision is counted and reported by reason and by battle. A fallback-bearing
battle remains in the primary intention-to-treat win-rate denominator; no fallback result is
silently imputed or excluded. The primary result therefore answers the operational question
of the complete arm, including its service failures. A secondary no-fallback-only table MAY
be reported as descriptive diagnostics, but it cannot replace the primary result or its
70% verdict. Fallback rows are excluded from component-cause attribution only.

A harness-error row, missing result, or unfinished battle is not a loss and does not count as
a completed battle; the arm is incomplete until all 200 live and 200 control result rows
are present. Any 402 stops the live arm as above. Other fallbacks do not stop the arm but
remain visible in the receipt.

## Acceptance and fixed bar

Use the existing Stage B bar without retuning:

- `KILL` if live win rate is `< 0.70` or own-side time losses exceed `1%`;
- `PASS` only if live win rate is `>= 0.84` and own-side time losses are zero;
- otherwise `FAIL`.

Report the live-control win-rate difference descriptively; it is not a second success bar.
Also report finished rows, wins/losses, own/opponent time losses, fallback decisions and
fallback-bearing battles by reason, decision count, Jev call count, per-call model set,
input tokens, spend at `$0.042/M`, p50/p95/max decision latency, and wall time. Record the
new pair seed and verify that no Stage B `k`/replay/result is reused.

## Boundary

This is one intervention against one new 200-battle Abyssal sample and a same-seed
zero-call control. It does not retest revealed state, items, speed, or a relative question;
those are later live arms. It does not change or re-fit the leaf-value component. A result
with a 402 or incomplete rows is a stopped partial run, not evidence for the 70% bar.
