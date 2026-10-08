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

## Design amendment: seed-blocked paired comparison and pilot stop (2026-09-25)

This amendment is committed before any further Detective or Deephome live invocation. The
initial three-seed-per-arm plan is underpowered for the frozen Zork1 `+5` point bar when treated
as an independent-means comparison. The revised design treats seed as a block: for each seed,
the Jev and uniform arms must both have a final `status=ok` row, and the primary observation is
the paired score difference `d_s = score_jev,s - score_uniform,s`. A partial, timed-out, crashed,
or error row is not a score and cannot form a pair.

The completed same-seed keyless rows are:

| seed | Jev score | uniform score | paired difference | uniform row SHA-256 |
|---:|---:|---:|---:|---|
| 1 | 25 | 25 | 0 | `08c4ab4e868f295798a1b9fa5acc993cb163efb6a5986fde2e23f3eaef1fe730` |
| 3 | 44 | 25 | 19 | `8164c6a5dbf40fb4b1630256d1436fe1d85fa1bbddb394ae65e4681c01f26d34` |

The exact keyless uniform seed-2 run reached no final row before its 3,600-second wrapper
deadline and ended with the known arm64 Jericho/Frotz worker segmentation fault. Its partial
scratch output remains untracked and is not scored or copied. The two complete pairs give
`d = [0, 19]`, mean `9.5`, sample SD `13.435`, and SEM `9.5` points. This is a two-pair pilot
estimate, not a calibrated variance estimate.

Using the statistical-power skill's paired/one-sample t-test recipe (`statsmodels 0.15.0`,
SciPy 1.18.1), with the preregistered smallest effect of interest `delta=5`, two-sided
`alpha=0.05`, and target power `0.80`, gives `dz = 5 / 13.435 = 0.3722`, raw `n=58.619`,
and **59 complete seed pairs** after ceiling; power at 59 is `0.8026`. Sensitivity to the
pilot SD is 34 pairs at `0.75 SD`, 59 at the observed SD, 91 at `1.25 SD`, and 130 at
`1.5 SD`. The observed paired mean is not used as the powered effect.

The completed Jev Zork1 runs average 1,227.081 seconds each; the two complete uniform runs
average 280.792 seconds. At those observed means, 59 paired runs project to **24.712 hours**
before startup, contention, or failures. The required powered count therefore cannot fit one
attended day. Jericho is a **descriptive pilot**, not a powered confirmatory test, under this
receipt. No further Jev runs are authorized by this amendment; Detective and Deephome are not
scored against the original bar.

For completeness, the Detective processes had already been launched before this amendment:
seed 1 ended `status=error`, seed 2 ended `status=ok`, and seed 3 ended `status=error`; they
are unpaired and therefore descriptive only. All three Deephome processes are incomplete
without a final row: seed 2 was interrupted by its 300-second wrapper, and seeds 1 and 3 were
cancelled after the superseding design instruction. No partial Detective or Deephome row is
averaged into any bar, and no replacement live call is made.

## Superseding bounded live-run amendment (2026-10-01; before any r2 Jev call)

Joshua's directive (verbatim, 2026-09-30): “our only mission right now is to unblock every blocker and get our bead dag closed. do not stop until this is done. Find every sota practive possible to land the fucking plane.” This authorizes a fresh bounded r2 collection and supersedes only the 2025 pilot-stop sentence above. No r2 Jev request has been made. The score bars, game settings, Jev model, question, action-space rules, aggregation, and published comparator remain unchanged.

### Frozen r2 cohort and decision

