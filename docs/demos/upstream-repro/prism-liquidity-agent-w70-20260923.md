# prism-liquidity-agent W7.0 receipt — 2026-09-23 (worker W70Prism)

Class: seat. Live unit after the keyless start. Bar read before any call:
`docs/demos/upstream-repro/w70-new10-t4-bar-20260923.md` (commit `1e59489`).
Model pin `jev-1.13.0`. No wallet, no order path. `EVAL.md` not edited.
Clone not edited.

| id | result | evidence |
|---|---|---|
| T1 | PASS | Pin, license, clean status, runtimes, and the bun deviation are below. |
| T2 | FAIL (environment) | `bun --bun vitest run` exit 1: 2 failed / 2183 passed / 17 skipped. Plant NOT-APPLICABLE. |
| T3 | PASS | Six claims, each with the file:line that decides it. |
| T4 | PASS (smoke) | One committed pool, N=1. Prevalence REFUSED (exit 2). No accuracy claim. |
| T5 | NOT-APPLICABLE | No labelled rows. Scored floor not computable. |
| T6 | PARTIAL | Same state through the adapter. Accuracy and McNemar not computable. |
| T7 | PASS (negative) | Calibration not observable at N=1. One bin count stated. |
| T8 | PASS (counts) | Choice repeat flips 0; framing flip 0/1. Not a stability claim beyond this row. |
| T9 | PASS | Injected `fetchImpl` refuses timeout, 429, 500, malformed, missing key. Host survived. |
| T10 | withheld | Not SELF, not FLOOR, not INCUMBENT. NO-CLAIM below. |

## T1 pin and environment

- Clone: `/Users/josh/Developer/jev/prism-liquidity-agent` @ `f503db10451fc2c6f1c614996b197442c064ba64` (2026-09-23 09:23:28 +0700, `test(native): flat-drift zero-fee vector completes the fee/IL ternary`).
- License: MIT, `LICENSE:1-3`, Copyright (c) 2026 irfndi. `package.json:17` agrees.
- `git status --porcelain` empty before the suite and after the last live call. HEAD unchanged. Adapter tree `upstream/typesafe-ai/system-one-adapter-python` also empty.
- Host: `Joshs-Mac-Studio.local`, Darwin 25.5.0 arm64. No omp command was run, so `OMP_PROFILE=grok`, `PI_PROFILE=grok`, and `PI_CODING_AGENT_DIR=/Users/josh/.omp/profiles/grok/agent` were recorded and not unset.
- Runtimes: node v22.22.0, bun 1.4.0. Deviation: the only lockfile is `bun.lock` (`packageManager` `bun@1.4.2` at `package.json:79`; CI `BUN_VERSION: 1.4.2` at `.github/workflows/ci.yml:22`). AGENTS.md says npm for JS. The lockfile wins. Local bun is 1.4.0, not 1.4.2.
- Install: `bun install --frozen-lockfile --ignore-scripts` (postinstall would write `.env` and ping `prism-api.irfndi.workers.dev`). Then `bun run scripts/generate-vec-embed.ts darwin arm64`, which writes gitignored `engine/sqlite-vec-embedded.ts`. Neither is a tracked edit.
- Key presence, value never printed: `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- sh -c '…'` reported `TYPESAFE_API_KEY=set len=107`, `ANTHROPIC_API_KEY=set len=108`. Infisical 0.43.84 from `~/.local/bin`. Upgrade nag declined.

## T2 own suite

Command, from the clone root, matching `package.json:34` (`"test": "bun --bun vitest run"`). The ledger's two-file command is a lead: line 34 names no files. `vitest.config.ts:13` includes `bench/**/*.test.ts`. `vitest.config.ts:6-7` refuses Node.

```
CI=true NODE_ENV=test LOG_LEVEL=error HELIUS_API_KEY=test-helius-key \
  SOLANA_RPC_URL=https://example.com WALLET_PRIVATE_KEY=test-private-key \
  env -u TYPESAFE_API_KEY -u TYPESAFEAI_API bun --bun vitest run
```

`WALLET_PRIVATE_KEY=test-private-key` is the CI dummy (`ci.yml:33`), not a wallet this run used.

Verbatim summary (2026-09-23T05:44:10Z, duration 57.91s):

```
Test Files  1 failed | 152 passed | 1 skipped (154)
     Tests  2 failed | 2183 passed | 17 skipped (2202)
error: "vitest" exited with code 1
```

Failed tests, verbatim:

```
FAIL  bench/http-status-server.test.ts > HttpStatusServer > serves status endpoint
Error: Failed to start server. Is port 18799 in use?
 ❯ engine/http-status-server.ts:593:25

FAIL  bench/http-status-server.test.ts > HttpStatusServer > rejects /approve batches that exceed the configured limit
Error: Failed to start server. Is port 18789 in use?
 ❯ engine/http-status-server.ts:593:25
```

