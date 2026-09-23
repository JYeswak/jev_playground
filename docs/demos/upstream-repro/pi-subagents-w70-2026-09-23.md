# pi-subagents W7.0 — 2026-09-23

Clone: `pi-subagents` @ `f4918e80b531f1bf9f1d9e847b8f86c9016108f1` (2026-09-18 08:59:47 -0700, `chore(release): v0.69.0`). Class: tool/integration. Profile: T1–T4+T9+T10 (no omp ladder; not ported). Worker: W70PiSub. Host: `Joshs-Mac-Studio.local` (darwin 25.5.0, arm64). Node `v22.22.0`, npm `10.9.4`. License: MIT (`LICENSE:1`, `package.json:6`). Pin clock: 2026-09-23T03:40:56Z. Clone never edited (read + run only). Prior lead `docs/demos/upstream-repro/pi-subagents-w70-20260922.md` is not evidence. Live model `jev-1.13.0`: zero live calls made (N=0, cost $0, no latency). Spend: $0.

Env note: the login shell carries `OMP_PROFILE=muse`, `PI_PROFILE=muse`, `PI_CODING_AGENT_DIR=/Users/josh/.omp/profiles/muse/agent`. Every test and `classify` command below ran with all three unset via `env -u OMP_PROFILE -u PI_PROFILE -u PI_CODING_AGENT_DIR`.

| id | status | result |
|---|---|---|
| T1 | FAIL | Pin recorded. Cleanliness fails: `M package-lock.json` only (2 deletions, both a `"peer": true` line under dev packages; no source change; pre-existing, not added and not reverted by this run). SHA, date, license, host, worker, Node/npm, and the unset-profile discipline are recorded above. |
| T2 | PASS | Own suite ran fresh and a planted defect turned a `/tmp` copy RED. The suite itself is red (pre-existing failures, not triaged as a defect report). See counts and plant below. |
| T3 | PASS | Five claims, each with the line that decides it; four executed keylessly, one inspection-only (marked partial). |
| T4 | PROPOSED-NOT-RUN | This clone calls no Jev endpoint, so there is no live bar to apply. A committal bar is proposed verbatim below from the repo's own runnable surface (typed-gate swap); no live call was made under it. |
| T5 | NOT-APPLICABLE | Seat/benchmark floor arm. This clone asks no labelled question. |
| T6 | NOT-APPLICABLE | Seat/benchmark incumbent arm. No Jev call and no labelled rows. |
| T7 | NOT-APPLICABLE | Calibration needs a live choice distribution. None exists. |
| T8 | NOT-APPLICABLE | Stability needs repeated live asks. None performed per profile. |
| T9 | PASS (client-surface faults, keyless) | No Jev client exists to fault (see cause + routes below), so timeout/malformed/missing-key were exercised on the client surface the package actually ships: tool-timeout resolver, typed-gate stdout validation, `classify` exit paths, and the intent-arbiter missing-auth path. |
| T10 | PASS | Result class **SELF**. Keyless floor recorded on the repo's own decision surface (keyword `classify` over its documented fixtures). No accuracy, cost, or latency claim. |

## T1 — pin and environment

- Repo: `/Users/josh/Developer/jev/pi-subagents`, upstream `https://github.com/nicobailon/pi-subagents` (`package.json:29-31`).
- SHA: `f4918e80b531f1bf9f1d9e847b8f86c9016108f1`; `chore(release): v0.69.0`; author Nico Bailon `nico.bailon@gmail.com`; date 2026-09-18 08:59:47 -0700.
- License: MIT (`LICENSE:1-3`).
- `git status --short` before and after: `M package-lock.json` only. Diff: 2 deletions, both `"peer": true` lines (hunks at `package-lock.json:667-670` and `:1859-1862`). No source change.
- Runtime: Node v22.22.0, npm 10.9.4, Darwin 25.5.0 arm64, host `Joshs-Mac-Studio.local`.
- Deps (`package.json:96-102`): `acorn`, `jiti`, `typebox`, `undici`, `yaml` — no judgment SDK, no POST client, no key.

