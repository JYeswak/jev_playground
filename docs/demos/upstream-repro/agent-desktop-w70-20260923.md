# agent-desktop W7.0 receipt — 2026-09-23 (worker W70Desktop)

Clone: `/Users/josh/Developer/jev/agent-desktop` at `a4a695fdd1f673426579696c7e17074910e799fc` (`a4a695f`). Class: tool/integration. The clone was not edited. No key value was printed. The desktop was not clicked and the `agent-desktop` binary was not spawned.

Re-run (keyless, no desktop, no key):

```sh
unset OMP_PROFILE PI_PROFILE PI_CODING_AGENT_DIR
cd /Users/josh/Developer/jev/agent-desktop && node scripts/jev/act.test.mjs && node scripts/jev/run.test.mjs
```

Evidence levels: a number below is either a command exit I ran, a live response field (N, model, and time stated), or a file:line I read. A live token count does not justify an accuracy or a dollar figure. Those are not claimed.


## Results

| id | status | evidence |
|---|---|---|
| T1 | PASS | Full SHA, date, license, host, and runtimes below. Porcelain empty before the suites and after the live call. Not reverted. |
| T2 | PASS (JS) / NOT-RUN (Rust) | JS suites exit 0, 0 skips. Plant in `/tmp` turned both RED, exit 1. Rust never reached a worker. Four fields below. |
| T3 | PASS | Five claims below, each with the line that decides it. |
| T4 | PASS (smoke) | Four pinned `jev-1.13.0` calls on the clone's own fixture. No `--execute`. No accuracy claim (N=4 < 20, no labels). |
| T5 | NO TIE / NO ACCURACY | Lexical rule abstains on the original intent (3 hits). Majority constant not computable. Prevalence refused. |
| T6 | SMOKE | Same state through the adapter. OpenAI 401. Haiku agrees on the one row. No paired test. |
| T7 | NOT OBSERVABLE | No labels. N=4. Bins would not be calibration. |
| T8 | STABLE CHOICE | 3× same target and command. Reword keeps both. Confidence drops. |
| T9 | FAIL | Missing key does not become a score. A partial choice body does become `act`. |
| T10 | NO ACCURACY CLASS | Verdict below. NO-CLAIM stated. |

## T1 pin and environment

- SHA: `a4a695fdd1f673426579696c7e17074910e799fc`
- Date: `2026-09-22 21:42:18 -0400`
- Subject: `chore(main): release 0.9.4 (#218)`
- License: Apache License, Version 2.0 (`LICENSE:2`; line 1 blank). `Cargo.toml:9` says `Apache-2.0`.
- Host: `Joshs-Mac-Studio.local`, Darwin arm64. Not an RCH worker.
- node `v22.22.0`, npm `10.9.4`.
- `OMP_PROFILE`, `PI_PROFILE`, and `PI_CODING_AGENT_DIR` were unset before every command.
- `git status --porcelain` empty before the first suite and after the live call. HEAD still `a4a695f`. RCH printed a target-sync banner and then refused; porcelain stayed empty. Not reverted.
- Bar read before the first live call: `docs/demos/upstream-repro/w70-new10-t4-bar-20260923.md` at `1e594899ac52bd17f031842ab6d71a85a42c3334` (`2026-09-22 23:40:28 -0600`). First live call `2026-09-23T05:48:27Z`. Pin not retuned after the answers.
- Key presence: `len=107`. Value not printed. Infisical `~/.local/bin/infisical` 0.43.84. The upgrade nag was declined.

## T2 own suite

Unmodified, in the clone:

```
node scripts/jev/act.test.mjs   → ok, ACT_EXIT=0
node scripts/jev/run.test.mjs   → ok, RUN_EXIT=0
```

These files use `node:assert`. There is no skip API. Skip count: 0. They print `ok` or throw.

Plant, `/tmp/ad-w70-plant2` only. One line in the copy of `scripts/jev/policy.mjs:200`:

```
- export const BARS = { floor: 0.55, act: 0.7, risky: 0.9 };
+ export const BARS = { floor: 0.55, act: 0.99, risky: 0.9 };
```

`ACT_PLANT_EXIT=1`. First failure, verbatim:

