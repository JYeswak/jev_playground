# Jev-PUCT on Jericho — preregistration

Bead `jev-jy7t.1.4`. Author: CopperHeron (pane 2). This file is fixed before any Jev
request. No live call has been made. The local Laya alternative is not used, started, configured,
or treated as a comparator or fallback.

## Question and prior art

This is the **Gaming** cell of TypeSafe's use-case map, with Jev used for **Ranking** valid
actions. It ports MC-DML's action-prior slot: a Choice over Jericho's code-owned valid actions
replaces the unavailable token log-probabilities. The search, rollout, reward, and action space
remain MC-DML's.

- MC-DML: `winni18/MC-DML @ 7f1312225c4a93cb7c3c6e93c4a6b9e0f739a0df`, read-only source
  reference; Table 4 no-memory LLM-prior PUCT targets 31.67 / 51 / 320 for Zork1 / Deephome /
  Detective, and Table 1 full targets 48.66 / 67 / 346.67.
- Jericho: `microsoft/jericho`, version 3.3.1 in the pinned Docker image.
- Game ROM source: `BYU-PCCL/z-machine-games` archive SHA
  `bfd7544aa1f50549fc327bd4eb3bc8144bfd80ea`; Docker verifies the three ROM SHA-256 values.
- Jev client: official `typesafe-sdk-python` 0.7.1 (`upstream/typesafe-ai/typesafe-sdk-python`
  pinned at `0ffd094`), model `jev-1.13.0`.
- Local primary sources: `docs-mirror/typesafe/primitives/choice.md`,
  `docs-mirror/typesafe/api.md`, `docs-mirror/typesafe/concepts/use-case-map.md`.

## Fixed protocol

Games are `zork1`, `deephome`, and `detective`. Each arm runs seeds **1, 2, and 3**, one run
per seed. The seed list is fixed before any arm starts. Per-game settings are the MC-DML/Jang
fixed-depth ablation in `work/jev-if/puct.py`: maximum real steps 35 / 35 / 50, maximum search
depth 10, `c_puct` 50 / 20 / 200, discount 0.95, and **50 × number of valid actions** PUCT
simulations per real step. No dynamic pruning (`--dp`), no cross-trial memory, and no LLM rollout.
The valid-action handicap and Jericho save/restore path are retained.

The Jev arm makes one request for each newly expanded non-singleton search node. Each request has
one Choice question whose criteria are exactly the current valid action strings. The Jev
probabilities go through MC-DML's fixed transform `softmax(max(log(p), -5) / 5)`. The client pins
`https://api.typesafe.ai`, never Laya or another endpoint, and refuses a missing/rejected key;
there is no uniform fallback for an authentication failure. Malformed non-auth responses are
recorded as a failed node and use the explicitly documented uniform-prior fail-safe.

Arms:

1. `uniform`: uniform-prior PUCT, the no-model floor.
2. `random`: seeded uniform valid-action policy, reported as a secondary floor.
3. `look`: repeated `look`, reported as a secondary floor.
4. `jev`: the Jev Choice prior, otherwise the same search path as `uniform`.

The primary comparison is `jev` versus `uniform` on the same game and seed. `random` and `look`
are not substituted into the primary bar.

## Frozen bar

**PASS only if all of these hold:**

- Jev reaches at least the MC-DML no-memory targets on all three games:
  Zork1 `>=31.67`, Deephome `>=51`, Detective `>=320` (mean final score over the three fixed
  seeds); and
- on Zork1, Jev's mean final score is at least **5 points above** the uniform PUCT mean.

The stretch comparison is the MC-DML full target 48.66 / 67 / 346.67. The preregistered kill is
Jev no better than uniform PUCT on at least two of the three games. A kill is a result, not a
prompt or threshold change. The bar, seeds, game settings, question, model, retry policy, and
aggregation do not change after the first live request.

Report per-seed rows, means, sample standard deviation and standard error, final score, maximum
score, completed steps, engine `done`, prior requests/calls/failures, input/output tokens,
wall-clock seconds, and billed spend. Report every resolved model id. The receipt must state any
incomplete or billing-error run and must not score a partial run against the bar.