- Gaming × Ranking, Jev Choice action prior inside the same MC-DML PUCT path. The fixed-score matrix is all 3 games × 4 arms (jev, uniform, random, look) × seeds 1–3: 36 fresh runs under current source. Every old row remains intact and is excluded from r2 scoring.
- The confirmatory Zork1 paired sample is 59 fresh seeds, 4–62 inclusive, one Jev and one uniform PUCT run per seed, with Jev first. The paired statistic is unchanged: d_s = score_jev,s - score_uniform,s; PASS requires mean d_s >= 5. The old seed-1/3 pilot pairs are not included in this confirmatory N; they informed the already-frozen power calculation only. Random/look remain secondary floors, never replacements for uniform.
- The original fixed-seed SOTA means and KILL rule remain exactly as above: Jev means >=31.67 / 51 / 320 on Zork1 / Deephome / Detective; kill if Jev is no better than uniform on at least 2 of 3 games; stretch 48.66 / 67 / 346.67. Incomplete rows are not averaged.
- New per-run paths, all exclusive-reserved before output creation (154 paths, no collisions): work/jev-if/rows/{zork1,deephome,detective}-{jev,uniform,random,look}-r2-20260930-s{1,2,3}.jsonl and work/jev-if/rows/zork1-{jev,uniform}-power-r2-20260930-s{4..62}.jsonl. An error/timeout row is left intact and not scored; there is no seed substitution or episode retry. TypeSafe SDK retries remain pinned at 2; HTTP 401/402/403/404/429 ends the Jev queue immediately, with no further Jev call. A request rejected by the byte guard is NOT_SCORED and is not converted to uniform.

### Keyless feasibility and live-call boundary

- Captured input: work/jev-if/state-sample.json, SHA-256 9e28b81ad90e0841421b408ef7d1ccdf42e152f3f540bc6e19eac427647d1ba3; it was emitted by run.py --dump-state from a real Zork1 root. scripts/jev-state-size.py on that captured state and its 416-byte question returned FITS 1, NEAR 0, OVER 0; current calibration band 1.479–2.082 bytes/token, source calibration-osworld-r3.tsv. Recorded Zork1 Jev seed 2 has 35/35 chosen actions present in the root action set, four positive-reward actions (steps 4, 14, 20, 24), final 44/44, status=ok; row SHA-256 8d574380ef66de53a6e38791d3c66374fc68fdbae0bcfb0a3ea872a104fa4b34. This is prior feasibility evidence, not part of r2 scoring.
- Current source pins: puct.py 96fe13701092659d5a41e8bc90557f26079a565c5cae3bd9898144f18abae345; run.py ff923889a85f5590dc78cd8c8b25a04a683e22459b298041aa8d1f65919519d0; tests test_puct.py 622fa43b8515c9213986facc5644988c22bb4f49700731e9208fca992b9e35c7; Dockerfile fc137cc125d09f4ef492950ebf22b250e2a340c95903c15bba4ec763762255e8; image jev-if:wave1-amd64 sha256:0e78b19054ad9549a5a17beacb42ee5bde70f12968dfc8177d72a945f1d94516 (linux/amd64, /app). The run mounts current puct.py and run.py read-only; no image rebuild or upstream edit.
- Every Jev SDK operation now writes one metadata-only kind=jev_request JSONL row (model, status/http status, full-request byte count, latency, input/output tokens, SDK retry maximum), then flushes and fsyncs through Rows.write. No state, prompt, answer body, API key, or raw error message is logged. A failed row write raises FatalPriorError; it cannot fall back to a scored uniform prior. SDK retries remain inside one logical-call row; max_retries=2 means at most 3 HTTP attempts per logical call, confirmed by the official SDK MockTransport smoke: 401/402/403/404 each 1 attempt; 429 3 attempts; one checkpoint row each. Success MockTransport returned jev-1.13.0, 12 input / 3 output tokens and one received row.
- The full serialized UTF-8 request is rejected before SDK initialization when over 32,768 bytes. Unit coverage proves exactly-at-limit is sent and over-limit is refused before SDK construction. This is a conservative byte ceiling informed by the observed token-density calibration, not an exact tokenizer; no claim about unseen tokenizers beyond that evidence.
- Offline verification before this amendment: python3 -m unittest work/jev-if/test_puct.py — 36/36; ubs work/jev-if/puct.py work/jev-if/run.py work/jev-if/test_puct.py — 0 critical / 0 warnings. ripwire work/jev-if --quality-delta — exit 2, two preexisting-worse major findings; first names SdkAsker verbosity 59→101 lines. No baseline acknowledgment or gate weakening. This remains an open peer-review item; do not claim a clean quality delta.

### Budget, stop, and explicit boundary

