# pi-subagents W7.0 — 2026-09-22

Clone: `pi-subagents` @ `f4918e80b531f1bf9f1d9e847b8f86c9016108f1` (2026-09-18 08:59:47 -0700, `chore(release): v0.69.0`). Class: tool/integration. Worker: W70Pi. Host: `Joshs-Mac-Studio.local` (darwin 25.5.0, arm64). Node `v22.22.0`, npm `10.9.4`. `OMP_PROFILE`, `PI_PROFILE`, and `PI_CODING_AGENT_DIR` unset before every command. License: MIT (`LICENSE:1`, `package.json:6`). Pin clock: 2026-09-23T03:15:43Z. Clone not edited. Prior lead `EVAL.md:290` (3263/23/23/12) is not evidence.

T4 bar, written before this wave and not retuned: `docs/demos/upstream-repro/w70-t4-bar-20260922.md` @ `da2a785db92e15f314aa47829015d84f0a038d97` (2026-09-22 21:14:20 -0600). Model pin named there: `jev-1.13.0`. No live call was made, so the bar was not applied.

| id | status | result |
|---|---|---|
| T1 | FAIL | Pin recorded. Cleanliness fails. Before and after the suite: `M package-lock.json` only (2 deletions, both a `"peer": true` line under dev packages; no source change). SHA, date, license, host, worker, Node/npm, and the three unset profile vars are recorded above. This run did not add dirt and did not revert the lockfile. |
| T2 | PASS | Own suite ran and a planted defect turned a `/tmp` copy RED. The suite itself is red. See counts and plant below. |
| T3 | PASS | Five claims, each with the line that decides it. |
| T4 | NOT-APPLICABLE | This clone does not call Jev. The only mention is a comment inviting a swap (`examples/typed-gate/classify:4-5`). No SDK, no POST, no key (`package.json:96-102`). |
| T5 | NOT-APPLICABLE | Seat/benchmark floor arm. This clone asks no labelled question. |
| T6 | NOT-APPLICABLE | Seat/benchmark incumbent arm. No Jev call and no labelled rows. |
| T7 | NOT-APPLICABLE | Calibration needs a live choice distribution. None exists. |
| T8 | NOT-APPLICABLE | Stability needs repeated live asks. None exist. |
| T9 | NOT-APPLICABLE | No Jev client to fault. `package.json:96-102` depends on acorn, jiti, typebox, undici, yaml. Undici is a host fetch dispatcher (`src/runs/background/runner-http-dispatcher.ts:98-115`), not a judgment client. |
| T10 | PASS | Result class **SELF**. No accuracy claim. |

## T2 — own suite

Command, from the clone, profiles unset:

```
npm run test:unit
```

which is `node --experimental-strip-types --import ./test/support/isolated-temp-root.mjs --test test/unit/*.test.ts` (`package.json:61`).

Counted run wrote the spec reporter to a file outside the clone. Exit **1**. Duration **138917 ms**. Evidence: test, N=3321, 2026-09-23 UTC, no model. Lane: local `npm run test:unit` on this host, not a live Jev call.

| | |
|---|---|
| tests | 3321 |
| suites | 356 |
| pass | 3260 |
| fail | 26 |
| cancelled | 23 |
| skipped | 12 |
| todo | 0 |

A first `npm run test:unit` in the same pin also exited 1. Its captured log was truncated before the footer, so the table is the second run.

Skips, from the spec markers and the `skip:` expressions. The runner counted **12**. The spec file printed **13** skip markers. Both numbers are reported; none was dropped to force a match.

| reason | where |
|---|---|
| `Set PI_SUBAGENTS_NATIVE_SDK to the isolated 0.85.1 SDK root` (8 tests) | `test/unit/acceptance-compaction.test.ts:19` |
| `Set PI_SUBAGENTS_NATIVE_SDK to an installed real Pi SDK root` | `test/unit/watchdog-native-scheduling.test.ts:15` |
| describe skipped: `process.platform !== "win32"` (darwin) | `test/unit/herdr-session-roots-codec.test.ts:30` |
| `process.platform !== "win32"` | `test/unit/owned-process-tree.test.ts:14` |
| `Windows-only platform boundary` | `test/unit/orca-progress-tabs.test.ts:82` |
| `Windows path comparison` | `test/unit/single-output.test.ts:250` |

Fail files, not a triage: `herdr-connection.test.ts:25` (acknowledgement timed out), `herdr-inspector.test.ts` (pending promise after the event loop resolved; parent cancellation), `host-command.test.ts:130` (`false !== true`), `native-supervisor-channel.test.ts:96` / `:129` (after-hook expected a `requests` child, saw the channel directory), `orca-progress-tabs.test.ts` (several duration-0 failures), `watchdog-lsp-diagnostics.test.ts:93` (expected `failed`, actual `timeout`). Cancelled **23** are a separate counter, not folded into the 26.

### Plant

Copy: `/tmp/pi-subagents-w70-plant` (clone tree without `.git`, `node_modules` symlinked). Clone bytes unchanged.

Control, same runner, unplanted copy: `test/unit/typed-gate-output.test.ts` — **9 pass, 0 fail, exit 0**, including `fails the gate on invalid or empty stdout instead of dropping the verdict` (`typed-gate-output.test.ts:113`).

Plant, only in the copy, `src/runs/shared/acceptance.ts` catch that used to fail invalid JSON (`acceptance.ts:1311-1312` at the pin): invalid JSON now sets `structuredOutput = { coerced: true }` and returns. Re-run of that one test:

```
not ok 1 - fails the gate on invalid or empty stdout instead of dropping the verdict
location: test/unit/typed-gate-output.test.ts:113:2
expected: 'rejected'
actual: 'verified'
PLANT_EXIT:1
```

The suite can fail, and the failure names the planted coercion. This is not a certification of the 26 pre-existing failures. Evidence level: test, N=1 planted assertion, 2026-09-23 UTC, no model. Lane: `/tmp` copy only.
## T3 — claims

| # | claim | status | evidence | decides it |
|---|---|---|---|---|
| 1 | The typed-gate example is a keyword stand-in and runs with no API key (`examples/typed-gate/README.md:3`, `classify:3-5`). | demonstrated | test, N=2 stdin fixtures, 2026-09-23 UTC, no model | Ran `classify --stdin` with no key. `P0 blocker` + `secret token` → `{"verdict":"blocked","risk":0.9,...}` exit 0. `LGTM no issues found` → `{"verdict":"ok","risk":0,...}` exit 0. Rules: `classify:31-34`. |
| 2 | A typed gate's stdout must be one JSON document; anything else fails the gate and the verdict is not dropped (`examples/typed-gate/README.md:38`, `docs/tool-reference.md:424-425`). | demonstrated | test, N=9 in the control file, 2026-09-23 UTC, no model | `TYPED_VERIFY_OUTPUT_MAX_BYTES = 12_000` and the fail paths (`src/runs/shared/acceptance.ts:1290-1312`). Control test above passed. The plant inverted `rejected` to `verified`. Typed gates are also not memoized (`acceptance.ts:1340-1343`; test `typed-gate-output.test.ts:132-139`, passed in the control). |
| 3 | `maxSubagentSpawnsPerRun` defaults to 64 (`README.md:101`). | demonstrated | test, inside the N=3321 suite, 2026-09-23 UTC, no model | `DEFAULT_MAX_SUBAGENT_SPAWNS_PER_RUN = 64` (`src/shared/types.ts:2918`) and the resolver falls through to it (`types.ts:2927-2928`). Fresh suite passed `formats a bounded successful environment summary` (`test/unit/doctor.test.ts:51`, assertion `:120`: `configured limit: 64 (default)`). |
| 4 | Command-runner / external-cli agents are async-only; a direct foreground call is refused (`docs/workflows.md:243`, `examples/typed-gate/README.md:41`). | partial | inspection, N=0 executions of that branch | The refusal is in source: if the agent is external and the call is not async, or `foregroundOnly` is set, the executor returns an error (`src/runs/foreground/subagent-executor.ts:6994-6995`). This run did not send that call. |
| 5 | Swap the keyword `score` body for TypeSafe Jev and keep the JSON shape (`classify:4-5`). | aspirational | inspection, N=0 Jev calls | Comment only. No `typesafe` dependency (`package.json:96-102`). No POST and no model pin in the tree. |

## T4

NOT-APPLICABLE. `examples/typed-gate/classify:4-5` names TypeSafe Jev as one thing a human might swap in. The script that runs is `grep` (`classify:31-34`). Nothing in `package.json:96-102` or the import graph calls `jev-1.13.0` or `jev-latest`. The precommitted bar was not applied and was not changed after seeing an answer, because there was no answer.

## T9

NOT-APPLICABLE. There is no client that sends a judgment request, so timeout / 429 / malformed body / missing key were not injected. The host-model intent arbiter is not that client: on timeout, throw, or missing auth it returns `unavailable` and does not rescue the guard (`src/runs/shared/llm-intent-arbiter.ts:238-239`, `:257`, `:283-286`). That path was read, not fault-injected, because the assignment limits T9 to a client this package does not have.

## T10 — verdict

Result class: **SELF**. The number this run owns is the unit suite at this pin: exit 1, 3260 pass / 26 fail / 23 cancelled / 12 skipped, of 3321 tests, in 138917 ms. No floor arm and no incumbent arm were run, because there is no labelled Jev question. No accuracy, cost, or latency claim. N is not stated for a live call; nothing here is a certification.

RULEBOOK tier, per claim: 1–3 **[Verified]** (executed at this pin). 4 **[Verified]** as an inspection of the refusal line, and the claim status stays **partial** because the branch was not executed. 5 **[Verified]** that the Jev swap is absent; the claim itself is aspirational, not disproven as a future invitation.

NO-CLAIM: this receipt does not say Jev would grade a review, does not price a call, does not explain the 26 failures, and does not treat `EVAL.md:290` as a pass. A missing key was not turned into a score. A malformed body was not coerced in the clone; the coercion existed only in the `/tmp` plant, where the test rejected it.

**Boundary.** Measures the unit suite and five claims at `f4918e80` on this host. Does not prove a live Pi session delegates, does not call Jev, does not fault a client, does not clean or explain the lockfile dirt, and does not file the 26 failures upstream. The plant is not in the clone. Re-running the suite can move the 26/23 counts; the plant command is the red-arm check, not a second certification.

Re-run, from the jev repo root, profiles unset:

```
unset OMP_PROFILE PI_PROFILE PI_CODING_AGENT_DIR && npm --prefix pi-subagents run test:unit
```

## Non-author re-run

Same command, 2026-09-22 21:32 local. Exit 1. `# tests 3321`, `# pass 3262`, `# fail 24`, `# cancelled 23`, `# skipped 12`, `# duration_ms 45629`. The receipt's 3260/26 is not stable. The red exit is.