## Call and spend estimate

The source estimate is **80,000 Jev prior requests per completed game run** (the 100-step ×
roughly-800-simulations upper-envelope from the design notes; the actual frozen runs have lower
35/35/50 step caps and report their observed request count). The TypeSafe service limit is 1,200
requests per minute, so this envelope is at least 66.67 minutes, rounded up to **67 minutes per
game-run**, and nine serial game-runs are at least **10 hours** of attended wall time. The
preregistered live arm is 3 games × 3 seeds, so the exact budget estimate is:

```text
9 game-runs × 80,000 requests/run = 720,000 TypeSafe requests
720,000 × 700 input tokens/request = 504,000,000 input tokens
504,000,000 × $0.042 / 1,000,000 = $21.168, rounded to $21.17
```

This is a cap/estimate, not an observed result. Actual calls and spend are read from the final
rows and the TypeSafe usage response. The uniform, random, and look arms make no Jev requests and
cost $0. The first live checkpoint, if authorized, is exactly one **uncached** `jev` Zork1 run at
seed 1; remaining runs stay stopped until that checkpoint's observed request count, tokens,
resolved model, wall time, and spend are reported and the parent pane confirms continuation.

### Cache decision

A prior cache keyed by `sha256(canonical serialized state + exact valid-action list)` was
considered. It is **not enabled in this preregistered primary arm**: the first live run is the
uncached baseline, so a later cache can be introduced as the only changed variable rather than
silently mixing cache behavior into the first measurement. Therefore this receipt reports no cache
hit rate; adding the cache requires a new preregistration that retains this uncached arm.

## Keyless gates before live

```bash
PYTHONPATH=work/jev-if python3 -m unittest work/jev-if/test_puct.py

run_dir="var/agent-tmp/jev-jericho-keyless-$(date +%s)"
mkdir -p "$run_dir"
docker run --rm --platform linux/arm64 -v "$PWD/$run_dir:/results" jev-if:wave1 \
  --game zork1 --arm uniform --seed 1 --out /results/zork1-uniform-s1.jsonl
```

The keyless arm is required before the live arm. It must finish with a final row, no error row,
and `prior_calls=0`, `prior_failed=0`, and `$0`. The offline unit suite must be green. A fake-asker
run may be used only as a keyless call-count/latency feasibility probe and is not scored.

## Keyless checkpoint

The required offline unit suite was green: **32/32**. The required keyless uniform run completed
with no error row:

```text
game=zork1 seed=1 status=ok steps=9 done=true
final_score=25 max_score=35 wall_s=303.826
prior_requests=257 prior_calls=0 prior_failed=0
input_tokens=0 output_tokens=0 spend=USD 0
```

This is `offline-verified` for the uniform arm only. It is not a Jev result and does not
authorize a live call. The output was written under the ignored `var/agent-tmp/` scratch root.

## Live commands

Build the image from this tree with the pinned Dockerfile. Use one foreground invocation at a time;
no unattended loop or retry wrapper is permitted. The first authorized live command is:

```bash
run_dir="var/agent-tmp/jev-jericho-zork1-live-s1-$(date +%s)"
mkdir -p "$run_dir"
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  docker run --rm --platform linux/arm64 \
  -e TYPESAFE_API_KEY \
  -v "$PWD/$run_dir:/results" jev-if:wave1 \
  --game zork1 --arm jev --seed 1 --out /results/zork1-jev-s1.jsonl
```

The remaining eight Jev runs are held until the first run's actual calls, input tokens, resolved
model, wall time, and spend are reported and the parent pane confirms continuation. A TypeSafe
HTTP 402 billing error is terminal for this experiment: record the completed rows and stop; do not
retry or score an incomplete run.

## Non-claims

This is not a claim that Jev beats MC-DML's full system, GPT, XTX, TALES, or TextQuests. Those
protocols use different action spaces, memory, or rollout settings. It is not an omp integration;
this unit is a public runnable experiment. It is not a comparator-model result: paid comparisons
are stopped. It does not use Laya. A live result is only `live-verified (N=...)` after the exact
rows, model, tokens, and spend are recorded; keyless rows are `offline-verified` only.