Cause: ports are hardcoded at `bench/http-status-server.test.ts:213` (`18_799`) and `:988` (`18_789`). `lsof` showed node PID 705, parent 1, elapsed 2-09:14:36, command `openclaw/dist/index.js gateway --port 18789`, also listening on 18799. That is the user's gateway. It was not killed.

Skips, all 17, one reason: `bend` is not on PATH (`command -v bend` empty). `bench/bend-parity.test.ts:25-26` sets `describe.skip`. A focused rerun listed the same 17 names and `Tests  17 skipped (17)`.

Plant arm: NOT-APPLICABLE. The unmodified suite exited non-zero. A `/tmp` plant is not owed until a clean run exits 0 (`docs/PLAN-DEEP-KIT-20260922.md:429`).

Two routes for the red suite:

1. The full command above. Exit 1, the two port lines.
2. Identify the listener, then look for an override. No env var changes those literals. Freeing the ports means killing PID 705. That was not done. Editing the test is forbidden.

## T3 claims

1. Shadow only, never drives ENTER/EXIT (`engine/jev-service.ts:2-6`). **Partial.** `program.ts:505-513` halves a paper ENTER's size when `paperTrading`, `halveEnabled`, and stress `>= threshold`. It does not choose ENTER or EXIT. The header overclaims "NEVER drives".
2. One batched call: Choice `deposit_pick` plus three Nouls (`engine/jev-service.ts:182-207`). **Demonstrated.** `bench/jev-service.test.ts:99-119` expects one fetch and four fields. The live body sent those four ids in one POST.
3. Default model `jev-latest`, timeout 10s (`engine/jev-service.ts:25-26`). **Demonstrated** as the unset default. This run overrode the model to `jev-1.13.0`. The default itself is not disproven.
4. Fail-open, never throws (`engine/jev-service.ts:259-264`, `:292-294`). **Demonstrated** on the injected path (T9). The comment's "429/529" is **partial**: `failureForStatus` (`:246-249`) names only 429. Any other non-OK, including 500, is `failure: "error"`.
5. Paper-only stress halve at `>= 0.35`, never a veto (`engine/program.ts:477-485`, `:505-509`; tests `bench/jev-service.test.ts:137-150`). **Demonstrated** for the predicate. The number "kept PF 3.53 vs 1.74" (`.env.example:303`) is **stale**. Nothing committed reproduces it. `bench/jev-backtest.ts:4` reads `/tmp/jev_cohort_<name>.tsv`, and that file is absent.
6. Rust host consults Jev. **Aspirational.** `native/rust/src/main.rs:2697-2700` is `StubJev`; `jev_soft_gate(..., Err("jev client not wired"))`. The comment at `:2683-2684` says a real HTTP transport comes later.

The vendored skill (`skills-lock.json:4-8`) is not the call path. The engine posts by hand (`engine/jev-service.ts:211-226`).

## Prevalence, before the live call

```
node work/jev-prevalence-first/prevalence-check.mjs /tmp/prism-w70-rows.jsonl --truth label
set: /tmp/prism-w70-rows.jsonl rows=1 labelled=0
near-threshold: n/a (no labels)
own-constant: NOT COMPUTABLE — 0 of 1 rows carry 'label'
verdict: REFUSED — label a sample of this set before any Jev question is judged on it
EXIT:2
```

The row is the committed `native/rust/src/datapi_zec_sol.json` pool `8eybKAvjKJryVweQLg8SRgwUfdP7wHYJ5yyqgfE82DQA` (ZEC/SOL). It has tvl, volume, fees, and `pool_config.bin_step`. It has no label, no active bin, no fee/IL, no volatility. Missing numbers were sent as `null` with `*Known: false`. They were not filled in. Exit 2 means the calls below are a smoke (`w70-new10-t4-bar-20260923.md:5`). N=1 is under 20, so no accuracy claim (`:5`).

## T4 smoke

Four POSTs to `/v1/systemone`, each with `model: "jev-1.13.0"` on the wire. A wrapper refused to forward any other model. `fetchImpl` bypasses `jevFetch` (`engine/jev-service.ts:278-280`); the pace was a 2.1s sleep, the interval named in `bench/jev-backtest.ts:190`. No wallet function was called.

| tag | status | ms | in/out tokens | deposit | toxic | recovery | stress |
|---|---|---|---|---|---|---|---|
| repeat-1 | 200 | 228 | 707/97 | spot 0.95 | 0.46 | 0.39 | 0.27 |
| repeat-2 | 200 | 190 | 707/97 | spot 0.95 | 0.47 | 0.38 | 0.30 |
| repeat-3 | 200 | 229 | 707/97 | spot 0.95 | 0.46 | 0.39 | 0.29 |
| reword | 200 | 172 | 697/97 | spot 0.94 | 0.45 | 0.34 | 0.28 |

Parsed by `consultJevJudgments` for the three repeats (`ok: true`, `failure: null`). Reword was a direct POST of the captured body with instructions changed and `state` unchanged. Jev token totals: 2818 in, 388 out, 4 calls. Dollar cost is not in the response and is not invented. p50/p95 are not observable at N=1.

