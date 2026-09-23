# typesafe-mario W7.0 receipt — 2026-09-23 (worker W70Mario)

Clone: `/Users/josh/Developer/jev/typesafe-mario` @ `ca22449ed187118d19326d1f54b01b6636578aa4`. Class: seat, control loop. Live model pin required by the bar: `jev-1.13.0`. Live calls this receipt: N=0. Cost: $0.00. p50/p95: not observable (N<5). Result class: **UNEARNED** (not SELF, not FLOOR, not INCUMBENT).

The T4 bar was read before any live call: `docs/demos/upstream-repro/w70-new10-t4-bar-20260923.md` at `1e594899ac52bd17f031842ab6d71a85a42c3334` (2026-09-22 23:40:28 -0600, `[pending] preregister the new-clone T4 bar`). Ledger row `notes/deep/clone-ledger.tsv` and any older EVAL note are leads, not passes. `EVAL.md` was not edited. The clone was not edited. No ROM was downloaded. No `infisical run` was issued, because the ROM hard limit blocked the call before a key was needed. Shell `TYPESAFE_API_KEY` length 0 is not evidence the key is absent; the canonical key is in Infisical and was not loaded.

| id | result | evidence |
|---|---|---|
| T1 | PASS | SHA, date, license absent, clean status before and after, host and toolchain below |
| T2 | PASS | `pytest -q` on a `/tmp` archive of the pin: 10 passed, 0 failed, 0 skipped, exit 0. Plant in that copy only: 1 failed, 9 passed, exit 1 |
| T3 | PASS | 7 claims, each with file:line, below |
| T4 | NOT-RUN | No ROM on disk. Bar `:19`. Searches and the unstarted play command below. N=0, cost $0.00 |
| T5 | NOT-RUN | No labelled rows and no live rows. Floors not computable |
| T6 | NOT-RUN | Same-state incumbent arm has no rows. Adapter tree exists; it was not called |
| T7 | NOT-RUN | No live confidences to bin |
| T8 | NOT-RUN | No live answers to repeat or reword |
| T9 | NOT-APPLICABLE | Seat/control-loop profile is T1–T8+T10 (`docs/PLAN-DEEP-KIT-20260922.md:439`). Fault injection is not owed. Client exists at `policy.py:37,113` |
| T10 | UNEARNED | Verdict below. NO-CLAIM: nothing here is a Jev answer |

## T1 — pin and environment

- Full SHA `ca22449ed187118d19326d1f54b01b6636578aa4`, commit date `2026-09-15 21:59:07 -0700`, subject `feat: add TypeSafe Mario agent demo`, author `fhshaik`.
- License: absent. `ls LICENSE* COPYING*` → `No such file or directory`. Matches the ledger lead `none (no LICENSE file)`; re-derived, not copied as a pass.
- `git status --porcelain` empty before the first test command and after the last probe. HEAD unchanged.
- Host: `Joshs-Mac-Studio.local`, Darwin 25.5.0 arm64. Measured `2026-09-23T05:38:17Z`.
- `OMP_PROFILE=grok`, `PI_PROFILE=grok`, `PI_CODING_AGENT_DIR=/Users/josh/.omp/profiles/grok/agent`. No `omp` command was run.
- Runtime used for the suite: CPython 3.13.11 via `uv 0.9.28` (project requires `>=3.13`, `pyproject.toml:10`). System `/usr/bin/python3` is 3.9.6 and was not used. In the copy venv: `pytest==9.1.1`, `typesafe-sdk==0.7.1`, `ruff==0.16.8` (ruff was installed by `.[dev]` and not run; the named suite command is `pytest -q`, `ci.yml:23`).

## T2 — own suite, fresh

The suite ran in `/tmp/w70-mario`, a `git archive HEAD` of the pin, so an editable install and pytest cache could not dirty the clone.

Command:

```text
/tmp/w70-mario/.venv/bin/python -m pytest -q
```

Verbatim:

```text
..........                                                               [100%]
10 passed in 0.02s
EXIT:0
```

Skips: 0. No skip line, so none to list by reason. Tests are `tests/test_state.py` (7) and `tests/test_dashboard.py` (3). They do not import `typesafe_sdk` and do not call the network.

A first `pytest -q` launched from `/Users/josh/Developer/jev` (wrong cwd) is not this result. It died in collection with `PluginValidationError: unknown hook 'pytest_recording_configure'` from `system-one-adapter-python/tests/conftest.py`. That run is discarded.