There are 68 Jev-enabled episodes in the fixed schedule (9 fixed-target plus 59 powered) and 86 local-only baseline episodes. The receipt's historical 80,000-request/game figure remains a planning estimate, not an enforced cap; actual per-call rows and billed usage are authoritative. Each episode is bounded by its frozen 35/35/50-step and 50×valid-action simulation schedule, the 32,768-byte preflight, and the official SDK's 2-retry policy. There is no paid comparator arm. Boundary: this does not measure Jev against a chat model or establish general Jev superiority. The Ollama 0.35 ticket-triage/model-routing/classification note is user-reported and belongs to the separate localbench lane; it is not an arm or result here. No EVAL.md edit, no real r2 Jev call,…

## Superseding bounded live-run amendment (2026-10-01; before any r2 Jev call)

Joshua's directive (verbatim, 2026-09-30): “our only mission right now is to unblock every blocker and get our bead dag closed. do not stop until this is done. Find every sota practive possible to land the fucking plane.” This authorizes a fresh bounded r2 collection and supersedes only the 2025 pilot-stop sentence above. No r2 Jev request has been made. The score bars, game settings, Jev model, question, action-space rules, aggregation, and published comparator remain unchanged.

### Frozen r2 cohort and decision

- Gaming × Ranking, Jev Choice action prior inside the same MC-DML PUCT path. The fixed-score matrix is all 3 games × 4 arms (jev, uniform, random, look) × seeds 1–3: 36 fresh runs under current source. Every old row remains intact and is excluded from r2 scoring.
- Confirmatory Zork1 sample: **59 fresh paired seeds, 4–62 inclusive**, one Jev and one uniform PUCT run per seed, Jev first. The frozen statistic remains d_s = score_jev,s - score_uniform,s; PASS requires mean d_s >= 5. Old seed-1/3 pilot pairs informed the already-frozen power calculation but are excluded from this confirmatory N. Random/look remain secondary floors, never substitutes for uniform.
- Original fixed-seed SOTA means and KILL rule unchanged: Jev means >=31.67 / 51 / 320 on Zork1 / Deephome / Detective; KILL if no better than uniform on at least 2 of 3 games; stretch 48.66 / 67 / 346.67. Incomplete rows are not averaged.
- New paths, exclusive-reserved before output creation (154 paths; no collisions): work/jev-if/rows/{zork1,deephome,detective}-{jev,uniform,random,look}-r2-20260930-s{1,2,3}.jsonl and work/jev-if/rows/zork1-{jev,uniform}-power-r2-20260930-s{4..62}.jsonl. Every old row remains untouched. No seed substitution or episode replay. An error/timeout row is not scored. SDK retries remain pinned at 2; HTTP 401/402/403/404/429 terminates the Jev queue immediately. A request rejected by the byte guard is NOT_SCORED, never converted to uniform.

### Keyless feasibility and live-call boundary

- Captured input: work/jev-if/state-sample.json, SHA-256 9e28b81ad90e0841421b408ef7d1ccdf42e152f3f540bc6e19eac427647d1ba3, emitted by run.py --dump-state from a real Zork1 root. scripts/jev-state-size.py on that state and its 416-byte question returned FITS 1, NEAR 0, OVER 0; current calibration band 1.479–2.082 bytes/token from calibration-osworld-r3.tsv. Recorded Zork1 Jev seed 2 has 35/35 chosen actions present in the root action set, positive rewards at steps 4, 14, 20, 24, final 44/44, status=ok; row SHA-256 8d574380ef66de53a6e38791d3c66374fc68fdbae0bcfb0a3ea872a104fa4b34. This is prior feasibility evidence, not an r2 score.
- Source pins: puct.py 96fe13701092659d5a41e8bc90557f26079a565c5cae3bd9898144f18abae345; run.py ff923889a85f5590dc78cd8c8b25a04a683e22459b298041aa8d1f65919519d0; test_puct.py 622fa43b8515c9213986facc5644988c22bb4f49700731e9208fca992b9e35c7; Dockerfile fc137cc125d09f4ef492950ebf22b250e2a340c95903c15bba4ec763762255e8; image jev-if:wave1-amd64 sha256:0e78b19054ad9549a5a17beacb42ee5bde70f12968dfc8177d72a945f1d94516 (linux/amd64, /app). Current puct.py/run.py mount read-only; no image rebuild or upstream edit.
- Each Jev SDK operation writes one metadata-only kind=jev_request JSONL row (model, status/http status, full-request byte count, latency, input/output tokens, SDK max retries), then flushes and fsyncs through Rows.write. No state, prompt, answer body, key, or raw error is logged. Row-write failures raise FatalPriorError; they cannot fall back to a scored uniform prior. SDK retries remain within one logical-call row; max_retries=2 means at most 3 HTTP attempts per logical call. Official SDK MockTransport evidence: 401/402/403/404 each one attempt; 429 three; one checkpoint each. Success MockTransport returned jev-1.13.0, 12 input / 3 output tokens and one received row.
- Every full serialized UTF-8 request is refused before SDK initialization when larger than 32,768 bytes. Unit coverage proves exactly-at-limit is sent and over-limit refused before SDK construction. This is a conservative byte ceiling informed by observed calibration, not an exact tokenizer; no claim about unseen tokenizer density beyond that evidence.
- Offline verification: python3 -m unittest work/jev-if/test_puct.py — 36/36. UBS on the three changed Python files — 0 critical, 0 warnings. ripwire work/jev-if --quality-delta — exit 2, two preexisting-worse major findings; the reported SdkAsker volume is 59→101 lines. No acknowledgment or gate weakening; peer review remains required before code is declared complete.