```
AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:
'confirm' !== 'act'
    at file:///private/tmp/ad-w70-plant2/scripts/jev/act.test.mjs:66:8
```

`RUN_PLANT_EXIT=1`. First failure, verbatim:

```
AssertionError [ERR_ASSERTION]: only inside the band can the answer change anything
false !== true
    at file:///private/tmp/ad-w70-plant2/scripts/jev/run.test.mjs:193:10
```

The suite can go RED. Clone porcelain stayed empty.

### Rust — NOT-RUN

Nothing ran on a worker. No `Selected worker`. No `Remote command finished`. No `test result:` line. Local cargo was not used.

Route 1. Command:

```sh
cd /Users/josh/Developer/jev/agent-desktop
unset OMP_PROFILE PI_PROFILE PI_CODING_AGENT_DIR
RCH_VISIBILITY=verbose rch exec -- cargo test -j 2
```

Verbatim:

```
[RCH] refusing local fallback (compilation.allow_local_fallback=false; all workers failed preflight checks)
```

Exit 1. The warning cites `rch/src/hook.rs:998`.

Route 2. Command:

```sh
RCH_VISIBILITY=verbose RCH_WORKER=contabo-4 rch exec -- cargo test -j 2 -p agent-desktop-core
```

Verbatim:

```
[RCH-I006] requested worker set [contabo-4] refused (missing_runtime); 'contabo-4' lacks the required runtime/toolchain/target
[RCH] refusing local fallback (compilation.allow_local_fallback=false; ...)
```

Exit 1. Same hook line, `rch/src/hook.rs:998`. No remote-finished line.

Cause: `Cargo.toml:8` sets `rust-version = "1.89"`. Probe of contabo-2 (`rch workers probe contabo-2 --json`) returned `status: capability_missing`, `error_code: RCH-E205`, verbatim `missing rustup component(s) for 1.89.0: clippy, rustfmt`. Worker rustc on that probe was `1.100.0-nightly`. That probe is not a test result.

## T3 claims

| # | claim | status | line that decides it | tier |
|---|---|---|---|---|
| 1 | "Jev returns choices, never strings." (`skills/jev-desktop/SKILL.md:124`, `scripts/jev/act.mjs:13-14`) | partial | The request builder asks only `choice` and `noul` (`act.mjs:76-114`). The live body had no `score` key. `readAnswers` still accepts a string noul (`act.mjs:129-131`) and a choice with no confidence (`act.mjs:118-132`). | [Verified, High] for the request shape; the parser does not enforce "never strings" on the way back |
| 2 | Ordinary action needs 0.70. Destructive at 0.50 or more needs 0.90. Below 0.55 nothing acts. (`SKILL.md:149-151`) | demonstrated | `policy.mjs:200-220`. Green suite asserts the bands. Live r1: confidence 0.89, destructive 0.35, decision `act`, which matches the ordinary bar. | [Verified, High] |
| 3 | A Choice takes at most 254 elements. (`SKILL.md:177`) | demonstrated | `policy.mjs:15` and `act.mjs:29-30`. `run.test.mjs:168` expects `elements.length === 254` on a 300-node screen. | [Verified, High] |
| 4 | The unmodified client sends `jev-latest`. | demonstrated | Hardcoded at `act.mjs:74`. The loop reads `TYPESAFE_MODEL` or the same default (`policy.mjs:162`). The live call had to set `model` on the returned object or the pin would fail. | [Verified, High] |
| 5 | "No retry and no backoff. A 429 ends the call." (`SKILL.md:184`) | partial | `act.mjs:185` throws on any non-OK status, no retry, no `AbortSignal` (`act.mjs:177-184`). `run.mjs:39-41` retries 429, 503, and 529 up to three times. The skill's sentence is false for the loop. | [Verified, High] for the contradiction; 429 was not live-probed |

A sixth, not needed to fill the five: "up to sixty characters" (`SKILL.md:62-63`) is true of the loop (`policy.mjs:76` slices 60) and false of the single-step describer (`screen.mjs:64` slices 120).

## T4 live call

No-execute path exists: omit `--execute`. `SKILL.md:123`. `act.mjs:208` reads the flag. `act.mjs:300-307` runs the binary only when that flag is set and `decision` is `act`. That CLI path was not used. It hardcodes `jev-latest` (`act.mjs:74`), which fails the pin, and it snapshots a real app before the POST (`act.mjs:222`). The bar forbids acting on the real desktop.

