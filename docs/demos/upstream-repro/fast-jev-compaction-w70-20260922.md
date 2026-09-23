# fast-jev-compaction — W7.0 — 2026-09-23

Clone: `/Users/josh/Developer/jev/fast-jev-compaction`. Class: tool/integration. Tests run: T1 T2 T3 T4 T9 T10. T5–T8 are not in this class profile.

Pin: `6e1da50d064cc06aa08e720b534b4d873e2bb0b6` (`6e1da50d064c`). Commit date: 2026-09-17 22:00:10 +0000. Subject: Merge pull request #16 from tamaratran/devin/1789680966-chunk-decision-log. License: MIT (`LICENSE:1`, `package.json:6`). Host: `Joshs-Mac-Studio.local` (Darwin arm64). Not an RCH worker. Suite node: v22.22.0 (`vitest/2.1.9 darwin-arm64 node-v22.22.0`). npm: 10.9.4. The tsx process under Infisical printed `Node.js v22.23.1` on the failed transform that preceded the live call. `OMP_PROFILE`, `PI_PROFILE`, and `PI_CODING_AGENT_DIR` were unset before every command. Infisical: `~/.local/bin/infisical` 0.43.84. Key presence check: `len=107`. The value was not printed.

T4 bar, already committed, not retuned: `docs/demos/upstream-repro/w70-t4-bar-20260922.md` at `da2a785db92e15f314aa47829015d84f0a038d97` (2026-09-22 21:14:20 -0600). The live call was 2026-09-22 21:22:11 -0600. Prior receipts, including `EVAL.md:11-22` and `docs/demos/upstream-repro/fast-jev-compaction-20260918.json`, were not used as passes.

Re-run (keyless, from the clone, no `/tmp` script):

```sh
unset OMP_PROFILE PI_PROFILE PI_CODING_AGENT_DIR
cd /Users/josh/Developer/jev/fast-jev-compaction && npm test
```

## Results

| id | status | evidence |
|---|---|---|
| T1 | PASS | Full SHA, date, license, host, and runtimes above. Dirty status recorded verbatim, same before the suite and after the live call. Not reverted. |
| T2 | PASS | `npm test` → vitest 2.1.9, exit 0, `Test Files  2 passed (2)` / `Tests  29 passed (29)`, 0 skipped, 3.14s, started 21:18:14 local. Planted defect in `/tmp/fjc-w70-plant` only: `src/compact.ts:108` `>=` inverted to `<`. Suite went RED, exit 1, 8 failed / 21 passed, 0 skipped. Clone porcelain stayed ` M package-lock.json`. |
| T3 | PASS | Five clone claims below, each with the line that decides it. |
| T4 | PASS | Smoke, not a certification. One live call on `examples/demo.ts`, request model `jev-1.13.0`, HTTP 200, schema-valid nouls, process exit 0. N=14 questions. No accuracy claim. |
| T5 | NOT-APPLICABLE | Floor arms are seat/benchmark only (`docs/PLAN-DEEP-KIT-20260922.md:417`, class profile `:426`). |
| T6 | NOT-APPLICABLE | Incumbent arm is seat/benchmark only (`:418`, `:426`). |
| T7 | NOT-APPLICABLE | Calibration bins are seat/benchmark only (`:419`, `:426`). |
| T8 | NOT-APPLICABLE | Stability flips are seat/benchmark only (`:420`, `:426`). |
| T9 | FAIL | Missing key, 429, 500, and malformed bodies throw and do not keep-or-drop. A hung fetch is not refused: no client deadline. |
| T10 | PASS | Verdict below. Result class SELF. NO-CLAIM stated. Nothing required was left NOT-RUN. |

### T1 dirty status, verbatim

`git status` before the suite, and the same porcelain after the live call:

```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   package-lock.json

no changes added to commit (use "git add" and/or "git commit -a")
```

Porcelain: ` M package-lock.json`. Diff is two lines: lockfile `version` `0.1.0` → `0.2.0` at the root and under `packages[""]`. `package.json:3` is already `0.2.0` at HEAD. This run did not edit the clone.

### T2 plant

Untouched suite: `npm test` in the clone, exit 0, 29 passed, 0 failed, 0 skipped.

`/tmp` copy only. One-line plant at the copy of `src/compact.ts:108`:

```
-  if (answer.keepResult >= options.keepThreshold) {
+  if (answer.keepResult < options.keepThreshold) {
```

`npm test` in `/tmp/fjc-w70-plant`, `PLANT_EXIT=1`. First failure, verbatim:

```
FAIL  tests/fast-jev-compaction.test.ts > decisions > keeps, drops the result, or drops the call based on the keep probabilities
AssertionError: expected 'drop_result' to be 'keep' // Object.is equality
 ❯ tests/fast-jev-compaction.test.ts:263:86
```