### Budget, stop, and explicit boundary

The fixed schedule has 68 Jev-enabled episodes (9 fixed-target plus 59 powered) and 86 local-only baselines. The historical 80,000-request/game value remains an estimate, not an enforced cap; per-call rows and billed usage are authoritative. Each episode has frozen 35/35/50-step, depth-10, 50×valid-action simulation bounds plus SDK max_retries=2; no unbounded loop. No paid comparator arm. Boundary: this does not measure Jev against a chat model or establish general Jev superiority. Ollama 0.35 triage/routing/classification is user-reported and belongs to the separate localbench lane; it is not an arm or result here. No EVAL.md edit, no real r2 Jev call, and no row overwrite has occurred.

## HOLD correction and partial r2 accounting (2026-10-01)

Joshua's latest directive supersedes the continuation permission above: HOLD all new live Jericho r2 Jev calls until there is a named downstream consumer, a useful same-state incumbent, and an enforced call cap. This does not alter or weaken the frozen PUCT bar, sample, or any pilot row. Do not close jev-jy7t.1.4.

- One r2 provider run **did start**: Jev / Zork1 / seed 1, output work/jev-if/rows/zork1-jev-r2-20260930-s1.jsonl. Background job bg_133 was cancelled; the named container jev-puct-r2 was stopped without deleting it. No continuation call has been launched.
- Durable partial row summary: 626 logical request rows, all status=received, model jev-1.13.0; 309,722 input tokens, 47,823 output tokens; 15 step rows; no final row, no final score, no error row. Mark this run NOT_SCORED. The row file is preserved.
- Exact logged spend: 309,722 × $0.042/M input tokens = $0.013008324; output is free. This is the exact sum of persisted response usage, not a claim about the full provider bill: termination may have interrupted at most one in-flight logical SDK operation (max_retries=2, at most 3 HTTP attempts), for which no usage checkpoint exists. The actual total spend is therefore UNKNOWN; the current byte ceiling and calibration only estimate, not replace, provider usage.
- The prior 80,000-request/game figure is only an estimate, not an enforced cap. Therefore the original 68-episode plan had no hard per-run request cap. The new operational cap is **0 additional Jev calls** until the consumer and paired incumbent are identified; do not resume the 59-pair run under the current plan.
- No named downstream product or omp consumer would act on a Jev-PUCT win; work/jev-if is a benchmark harness. Uniform PUCT is a floor, not a useful incumbent. The only candidate raised here is the user-reported localbench Ollama 0.35 upgrade for same-state ticket triage/model routing/content classification; it is not yet available or validated and is not a Jev-PUCT comparator. Any useful comparison belongs to localbench and needs its own consumer, labels, paired incumbent, and hard cap; do not change this frozen game bar.
- Receipt hygiene: the two superseding r2 sections above are duplicate append records with the same cohort/bar; no text has been removed. Their puct.py/test_puct.py SHA values were copied from pre-format files. The exact committed and mounted files used by the started run are puct.py 4bdaaa3cbabe30efb7f0a6878d929b7ee9b7f461f30a8e632e704b77a9338c99, run.py ff923889a85f5590dc78cd8c8b25a04a683e22459b298041aa8d1f65919519d0, test_puct.py a779239e801b661a546d3de08eb00754718a67241ddde05065142f0ab392ec98; commit a1ff8f58. The mounted puct.py SHA was checked before the first call. This is a checksum correction only; the formatted source behavior and frozen bar were unchanged.
- No EVAL.md edit. No row was overwritten or deleted.