The live call imported `buildRequest`, `readAnswers`, and `route` from the clone. It did not import `desktop.mjs`. It did not spawn `agent-desktop`. State is the screen in `scripts/jev/act.test.mjs` (Save As, File Format, Save, a disabled Gone, Documents, an unnamed field). `model` was set to `jev-1.13.0` on the object the builder returned. The clone file was not edited. Response `model` was `jev-1.13.0` on every call. HTTP 200. Host process stayed up. No `score` key in any body.

N=4 requests, 5 questions each (`target`, `command`, `present`, `destructive`, `needs_text`). Smoke, not a certification. No accuracy claim.

| tag | intent | ms | in / out | target | conf | command | decision |
|---|---|---:|---|---|---:|---|---|
| r1 | save the file | 480 | 1270 / 303 | `@s8f3k2p9:e3` (Save) | 0.89 | click | act |
| r2 | save the file | 220 | 1270 / 303 | `@s8f3k2p9:e3` | 0.92 | click | act |
| r3 | save the file | 196 | 1270 / 303 | `@s8f3k2p9:e3` | 0.89 | click | act |
| reword | press the control that writes this document to disk | 214 | 1276 / 303 | `@s8f3k2p9:e3` | 0.76 | click | act |

Token totals: 5086 in, 1212 out. Both counts finite. The response has no dollar field. Cost in USD is not invented. p50 and p95 are not observable (N=4 < 5). Per-call latency is the table.

Prevalence, run before treating any answer as a judgement. The fixture has no gold label. Command:

```sh
node work/jev-prevalence-first/prevalence-check.mjs /tmp/ad-w70-unlabelled.jsonl --truth gold
```

Three lines, verbatim. Exit 2.

```
near-threshold: n/a (no labels)
own-constant: NOT COMPUTABLE — 0 of 1 rows carry 'gold'
verdict: REFUSED — label a sample of this set before any Jev question is judged on it
```

## T5 floors

Majority constant: not computable. No labelled positive class. The prevalence check above is the evidence.

Lexical rule, frozen in the caller before the first response: tokens of length greater than 2; if exactly one offered element's name contains a token, pick it; otherwise abstain. Not retuned after the answers.

- "save the file" hits Save As, File Format, and Save. Choice: null (abstain). Jev picked Save and acted. Not a tie.
- The reword hits Documents only. Lexical picks `@s8f3k2p9:e5`. Jev still picked Save. Disagreement, not a tie. No gold, so this is not an accuracy comparison and does not refuse a seat. There is no seat on this fixture.

## T6 incumbent

Same state and the same five questions, from the dumped `buildRequest` payload. Adapter: `upstream/typesafe-ai/system-one-adapter-python`. `ProviderName` is only `"openai"` or `"anthropic"` (`src/system_one_adapter/providers/base.py:21`).

Route 1. `python3` with that `src` on `PYTHONPATH`. Verbatim: `No module named 'httpx2'`. Exit 2. File: the import of `httpx2` in `_client.py:13`.

Route 2. `uv run --no-active` from the adapter directory, under Infisical. The adapter loaded.