Eight failures: five in `tests/fast-jev-compaction.test.ts`, three in `tests/hook.test.ts`. The suite can go RED. It is not unable to fail.

### T3 claims

| # | claim | status | line that decides it | tier |
|---|---|---|---|---|
| 1 | "This library never rewrites anything. It only deletes tool calls and tool results." User and assistant text "stays verbatim and in order." (`README.md:9-12`) | partial | Untouched messages are returned as the same object (`src/compact.ts:166-168`). Rebuilt messages copy `text: message.text` (`src/compact.ts:220`). Dropped results are rewritten by `truncatedResultText` (`src/compact.ts:135-140`). The README itself qualifies this at `README.md:46-47`. | [Verified, High] for the text copy; the absolute "never rewrites" sentence is too strong |
| 2 | "Jev failures, malformed answers, a missing key, or a history that cannot be fitted throw" (`README.md:53-54`) | demonstrated | Missing key: `src/client.ts:30`. Non-OK HTTP: `src/request.ts:44-45`. Malformed JSON: `src/request.ts:51`. Missing `answers`: `src/request.ts:60`. Non-finite noul: `src/request.ts:77`. Unfittable history: `src/state.ts:301`. Green suite covers the unfit and keyless cases (`tests/fast-jev-compaction.test.ts:223`, `:427-431`). T9 re-ran the key and body cases. | [Verified, High] |
| 3 | Default model is `jev-latest` (`README.md:101`) | demonstrated | `src/request.ts:4` and `src/request.ts:31`. Green test expects `model: 'jev-latest'` when the caller omits it (`tests/fast-jev-compaction.test.ts:400`). The unmodified example would send that default (`examples/demo.ts:51`). | [Verified, High] |
| 4 | No runtime dependencies (ledger lead; the clone's own `package.json` is the claim surface) | demonstrated | `package.json` has no `dependencies` key. `devDependencies` only, `package.json:29-34`. `node -e` printed `dependencies null`. | [Verified, High] |
| 5 | The estimator "lands 2–18% above" the counts Jev reports (`README.md:33-35`, `src/state.ts:24-25`) | aspirational | `estimateTokens` is a character heuristic (`src/state.ts:28-37`). This run's `stateTokens` was 1139 and the response `input_tokens` was 1908, but that input count includes questions, so it does not test the band. No calibration artifact is in the clone. | [Maintainer claim, Low] |

### T4 live call

Bar applied as committed. No new threshold.

State: `examples/demo.ts` lines 1–49, the clone's own `messages` array. A `/tmp` copy deleted only the call at `examples/demo.ts:51` and exported `messages`. Diff against the clone is that deletion plus `export { messages }`. Options matched the example (`preserveRecentMessages: 2`) plus `model: 'jev-1.13.0'`.

Command:

```sh
unset OMP_PROFILE PI_PROFILE PI_CODING_AGENT_DIR
export PATH="$HOME/.local/bin:$PATH"
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  /Users/josh/Developer/jev/fast-jev-compaction/node_modules/.bin/tsx /tmp/fjc-w70-live/run.mts
```

`T4_EXIT=0`. One HTTP call. The first attempt exited 1 before any request: tsx refused top-level await in a `.ts` file (`Transform failed ... "cjs" output format`). That attempt sent nothing. The `.mts` re-run is the data.

| field | value |
|---|---|
| request model | `jev-1.13.0` |
| HTTP | 200 |
| latency | 832 ms (fetch); `stats.ms` 835 |
| N | 14 noul questions, 7 tool calls, 1 HTTP call |
| question type | `noul` on every question |
| answers | 14 keys, 0 missing |
| schema | client did not throw; every required noul was a finite number |
| tokens | `input_tokens` 1908, `output_tokens` 256 (both finite, copied) |
| cost | not in `usage` (keys were only those two). Not invented |
| p50 / p95 | not observable (1 timed call; bar requires N ≥ 5) |
| positive-class prevalence | not observable (the example has no labels) |
| process | alive, exit 0, pid 96297 |

Decisions the client applied at `keepThreshold` 0.5. These are observations, not a correctness score:

| id | tool | action | keepCall | keepResult |
|---|---|---|---|---|
| t1 | Glob | drop_call | 0.13 | 0.07 |
| t2 | Read | drop_call | 0.15 | 0.06 |
| t3 | Read | drop_call | 0.24 | 0.13 |
| t4 | Bash | drop_call | 0.20 | 0.12 |
| t5 | Edit | drop_call | 0.38 | 0.16 |
| t6 | Bash | drop_call | 0.21 | 0.09 |
| t7 | Bash | drop_call | 0.22 | 0.10 |

`stats`: messages 21 → 7, chars 4475 → 577, calls 7, kept 0, resultsDropped 0, callsDropped 7, pinned 0, stateTokens 1139, stateStage `full`, requests 1.

N is under 20. This is a smoke. It is not a certification and makes no accuracy claim.

### T9 faults

Probe: `/tmp/fjc-w70-t9.mts` against the untouched clone, `TYPESAFE_API_KEY` deleted, `T9_EXIT=0` (the probe caught every throw; the host printed the report and exited 0).

| case | result |
|---|---|
| `JevClient` with `apiKey: ''` | threw `TYPESAFE_API_KEY is not configured`; fetch calls 0; no decision returned |
| `compactMessages` with `apiKey: ''` and env unset | same throw; fetch calls 0; no `CompactResult` |
| HTTP 500 | threw `Jev request failed (500): boom`; no decision |
| HTTP 429 | threw `Jev request failed (429): slow down`; no decision |
| body `not json` | threw `Jev returned malformed JSON` |
| body `{}` | threw `Jev response is missing answers` |
| noul as the string `"0.99"` | threw `Invalid Jev answer for call_t1`; not coerced to a keep |
| `call_t1` present, `result_t1` absent | threw `Invalid Jev answer for result_t1`; did not fall through to the keep default |
| transport `TimeoutError` rejection | threw `The operation was aborted due to timeout`; no decision |
| fetch that never resolves | `STILL_PENDING` at 200 ms; `settled: false`; fetch was called once |
| `compactSession` with no key | threw `TYPESAFE_API_KEY is not configured`; fetch not called |
| `register` `session.compact` with no key | `delegated: true`, `hookFetches: 0`, `inventedDecisions: false`, returned keys `delegated`, `count` |

Missing key does not keep-or-drop. `src/compact.ts:282` defaults a missing answer map entry to `{ keepCall: 1, keepResult: 1 }`, but the missing-key path throws at `src/client.ts:30` before `fetch` and before `decideCall`. A missing noul throws at `src/request.ts:77` inside `askBatch`, so that default is not a substitute for a live answer either.

The hook's `register` catches and calls `next(event)` (`hooks/fast-jev.ts:283-288`). That is the documented fallback to built-in summary (`README.md:53-54`), not a synthetic keep/drop. `compactSession` still throws (`hooks/fast-jev.ts:170`).

Timeout clause, two routes, both fail closed as a refusal:

1. Empirical: hung `fetch`, `Promise.race` 200 ms, result `STILL_PENDING`.
2. Source: `src/client.ts:36-40` passes only `method`, `headers`, and `body`. No `signal`, no deadline. `hooks/fast-jev.ts:95-99` is the same shape.

A caller-aborted fetch is propagated. A fetch that never settles is not refused. That is the T9 fail. The host of the probe survived because the probe did not await the hang; `compactMessages` itself would block.

## T10 verdict

Result class: **SELF**. The mechanism was measured on its own suite, its own fault paths, and one live call on its own example. Floor and incumbent arms are outside this class profile, so they are not claimed and not scored.

RULEBOOK tier per claim: table in T3. Claims 2–4 are [Verified, High]. Claim 1 is verified as a text copy and partial as an absolute. Claim 5 is a maintainer comment, not a measurement.

NO-CLAIM:

- No accuracy, no precision, no "drops were correct." N=14 questions on an unlabelled example. Smoke only.
- No positive-class prevalence. The example has no labels.
- No cost. The response `usage` object had `input_tokens` and `output_tokens` only.
- No p50 or p95. One timed call.
- No confirmation of the 2–18% estimator band (`src/state.ts:24-25`).
- No grade of the omp port in `compaction/` or `.omp/lib/jev-compact`. This receipt does not run the L0–L4 ladder. The assigned tests were T1–T4, T9, and T10 on the clone.
- Prior receipts are leads. They are not this pass.

Nothing in T1–T4 or T9 was left NOT-RUN. T5–T8 are NOT-APPLICABLE by class, not unrun.

## Boundary

This receipt covers `fast-jev-compaction` at `6e1da50d064cc06aa08e720b534b4d873e2bb0b6` on host `Joshs-Mac-Studio.local`, run 2026-09-23T03:15:53Z through 2026-09-23T03:22:49Z. Inside: the dirty lockfile version bump, the 29-test suite, one planted inversion, five claims, one pinned live call (14 questions, 832 ms, 1908/256 tokens), and the fault probe. Outside: accuracy, cost, latency percentiles, the estimator's calibration band, a client-side deadline, and any omp port of this library.