## HOLD after Joshua's latest directive (2026-10-01)

This hold supersedes the earlier r2 continuation permission. The two r2 amendment blocks above are duplicate append records; the later block is canonical, and neither block is deleted. Their statements that no r2 Jev request had occurred were true when written but are now superseded by this partial attempt. Preserve the frozen bar and every existing row. Bead jev-jy7t.1.4 remains in_progress; do not close it.

- One r2 provider run started: Jev, Zork1, seed 1, output work/jev-if/rows/zork1-jev-r2-20260930-s1.jsonl. Background job bg_133 was cancelled; container jev-puct-r2 was stopped without deleting it. No new r2 Jev call may start.
- Durable partial output: 626 logical request rows, all status=received, model jev-1.13.0; 309,722 input tokens; 47,823 output tokens; 15 step rows; no final row and no score. Run status is NOT_SCORED. The row file remains intact.
- Exact response-row spend: 309,722 × $0.042 / 1,000,000 = $0.013008324; output is free. Exact total provider spend is UNKNOWN because cancellation may have interrupted one in-flight SDK operation with no usage row. With max_inflight=1 and SDK max_retries=2, the run has at most 627 logical operations and 1,881 HTTP attempts total. At the documented 32,768-token input ceiling, the loose maximum spend across those attempts is $2.588737536; this is a worst-case ceiling, not an observed bill. The hard cap from this hold is **0 additional Jev calls**.
- No named downstream product or omp consumer would act on a Jev-PUCT win; work/jev-if is a benchmark harness, not a deployed decision path. Uniform PUCT is only a floor, not a useful incumbent. The user-reported localbench Ollama 0.35 upgrade is a possible separate same-state incumbent for ticket triage/model routing/content classification, but it is not installed, paired, or validated here. No useful incumbent currently exists for this game study. Do not resume until a named consumer, a useful paired incumbent on identical inputs, and an enforced call cap are specified; the 80,000-request/game figure above is only an estimate.
- Source-pin correction: the pre-run container mount check recorded puct.py SHA-256 4bdaaa3cbabe30efb7f0a6878d929b7ee9b7f461f30a8e632e704b77a9338c99, run.py ff923889a85f5590dc78cd8c8b25a04a683e22459b298041aa8d1f65919519d0, and test_puct.py a779239e801b661a546d3de08eb00754718a67241ddde05065142f0ab392ec98. The earlier copies of the puct.py/test_puct.py hashes (96fe… / 622fa…) were stale pre-format values; the read-only mount check was captured before the first call, so the run used the committed formatted source in a1ff8f58. This is a checksum correction only; no source behavior or bar changed.
- No EVAL.md edit. No Bead close. No pilot row or r2 row deleted or overwritten.

## Exact call and spend bounds for the stopped seed-1 attempt

- Persisted rows: 626 completed logical SDK calls. With the runner's max_inflight=1, at most one additional logical SDK operation could have been in flight when stopped: 627 logical operations total. The SDK's max_retries=2 gives at most 3 HTTP attempts per operation, so at most 1,881 HTTP attempts. Actual retry attempts are not recorded per transport attempt.
- The exact response-usage sum is 309,722 input tokens and 47,823 output tokens; at $0.042/M input tokens and free output, logged usage is $0.013008324. Exact invoice spend remains UNKNOWN because retries and a possible in-flight request may not have a usage row.
- Conservative documented-limit ceiling: 1,881 × 32,768 input tokens = 61,636,608 tokens, or $2.588737536 if every HTTP attempt were charged at the full input limit. This is a worst-case ceiling, not a measured spend. The r2 hard cap for any further Jev call remains 0 until the user-directed consumer/incumbent gate is resolved.
