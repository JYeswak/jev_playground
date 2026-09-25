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
### Wall-time amendment (before any Deephome live run)

The completed keyless runs measured 303.826 s for a 9-step Zork1 episode and 155.309 s for a
40-step Detective episode. The Deephome keyless attempt reached only five complete steps in an
outer 1,800-second command budget and had no final row. This is a harness-time finding, not a
partial result.

The Deephome live arm therefore has a fixed **14,400-second (four-hour) per-run wall budget**,
enforced by a foreground `timeout 14400` wrapper. This is intended to cover the roughly 3.5-hour
keyless projection from the first five Deephome steps plus Jev request latency. If the wrapper
returns 124, the process is killed, or the output has no `kind=final` row with `status=ok`, that
seed is **NOT-SCORED**; its completed partial steps may be used only to explain the timeout and
must not be averaged into the bar. Deephome remains in scope under this budget; dropping it
requires a further preregistration amendment, not silent omission.

The live Deephome command shape is:

```bash
timeout 14400 infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  docker run --rm --platform linux/arm64 \
  -e TYPESAFE_API_KEY \
  -v "$PWD/$run_dir:/results" jev-if:wave1 \
  --game deephome --arm jev --seed 1 --out /results/deephome-jev-s1.jsonl
```

This amendment is committed before any Deephome live call. The Zork1 and Detective runs remain
foreground and are also not scored if they lack a final `status=ok` row.

## Runtime boundary

The arm64 Jericho 3.3.1 development probe found a Frotz segfault on a separate Zork1 inventory
path; in pool mode that can hang valid-action generation. The watchdog converts a timed-out or
crashed run into an error/incomplete receipt, never a score. The completed Zork1 seed-1 checkpoint
did not enter that path. This is a known execution risk for later live rows, not evidence about
Jev quality.

## Cache decision

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

The terminal reason was independently replayed against the same image and action sequence:
`south` returned reward `-10`, `done=true`, `game_over=true`, and the engine text said
`A lurking grue ... devoured you` / `You have died`. This was a death/game-over termination,
not the 35-step cap. The Zork1 count must not be applied to the other games.

Additional keyless uniform arms:

```text
detective seed=1 status=ok steps=40 done=true final_score=300 max_score=300
wall_s=155.309 prior_requests=1023 prior_calls=0 prior_failed=0

deephome seed=1 incomplete: outer 1800-second command timeout during step 6
completed_steps=5 cumulative_prior_requests=314 prior_calls=0 prior_failed=0
no final row; not scored and not treated as a completed run
```

The Detective run completed before its 50-step cap. Deephome is too slow to complete under the
current keyless command deadline: its first five completed steps average 62.8 prior requests,
so the only honest game-specific proxy is `35 × (314 / 5) ≈ 2,198` requests per Deephome run;
this is explicitly **incomplete**, not a score or a Jev budget. Before the live checkpoint, the
uniform-count proxy for the other eight runs is therefore Zork1 `2 × 257 = 514`, Deephome
`3 × 2,198 ≈ 6,594`, Detective `3 × 1,023 = 3,069`, total **≈10,177** requests. The live Jev
seed-1 count must replace these uniform proxies before projecting the remaining eight.

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

## Live checkpoint and continuation (2026-09-25)

The uncached Jev Zork1 seed-1 checkpoint completed with `status=ok`, 9 steps, `done=true`,
final score 25/35, wall 317.530 s, 261 prior requests, 261 calls, 0 prior failures, 131,385
input tokens, 20,573 output tokens, and estimated spend `$0.005518170` at `$0.042/M` input
tokens. The resolved model was `jev-1.13.0`. Its source row was copied byte-for-byte to
`work/jev-if/rows/zork1-jev-s1.jsonl`; source and tracked SHA-256 are both
`443e7a250602e689ffad0e58722ffde580c765b1566d9c575ec3b6689a6bf991`.

Because 261 is below 3 × the keyless uniform count (771), continuation was authorized. Zork1
seed 2 completed with `status=ok`, 35-step cap, `done=false`, score 44/44, wall 1884.914 s,
1,971 prior requests, 1,941 calls, 7 prior validation failures, 1,013,756 input tokens,
182,176 output tokens, and `$0.042577752`; seed 3 completed with `status=ok`, 35-step cap,
`done=false`, score 44/44, wall 1478.798 s, 1,744 requests, 1,737 calls, 7 prior validation
failures, 860,769 input tokens, 142,078 output tokens, and `$0.036152298`. Their tracked row
SHA-256 values are respectively
`8d574380ef66de53a6e38791d3c66374fc68fdbae0bcfb0a3ea872a104fa4b34` and
`96f2478b34e3f90cc2dd29e2a050dfe8f28352c863fa4633bc4896750250365c`; both `cmp` checks returned
0.

The preregistration already names the non-auth malformed-answer behavior: it records a failed
node and uses the uniform-prior fail-safe (lines 34–39). The 7 `prior_failed` rows on each of
seeds 2 and 3 therefore require no prereg amendment; they are disclosed and are not silently
recounted as successful Jev priors.

The remaining Detective and Deephome seeds were launched concurrently in separate containers
after the Zork1 seed-3 row completed. The three Deephome processes use the committed 14,400-second
per-run wall budget. Their completion status, CPU-contention note, and any NOT-SCORED timeout
rows will be appended after all six rows settle.