## T5 floor

NOT-APPLICABLE. A scored floor needs labels on the same rows. Committed data has none (`jev-backtest.ts:4`; prevalence exit 2). The no-history branch of `recommendStrategy` returns `curve` (`engine/strategy-service.ts:480-491`). That was not scored against Jev, because the fixture does not contain the volatility and drift that function requires, and inventing them would be authoring a set.

Four fields, in case a reader treats this as unrun: command not issued as a scorer; verbatim output is the prevalence block above; cause `bench/jev-backtest.ts:4` plus the absent `/tmp/jev_cohort_*.tsv`; routes (1) committed tree has one unlabelled pool snapshot and two blacklists, (2) the backtest's own `/tmp` path is empty.

## T6 incumbent

Same captured `state` and the same four question texts, through `upstream/typesafe-ai/system-one-adapter-python` 0.2.0:

```
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  uv run --directory upstream/typesafe-ai/system-one-adapter-python \
  --extra anthropic --no-sync python /tmp/prism-w70-t6.py
```

`claude-haiku-4-5`, HTTP success, wall 2627 ms, adapter latency 2.203 s, 1149 in / 56 out, `n_retries` 0. Choice `curve` at confidence 0.01 (probabilities spot 0.33 / curve 0.34 / bidask 0.33). Nouls 0.50 / 0.50 / 0.50. Jev on the same state said `spot` at 0.95. Accuracy and McNemar are not computable: one unlabelled row. Dollar cost not invented. Adapter git status stayed empty (`--no-sync`).

## T7 calibration

Not observable at N=1. The only deposit confidence is 0.95, so the bin `[0.95, 1.01]` has count 1 and the other bins have count 0. That is a count, not a reliability curve.

## T8 stability

Same state, three times: deposit choice identical (`spot`), so repeat flips 0. Reworded instructions, same state: still `spot`, framing flip 0/1. Noul values moved (toxic 0.46/0.47/0.46/0.45, stress 0.27/0.30/0.29/0.28). None crossed the clone's paper-halve threshold 0.35 (`program.ts:485`). This is one row. It is not a stability rate for the seat.

## T9 faults

Mock path: `consultJevJudgments(..., { fetchImpl })` (`engine/jev-service.ts:268-280`). Probe `/tmp/prism-w70-t9.mjs`, no network, no key spent. Host survived, exit 0.

```
missing-key {"ok":false,"failure":"disabled","depositPick":null}
unset-key {"ok":false,"failure":"disabled","depositPick":null}
429 {"ok":false,"failure":"rate_limited","depositPick":null}
500 {"ok":false,"failure":"error","depositPick":null}
malformed-200 {"ok":false,"failure":"error","depositPick":null}
malformed-object {"ok":false,"failure":"invalid","depositPick":null}
timeout {"ok":false,"failure":"timeout","depositPick":null}
transport-throw-escaped {"threw":false}
calls429=1 calls500=1
```

`unset-key` was probed with the ambient key unset, so it did not prove the Infisical path. Explicit `""` does not fetch. Non-JSON 200 is `error` (the `response.json()` throw), not `invalid`. A JSON body without `answers` is `invalid`.

## T10 verdict

Result class withheld. Not SELF: no labelled accuracy. Not FLOOR: no scored constant or lexical arm. Not INCUMBENT: Haiku ran, but N=1 and prevalence REFUSED, so the disagreement is not a paired result. Seat neither granted nor refused.

NO-CLAIM: nothing here says Jev prices DLMM deposits, beats a heuristic, or produced PF 3.53. The smoke says only that one committed pool snapshot, with missing signals left null, got `spot` at 0.95 from `jev-1.13.0`, and that the clone's own suite is red on two ports held by OpenClaw.

## Boundary

Measured: pin and clean tree; the bun suite as written; six claims; a keyless fault probe; one unlabelled smoke (4 Jev calls, 2818/388 tokens) and one Haiku call (1149/56) on that same state. Not measured: accuracy, a scored floor, McNemar, calibration, a stability rate, dollar cost, any wallet or order, the Rust HTTP client, the PF figure, and a green suite. Plants were not applied. The live driver was `/tmp/prism-w70-live.mjs` and is not part of the clone.

Re-run the suite, not the smoke:

```
cd /Users/josh/Developer/jev/prism-liquidity-agent && \
  CI=true NODE_ENV=test LOG_LEVEL=error HELIUS_API_KEY=test-helius-key \
  SOLANA_RPC_URL=https://example.com WALLET_PRIVATE_KEY=test-private-key \
  env -u TYPESAFE_API_KEY -u TYPESAFEAI_API bun --bun vitest run
```

Artifact note at commit time: `/tmp/prism-w70` was absent. The smoke was not re-run. Pin `f503db1` and `engine/jev-service.ts:25` (`jev-latest`) were re-checked. The live numbers above are the previous session's, not a second measurement.