## T2 — own suite (fresh)

Command, from the clone, profiles unset (exactly `package.json:61`):

```
env -u OMP_PROFILE -u PI_PROFILE -u PI_CODING_AGENT_DIR npm --prefix pi-subagents run test:unit
```

which is `node --experimental-strip-types --import ./test/support/isolated-temp-root.mjs --test test/unit/*.test.ts`. Full log: `/tmp/pi-w70-unit-20260923.log`. Exit **1**. Lane: local suite on this host, not a live Jev call. Evidence: test, N=3321, 2026-09-23 UTC, no model.

| | |
|---|---|
| tests | 3321 |
| suites | 356 |
| pass | 3261 |
| fail | 25 |
| cancelled | 23 |
| skipped | 12 |
| todo | 0 |
| duration | 145088 ms |

Top-level failing suites (17 `^not ok` lines; remaining 8 of the 25 fail counter are nested subtests): `Herdr inspector`, `native supervisor channel`, `nested control routing`, the `orca-progress-tabs` cluster (13 lines: hung-terminal, malformed-metadata, disabled-tabs, creationSettled, worktree-sequence, split-sequence stripping, backpressure mirror, same-worktree waits, predecessor marker, queued-timeout, deferred cleanup, pretty-JSON manifest, byte-bound truncation), and `watchdog LSP diagnostics` (1 subtest failed). Not a triage: no failure is explained, filed, or attributed here; the red exit is the recorded fact. Cancelled 23 is a separate counter, not folded into the 25.

### Plant (RED proof, `/tmp` copy only)

Copy: `/tmp/pi-subagents-w70-plant-0923` (src, test, examples, package.json, tsconfig.json, index.ts; `node_modules` symlinked; no `.git`). Clone bytes unchanged — verified: `src/runs/shared/acceptance.ts:1308-1313` in the clone still fails invalid JSON (see T3 claim 2).

Control, same runner + same `--import isolated-temp-root.mjs` flag, unplanted copy, `test/unit/typed-gate-output.test.ts`: **9 pass, 0 fail, exit 0**. (Without the import flag the control fails environmentally — `git commit` in the temp repo is refused by a global `verification-level` hook — which is why the exact suite flag matters.)

Plant, only in the copy, in `applyTypedVerifyOutput` (`acceptance.ts:1311-1313` at the pin): the `catch` that used to fail invalid JSON now sets `run.structuredOutput = { coerced: true }` and returns. Re-run of that one file:

```
not ok 3 - fails the gate on invalid or empty stdout instead of dropping the verdict
  expected: 'rejected'
  actual: 'verified'
# tests 9
# pass 8
# fail 1
EXIT:1
```

The suite can fail, and the failure names the planted coercion (`typed-gate-output.test.ts:113`). This is not a certification of the 25 pre-existing failures. Evidence level: test, N=1 planted assertion, 2026-09-23 UTC, no model. Lane: `/tmp` copy only.

## T3 — claims (≥5, each with the line that decides it)