- `openai` / `gpt-4o-mini`: `TypeSafeAuthenticationError: 401 Incorrect API key provided`. The key text is withheld. This matches the already-recorded invalid OpenAI key; it is not a new claim about Jev. 1535 ms. No answers.
- `anthropic` / `claude-3-5-haiku-latest`: `TypeSafeNotFoundError: 404 model: claude-3-5-haiku-latest`. 687 ms.
- `anthropic` / `claude-haiku-4-5` (the adapter's own reference id): HTTP success, 4860 ms. `input_tokens` 2222, `output_tokens` 232. No dollar field. Choice `@s8f3k2p9:e3`, confidence 0.82, command `click` at 0.797. Present 0.95, destructive 0.15, needs_text 0.05.

Jev r1 and Haiku picked the same element and the same command on this one unlabelled row. N=1. No McNemar. No accuracy claim. Agreement is not a win.

## T7 calibration

Not observable. No gold label, so a bin has no accuracy. The four target confidences are 0.89, 0.92, 0.89, 0.76. Three of four sit in 0.8–1.0. That is a pile, not a reliability diagram.

## T8 stability

Identical state, three times: target flip 0/3, command flip 0/3, decision flip 0/3. Confidence moved 0.89 → 0.92 → 0.89.

Reword, same screen: target still Save, command still click, decision still act. Framing flip on the choice: 0. Confidence fell to 0.76 and still cleared 0.70. N=4, so this is a stability note, not a rate with a percentile.

## T9 fault behaviour

Missing key. Command, with the variable unset, not via Infisical:

```sh
node scripts/jev/act.mjs --app TextEdit "save the file"
node scripts/jev/run.mjs --app TextEdit "open the Applications folder"
```

Verbatim:

```
{"ok": false, "error": "TYPESAFE_API_KEY unset"}
```

`ACT_EXIT=1`, `RUN_EXIT=1`. No `score`, no `decision`, no confidence. The check is before any snapshot (`act.mjs:220` before `act.mjs:222`; `run.mjs:57` before `observe`). The desktop was not touched. A missing key does not become a score.

Malformed body. `readAnswers` on `{}`, `null`, a string, and a `type: "score"` body returns `{error: "response carried no target or command answer"}`. No `score` field is copied. `validateChoice` on `undefined`, a string confidence, and a score object throws `the model's answer did not name an offered option; nothing ran` (`policy.mjs:185`). The loop path refuses.

The act path does not. A choice body with no confidence is not an error (`readAnswers` returns the choice). `route` of that object returns `{decision: "act", why: null}`. Measured. The CLI checks `answers.error` (`act.mjs:244`) and then calls `route` (`act.mjs:270`), so this body would be acted on, not refused. A string noul (`"high"`, `"yes"`) is passed through (`act.mjs:129-130`) and `route` still returns `act`, because the string comparisons do not trip the numeric bars (`policy.mjs:204-210`). `route` of an error object — the object `readAnswers` returns for a score-typed body — also returns `act`. The CLI does not call `route` in that case. A caller that skips the error check would.

Timeout and 429 were not live-probed. `act.mjs:177` has no `AbortSignal`. `run.mjs:33` has none either. A 429 on the act path throws (`act.mjs:185`). A 429 on the loop path retries (`run.mjs:39`). Those lines are the cause. Routes tried: reading `ask`, reading `post`. A mock server was not stood up; the URL is a const inside the clone, and the clone was not edited.

Host process survived every probe that was run. T9 fails because a malformed choice body becomes `act`.

## T10 verdict

Result class: no accuracy class earned. Not SELF: there is no labelled win. Not FLOOR: the lexical rule abstained and Jev acted, which is not a tie, and there is no gold to score either arm. Not INCUMBENT: Haiku agreed on one unlabelled row. Prevalence verdict was REFUSED. No seat is claimed and none is refused.

NO-CLAIM: nothing here is a Jev accuracy, calibration, or dollar cost. The four live answers are a smoke of this client's request shape on its own test fixture. They do not say what `jev-1.13.0` does on a real desktop, and they do not say the lexical rule is a floor anyone should ship. The Rust suite was not run.

Earned labels: Rust T2 is NOT-RUN with both commands, both refusals, `Cargo.toml:8`, and the probe's `RCH-E205`. Timeout and 429 inside T9 were not executed; the two read routes and the file:line are above. Nothing else required was left NOT-RUN.

Spend: 4 Jev calls (5086 in / 1212 out) and 1 Haiku call (2222 in / 232 out). OpenAI was attempted once and rejected. No further calls.

## Boundary

This receipt covers `agent-desktop` at `a4a695fdd1f673426579696c7e17074910e799fc` on `Joshs-Mac-Studio.local`, from the pin check at `2026-09-23T05:38:48Z` through the Haiku call. Inside: the clean tree, both JS suites, one planted bar change, five claims, four pinned no-execute calls, one Haiku call on the same fixture, the missing-key refusal, and the malformed-body coercion. Outside, and not claimed: any click, any snapshot of a real app, any Rust `test result` line, any dollar figure, any accuracy, calibration, or McNemar, and any live behaviour of `jev-latest`. The live driver and the plant live under `/tmp` and are not part of the clone.