Plant, only in the copy: `src/typesafe_mario/actions.py` `JUMP_RELEASE_ACTION[Action.JUMP]` changed from `Action.NOOP` (`actions.py:32`) to `Action.RIGHT`. Re-run of the same `pytest -q` in `/tmp/w70-mario`:

```text
..F.......                                                               [100%]
FAILED tests/test_dashboard.py::DashboardTests::test_jump_macros_have_non_jump_release_frames - AssertionError: <Action.RIGHT: 'right'> != <Action.NOOP: 'noop'>
tests/test_dashboard.py:19: AssertionError
1 failed, 9 passed
PLANT_EXIT:1
```

The suite can fail. The copy was restored from `git archive` after the plant. Clone porcelain stayed empty.

## T3 — claim inventory

Evidence rank on every claim below is the justifier, not the README. Ranks used: `test` (pytest on the pin), `oracle` (this run's command output or a file:line read of the pin), `live N` (a `jev-1.13.0` answer). No claim below is justified by `live N`. Lane: W70Mario keyless-plus-blocked-live, 2026-09-23, model not called (pin would have been `jev-1.13.0`).


1. DEMONSTRATED — The model does not receive screenshots, and the tile grid is not in the model payload. `README.md:6-11`. `MarioSnapshot.to_state` returns nine groups and no grid (`state.py:252-294`). `to_debug_state` keeps `local_grid` (`state.py:323-327`). `TypeSafePolicy.choose` sends `snapshot.to_state()` (`policy.py:113`). `typesafe-mario state-demo` exit 0: model keys `episode, hazard, level, objective, player, reaction_timing, recent_control, terrain, trajectory`; `local_grid` absent from that object and present in the debug object. Field names contain the substrings `pixels` and `frames` (distances and horizons). Those are not image bytes. `screenshot` / `image` / `rgb` are absent from the model JSON.

2. PARTIAL — Jev chooses one of seven legal macros. The set is real: `Action` has `noop, right, right_jump, right_run, right_run_jump, jump, left` (`actions.py:6-13`; `README.md:19-27`). A keyless fake client recorded one `system_one` whose Choice criteria were exactly those seven strings. That Jev selected among them was not run. The clone also does not pin the model: `TypeSafeClient()` is constructed with no `model` argument (`policy.py:37`; `TypeSafePolicy.__init__` has no `model` local). Installed `typesafe-sdk` 0.7.1 defaults to `jev-latest` (`typesafe_sdk/constants.py:18`, env `TYPESAFE_DEFAULT_MODEL` at `:9`). Probe: `CLIENT_DEFAULT_MODEL jev-latest`, `MODEL_ARG_ON_CALL None`. An unmodified `play` would send `jev-latest`, which fails the committed pin (`w70-new10-t4-bar-20260923.md:9`). A future live run must set `TYPESAFE_DEFAULT_MODEL=jev-1.13.0` outside the clone.

3. DEMONSTRATED as request shape, not as answers — Each decision is one `system_one` with Choice `next_action`, Noul `jump_needed`, and Score `danger` (`README.md:103-107`; `policy.py:56-113`). Fake client, no HTTP: `QIDS ['danger', 'jump_needed', 'next_action']`, types `Choice` / `Noul` / `Score`, one call. Live answers: NOT-RUN (T4).

4. DEMONSTRATED — Default cadence is 8 emulator frames. `--frames-per-decision` default 8 (`cli.py:65-67`). The Choice instructions say the action is held at least 8 frames (`policy.py:61`). Headless loop steps `frames_per_decision` times (`runner.py:273`). Dashboard requests a new decision only when `frame_index - last_request_frame >= frames_per_decision` (`runner.py:152`). `state-demo` printed `reaction_timing.action_horizon_frames` 8. Caveat, not a disproof: if the previous call is still pending, the dashboard keeps the old action (`runner.py:148-152`), so a slow call holds longer than 8. The ledger's "~133ms at 60fps" is an inference from `state.py:534` (`previous_latency_ms / (1000/60)`), not a measured frame time in this run.

5. DEMONSTRATED — Timing arithmetic stays in code, including `jump_must_start_this_decision` (`README.md:109-112`). Unmodified `pytest` passed `tests/test_state.py:99-102`: with `previous_latency_ms=100` and `previous_response_delay_frames=8`, `takeoff_deadline_frames==0`, `last_inference_delay_frames==8`, and `jump_must_start_this_decision` is true. That fact is parser output, not a model answer.

6. PARTIAL — "there is no scripted recovery-action override" (`README.md:112`). `TypeSafePolicy.choose` returns the model's action unchanged (`policy.py:119-130`). The dashboard loop replaces a new grounded jump macro with `JUMP_RELEASE_ACTION` for one frame so the A button gets an up edge (`runner.py:163-165`). The headless loop does not (`runner.py:269-274`). `HeuristicPolicy` does script jump-when-stalled (`policy.py:138-140`). Its docstring says it is an offline smoke test, "not intended as the Mario benchmark baseline" (`policy.py:134`). That sentence is the author's scope limit, not a measurement against Jev.

7. STALE — The README text-view sample does not match this pin's `state-demo`. `README.md:88` says `moving right`; the command printed `nearly_stationary`. `README.md:96` shows a full ground row `###########`; the command printed `########...` under Mario (`state-demo` lines 91 and 102). The structured groups in `README.md:76-82` still match `to_state` (`state.py:252-294`).

## T4 — live Jev (NOT-RUN)

Cause: a legally obtained ROM is not on this machine. Hard limit `docs/demos/upstream-repro/w70-new10-t4-bar-20260923.md:19` and `notes/deep/dispatch/p2-w70-new10-live.md:29`. Do not download one. Parent confirmed: do not start a live call until a path is sent. No path arrived before this write.

Command that would have been the live arm, not executed:

```text
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- env TYPESAFE_DEFAULT_MODEL=jev-1.13.0 typesafe-mario play --env SuperMarioBros-1-1-v0 --frames-per-decision 8 --display none --max-decisions 20
```

Verbatim output of that command: none. It was not started.

Route 1 — known ROM caches, no download. `/Users/josh/roms`, `/Users/josh/ROMs`, `/Users/josh/Games` absent. Walk of `~/Library/Application Support`, `/tmp`, and Homebrew share, depth 4, skipping `node_modules` / `site-packages` / `.git`: `HITS 0`.

Route 2 — filename index, a different source. `mdfind 'kMDItemFSName == "*.nes"c'` → `NES_COUNT:0`. OpenEmu, RetroArch, BizHawk, Mesen, Nestopia library paths absent. `glob /Users/josh/**/*.{nes,rom,unf}` → no files. `gym_super_mario_bros` and `nes_py` are not installed in the measurement interpreter.

A non-live play attempt (heuristic policy, so `TypeSafePolicy` was not constructed, no key, no ROM install):

```text
/tmp/w70-mario/.venv/bin/typesafe-mario play --policy heuristic --display none --max-decisions 1 --frames-per-decision 8
```

```text
RuntimeError: Mario dependencies are missing. Install with: pip install -e ".[mario]"
PLAY_EXIT:1
```

Raised at `runner.py:37` from `cli.py:94`. Installing `.[mario]` was not done: that would not create a ROM, and the bar forbids running without one already on disk.

Prevalence check was not run. It applies before a labelled live call (`w70-new10-t4-bar-20260923.md:5`; `work/jev-prevalence-first/prevalence-check.mjs:17`). This clone has no rows file (`git ls-files` is 14 paths, no jsonl). `checkUnlabeled` refuses a constant (`prevalence-check.mjs:14`). There is no labelled positive class, so prevalence is NOT-APPLICABLE (`docs/PLAN-DEEP-KIT-20260922.md:431`). No accuracy claim. N=0 is under 20.

## T5 — floors (NOT-RUN)

Command: `git -C /Users/josh/Developer/jev/typesafe-mario ls-files`. Verbatim: 14 paths, listed under T1's tree (`.gitattributes`, `ci.yml`, `.gitignore`, `README.md`, `pyproject.toml`, six modules, two test files). No gold action column.

Cause: `docs/PLAN-DEEP-KIT-20260922.md:432` requires the same rows as T4. Those rows do not exist. File:line of the missing corpus: there is no data file; the closest offline policy is `HeuristicPolicy.choose` (`policy.py:136-146`), which is explicitly not a baseline (`policy.py:134`).

Route 1: the file list above. Route 2: ROM search in T4, which is what would have produced live rows to score. Neither produced a label.

## T6 — incumbent (NOT-RUN)

Command not executed:

```text
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <adapter on the same state and questions>
```

Verbatim: none. Cause: `w70-new10-t4-bar-20260923.md:22` requires the same state as T4. No state was sent. Adapter directory is present (`upstream/typesafe-ai/system-one-adapter-python/pyproject.toml` exists) and was not imported into a call.

Route 1: directory check, `ADAPTER_DIR True`. Route 2: ROM search in T4. The blocker is the missing ROM, not a missing adapter.

## T7 — calibration (NOT-RUN)

Command: none that bins confidences. Verbatim: no probability rows. Cause: `docs/PLAN-DEEP-KIT-20260922.md:434` needs live bins with counts. File:line of the confidence field that was never filled: `policy.py:125` (`action_answer.confidence`), unread from the API.

Route 1: fake-client probe set `confidence=0.5` locally and did not bin it (a constant from a stub is not calibration). Route 2: ROM search in T4.

## T8 — stability (NOT-RUN)

Command: the T4 play command, three times, plus one reword of `policy.py:59`. Not executed. Verbatim: none. Cause: `docs/PLAN-DEEP-KIT-20260922.md:435` rides on live asks. File:line of the question that would be reworded: `policy.py:59`.

Route 1: ROM search. Route 2: heuristic play failed at `runner.py:37` before any decision, so there is no action to flip.

## T9 — fault behaviour (NOT-APPLICABLE)

Seat/control-loop profile runs T1–T8+T10 (`docs/PLAN-DEEP-KIT-20260922.md:439`). This packet's mario row is T1–T3 plus live T4–T8 only when a ROM exists (`notes/deep/dispatch/p2-w70-new10.md:27`; `p2-w70-new10-live.md:29`). T9 is the SDK/client/tool arm (`PLAN:436`). Not NOT-RUN. A later fault probe could use `policy.py:113`, but this receipt does not owe it and did not run it.

## T10 — verdict

(a) Result class UNEARNED. SELF, FLOOR, and INCUMBENT all require a live arm or a labelled cache this clone does not have. Lane W70Mario, date 2026-09-23, model not called (`jev-1.13.0` pin unread by the API). Live N=0. Cost $0.00. No percentile. Justifier rank for this sentence: oracle (ROM searches + unstarted play command), not live N.


(b) Tiers: claims 1, 3 (shape), 4, and 5 DEMONSTRATED on this pin without a key. Claims 2 and 6 PARTIAL. Claim 7 STALE. The README's "Jev chooses" sentence is not a model result.

(c) NO-CLAIM: nothing in this receipt is a Jev answer, a latency, a token count, a calibration, a floor comparison, or an incumbent comparison. The official SDK call shape is demonstrated. Whether `jev-1.13.0` plays Mario is unmeasured. An unmodified client would send `jev-latest` (`policy.py:37`, SDK `constants.py:18`); that is a pin defect for the next live run, not a measured model difference.

Earned NOT-RUN: T4–T8, each with command, verbatim (or an explicit unstarted command), file:line, and two routes. T9 is NOT-APPLICABLE by profile, not a missing measurement.

Claim ranks: (1) oracle, `state-demo` exit 0 plus `state.py:252-294`. (2) oracle for the seven criteria; live N=0 for "Jev chooses". (3) oracle, fake client, HTTP N=0. (4) oracle, `cli.py:67` and `state-demo` horizon 8; the 133ms figure is not claimed. (5) test, `tests/test_state.py:99-102` passed. (6) oracle, `runner.py:163-165` vs `policy.py:119-130`; not a live override count. (7) oracle, `state-demo` text vs `README.md:88,96`.


## Boundary

This receipt covers `typesafe-mario` at `ca22449ed187118d19326d1f54b01b6636578aa4` only. It does not edit the clone, `EVAL.md`, or any other clone. It does not download a ROM, construct `TypeSafeClient` against Infisical, or send `system_one`. Plants and the suite lived in `/tmp/w70-mario`. A ROM path arriving later is a new run, not a revision of these N=0 numbers.

Did not run: live `play` under Infisical; `TYPESAFE_DEFAULT_MODEL=jev-1.13.0` against the API; `.[mario]` install; any ROM download; `prevalence-check.mjs` (no rows file); T5 majority and lexical floors; T6 adapter call; T7 bins; T8 repeats and reword; T9 missing-key / 429 / malformed-body probes; ruff; `EVAL.md` append. Numbers above are lane W70Mario, N as stated, date 2026-09-23, model uncalled.