| # | claim | status | evidence | decides it |
|---|---|---|---|---|
| 1 | The typed-gate example is a keyword stand-in and runs with no API key (`examples/typed-gate/README.md:3-5`, `classify:1-5`). | demonstrated | executed keylessly, 2026-09-23 UTC, no model | `P0 blocker … secret token` piped to `classify --stdin` → `{"verdict":"blocked","risk":0.9,"notes":["blocker-level finding","security-sensitive"]}` exit 0. `LGTM no issues found` → `{"verdict":"ok","risk":0,"notes":["explicit clean verdict"]}` exit 0. Rules: `classify:31-34`. No key, no network, no env var read. |
| 2 | A typed gate's stdout must be one JSON document ≤12,000 chars; anything else fails the gate and the verdict is never silently dropped (`examples/typed-gate/README.md:38`, `docs/tool-reference.md:424-425`). | demonstrated | test, N=9 control file green + N=1 plant red, 2026-09-23 UTC, no model | `TYPED_VERIFY_OUTPUT_MAX_BYTES = 12_000` (`src/runs/shared/acceptance.ts:1290`); empty/truncated/non-JSON/schema-invalid paths (`acceptance.ts:1306-1317`); control `typed-gate-output.test.ts:113` passes unplanted and rejects the coercion when planted. Never memoized (`acceptance.ts:1341-1343`; test `:132-139` green in control). |
| 3 | `maxSubagentSpawnsPerRun` defaults to 64 (`README.md:101`). | demonstrated | inside the N=3321 suite + source read, 2026-09-23 UTC, no model | `DEFAULT_MAX_SUBAGENT_SPAWNS_PER_RUN = 64` (`src/shared/types.ts:2918`); resolver falls through to it (`types.ts:2926-2930`); suite asserts the doctor line `configured limit: 64 (default)` (`test/unit/doctor.test.ts:120`). |
| 4 | Command-runner / external-cli agents are async-only; a direct foreground call is refused (`docs/workflows.md:243`, `examples/typed-gate/README.md:41`). | partial | inspection, N=0 executions of that branch | Refusal is in source: an external (`external-cli`/`external-job`) agent with `!effectiveAsync` or `foregroundOnly` returns `Agent '…' uses runner.type='…', which currently supports async/background execution only` (`src/runs/foreground/subagent-executor.ts:6994-6997`; default-async promotion `:6990-6991`). This run sent no such call. |
| 5 | Swap the keyword `score` body for TypeSafe Jev and keep the JSON shape (`examples/typed-gate/classify:4-5`). | aspirational | inspection, N=0 Jev calls | Comment only. No `typesafe`/`jev` dependency (`package.json:96-102`); no POST, no model pin, no key read anywhere in the tree. The swap is an invitation, not a behaviour. |

## T4 — proposed bar (PROPOSED, NOT RUN — verbatim for committal)

No live call was made under this bar. It activates only if a human performs the `classify:4-5` swap. Text as committed:

```
T4 bar — pi-subagents typed-gate Jev swap (PROPOSED 2026-09-23, NOT RUN).
Activation: a human replaces the keyword `score` body in
examples/typed-gate/classify (lines 28-36) with a jev-1.13.0 call, keeping
the stdin/JSON contract: one JSON document on stdout, at most 12,000
characters, schema { verdict: enum("ok","blocked"), risk: number }
(docs/tool-reference.md:424-428; enforced by
src/runs/shared/acceptance.ts:1290-1317; gates never memoized,
acceptance.ts:1341-1343).
Fixture set (to be committed before any keyed run):
examples/typed-gate/fixtures/jev-swap-20.jsonl — N=20 report texts,
10 blocker-class (data-loss, auth-bypass, unreviewed migration) and
10 clean-class (typo, docs, LGTM with no finding), each with a human label.
Oracle: human label; scorer: exact verdict match plus schema-validity.
Bar (single keyed run, model pin jev-1.13.0):
 accuracy >= 17/20 AND zero empty/truncated/non-JSON/schema-invalid
 outputs AND zero dropped verdicts (every output maps to exactly one
 stored structuredOutput) AND keyword-stand-in floor reported on the
 same 20 for the delta.
Record: N, prevalence of blocker-class, cost USD, p50/p95 end-to-end
 latency ms per gate call. No threshold retune after seeing answers.
NOT-RUN status reason: no Jev client exists at f4918e80
(package.json:96-102); the swap is a comment (claim 5, aspirational).
```

## T9 — fault behaviour on the shipped client surface

There is no Jev judgment client, so no Jev timeout/429/malformed/missing-key injection was possible. Cause: `package.json:96-102` depends only on `acorn, jiti, typebox, undici, yaml`; `undici` is host fetch-dispatcher plumbing (`src/runs/background/runner-http-dispatcher.ts:98-115`, default idle timeout `DEFAULT_HTTP_IDLE_TIMEOUT_MS = 300_000`, `:8`), not a judgment client. Routes tried: (1) `grep -rn "jev\|typesafe" package.json src --include='*.ts'` — hits are the `classify:4-5` comment and docs prose only, no import, no POST; (2) `grep -rn "fetch(" src/runs --include='*.ts'` — hits are runner/proxy plumbing and child-session transport, no scoring endpoint. What WAS fault-exercised, keylessly:

| fault | surface | behaviour (observed) |
|---|---|---|
| timeout | tool-timeout resolver (`src/runs/shared/tool-timeout.ts`): precedence per-call > frontmatter > config > env (`:62-90`); fast tools default 300s (`:8-14`); `contact_supervisor`/`intercom`/`bg_wait` exempt (`:17`); message `Tool 'x' exceeded its timeout of Nms.` Unit-covered (`test/unit/tool-timeout.test.ts`, green inside the suite). Verify commands default 120s (`acceptance.ts:1250`); `timed-out` fails the run exactly like `failed` (`:1624`, `:1693`). | fail-closed, message-stable |
| malformed | typed-gate stdout (`acceptance.ts:1306-1317`): empty/truncated/non-JSON/schema-invalid → `failed` + `structuredOutputError`, verdict never dropped. Proven by the plant (expected `rejected`, coerced `verified`, RED). Boundary noted: `classify --stdin` itself is an unvalidated keyword layer — garbage in returns `{"verdict":"ok","risk":0}` exit 0 (observed), schema enforcement lives in the gate, not the script. | fail-closed at gate; unvalidated at script |
| missing-key | `classify` needs none by design (claim 1: two fixtures, exit 0, no env). Jev missing-key is N/A — no client to withhold a key from (cause + routes above). Nearest shipped analogue, read not injected: the intent arbiter with missing auth returns `"unavailable"` and never rescues the completion guard (`src/runs/shared/llm-intent-arbiter.ts:257`, `:283-286`; `>8000`-char tasks refused before any model contact, `:224`, `:278-280`). | N/A by design; analogue fails closed |

## T10 — verdict and floor

Result class: **SELF**. The number this run owns is the unit suite at this pin: exit 1, 3261 pass / 25 fail / 23 cancelled / 12 skipped, of 3321 tests in 145088 ms — plus the plant pair (control 9/0 exit 0; planted 8/1 exit 1 naming the coercion). No floor arm and no incumbent arm were run: there is no labelled Jev question at this pin.

Keyless floor on the repo's own decision surface (keyword `classify`, $0, no model): the two `workflow.js` triage fixtures (`examples/typed-gate/workflow.js:16-19`) route correctly — blocker report → `blocked`/`0.6`, typo report → `ok`/`0` — and the rule table spans `blocked`/`0.9` (blocker+secret) through `ok`/`0` (LGTM) to `ok`/`0` on unrecognized garbage. Any future Jev swap (T4 bar above) must report its delta against this floor on the same inputs.

NO-CLAIM: this receipt does not say Jev would grade a review, does not price a call, does not explain the 25 failures, and does not treat the prior receipt as a pass. A missing key was not turned into a score. A malformed body was not coerced in the clone; the coercion existed only in the `/tmp` plant, where the test rejected it.

**Boundary.** Measures the unit suite, five claims, the shipped fault surface, and a keyless floor at `f4918e80` on this host. Does not prove a live Pi session delegates, does not call Jev, does not fault a networked client, does not clean or explain the lockfile dirt, and does not file the 25 failures upstream. The plant is not in the clone. Re-running the suite can move the 25/23 counts (prior lead: 3260/26/23/12); the plant command is the red-arm check, not a second certification.

Re-run, from the jev repo root, profiles unset:

```
env -u OMP_PROFILE -u PI_PROFILE -u PI_CODING_AGENT_DIR npm --prefix pi-subagents run test:unit
```

Plant re-run (copy only; control first, then the `catch`-coercion at `src/runs/shared/acceptance.ts:1311-1313`, then):

```
env -u OMP_PROFILE -u PI_PROFILE -u PI_CODING_AGENT_DIR node --experimental-strip-types --import ./test/support/isolated-temp-root.mjs --test test/unit/typed-gate-output.test.ts
```
