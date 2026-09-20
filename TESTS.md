# TESTS.md — the jev lane test registry

What is tested here, by whom, and the exact command. **Three surfaces, and they are not
interchangeable:** what we own, what upstream owns, and what only a live call can show.

Gate inventory (the enforcement layer, distinct from the tests themselves):
[`GATES.md`](GATES.md). Acceptance bar: [`AGENTS.md`](AGENTS.md) §4.

---

## Tracked test files — the enumeration

Every test file committed to this repo, by path. A test surface nobody enumerated is a coverage
claim nobody can check:

- `compaction/test/adapter.test.ts` — the omp transcript adapter's mapping tests, including the
  known-bad (a trailing `toolResult` must be kept) and **both live envelopes**: `message_end`
  (the `--mode json` stream) and `message` (the on-disk SessionEntry), which must produce
  identical messages, plus a planted negative that an unknown envelope still yields nothing.
  Gated by `foundation/gates.d/40-omp-compact-replay.sh`.
- `work/oracle-kit/test.mjs` — the shared scorer's self-test, **10 checks, every case a defect
  this lane actually shipped on 2026-09-19**: a constant score must be flagged rather than
  returned as a clean `0.500` (three bogus router runs), a degenerate label must throw rather
  than yield `NaN` (the gate's feasibility arm), and a field name absent from the SDK must throw
  rather than score silence (`.distribution` / `.probability`). Plus positive observables: AUC
  separates a real signal in both directions, ECE is 0 when calibrated, and the e-process
  accumulates toward rejection while staying conservative on few observations.
  Plus **R33's mechanical fix**: `requireKey` refuses to let absence be claimed without the
  record's own key list in the error, and `inspectKey` returns that list alongside the lookup —
  written after the eighth wrong-selector failure in one session, the only one that reached a
  published receipt.
  Run: `node work/oracle-kit/test.mjs` (13 checks).
- `compaction/test/hindsight.test.ts` — the hindsight oracle (`compaction/hindsight.ts`), which
  scores Jev's keep/drop decisions against the transcript's own future. 4 tests: a drop counts as
  a mistake only when the result is later reused; the **planted negative** that keeping everything
  scores zero mistakes but must still show the missed saving; a token present earlier is not a
  fingerprint (this defect made the first run report 90% mistakes on noise); and the random
  baseline drops the same count with alignment intact.
- `compaction/test/hook-compact.test.ts` — the omp compaction hook surface (sibling-owned, bead
  `jev-compact-hook-hbs`).
- `work/omp-harm-rule/verify-claim.mjs` — imports the shipped harm rule and verifies the committed 12/12 recall and 0/38 false-positive denominator. Run: `node work/omp-harm-rule/verify-claim.mjs` (exit 0 on the committed corpus; mutation arm is documented in the claim receipt).
- `work/omp-harm-rule/harm-error.test.mjs` — a throwing classifier must yield kind `harm_error` with NO score field (fails on the old harm_pass/0 code), plus unchanged fire/pass paths. Run: `node --test work/omp-harm-rule/harm-error.test.mjs` (2 tests).
- `work/omp-harm-rule/install-harm-rule.sh` — temp-`OMP_HOME` installer arms: missing install RED, install GREEN, check GREEN, idempotent rerun, empty block list, and inline-list refusal. Run against a disposable profile, never a real one — exit codes `1`, `0`, `0`, each taken **unpiped** (`| head` reports head's status and showed a false `0` on the refusal arm). Full arm table, plus the three defects these arms caught, in [`installer-grade-20260919.md`](docs/demos/upstream-repro/installer-grade-20260919.md) and `NEGATIVE_EVIDENCE.md` R35.
- `work/omp-jev-preaction/test/preaction.test.mjs` — deterministic preaction gate: all six policy patterns fire (wipe-root, wipe-star, mkfs, dd-device, forkbomb, chmod-root); the false-positive arm proves ordinary daily commands do NOT fire, including a scoped `node_modules` delete, `chmod +x`, a `dd` to a file rather than a device, and the pattern quoted inside an `echo`; non-bash tools ignored; a missing or non-string command never throws; a throwing host still returns undefined; and every fire names what matched. Run: `node --experimental-strip-types --test work/omp-jev-preaction/test/preaction.test.mjs` (6 tests).
- `work/omp-jev-commit/test/commit.test.mjs` — commit-message-vs-diff scorer: non-commit and message-less commands ignored, the `-F <file>` form (which this repo mandates) is read from the FILE not the command line, a `-F` pointing at a missing file is ignored rather than crashing, an inline `-m "..."` is parsed, unset key -> `commit_error` with no scores, and a throwing host still returns undefined. Run: `node --experimental-strip-types --test work/omp-jev-commit/test/commit.test.mjs` (6 tests). **Three arms are conditional on a staged diff existing in the cwd and therefore pass on a no-op** — the unconditional proof of the scored path is `live-probe.mjs`, which builds a real throwaway repo with a real staged diff.
- `work/omp-jev-rerank/test/rerank.test.mjs` — observe-only search-result scorer: non-search tools and errored results ignored, short lists skipped, a bare-string `result` (the shape I invented) rejected rather than accepted, a scored list reports real hit count vs capped scored count, unset key -> `rerank_error` with no scores, transport throw -> `rerank_error`, and a throwing host still returns undefined. Run: `node --experimental-strip-types --test work/omp-jev-rerank/test/rerank.test.mjs` (7 tests).
- `work/omp-jev-review/test/review.test.mjs` — observe-only diff review scorer: ignores non-diff tool calls, unset key records `review_error` not a pass, throwing transport records `review_error`, a real score records `review_scored` with probabilities, a 200 with no probabilities is an error, a throwing host still returns undefined, and it asks exactly the two MEASURED questions and no more (the `scope` question was cut as degenerate and mis-ordered; the test pins `Object.keys(questions)` so it cannot silently return). Run: `node --experimental-strip-types --test work/omp-jev-review/test/review.test.mjs` (7 tests).
- `work/jev-client/test/client.test.mjs` — the ONLY sanctioned systemOne caller: asserts the exact wire shape (`model` + `state` + `questions` as an object of `{type:'noul',instructions}`), unset key -> `unconfigured` with the infisical fix in the error, HTTP 400 surfaced with the server body, `.probability`/`.distribution` rejected, non-JSON, transport throw, partial answers, and empty questions refused before any network call. Also the MULTICLASS caller `askJevChoice`: `{type:'choice',instructions,criteria}` with `criteria` a MAP (the SDK refuses a list), a degenerate class set refused before any network call, and five plausible-looking 200s — a label never offered, no `choice`, `.distribution` instead of `.probabilities`, a label missing from `probabilities`, non-numeric `confidence` — each refused rather than read, because a scorer that shrugs at a missing field fabricates a finding instead of crashing. Also `readRow`, which handles BOTH omp session row shapes (`customType` as an object with nested `data`, and `customType` as a string with top-level `data`) — a reader that handles one silently reports "no rows" on the other, which is the root cause of R33 and R41. Run: `node --experimental-strip-types --test work/jev-client/test/client.test.mjs` (14 tests, 21 including subtests).
- `work/jev-client/test/uncertain.test.mjs` — uncertainty-ranked selection, deterministic random audit sampling, coarse score buckets, and no-near-threshold negative. Run: `node --test work/jev-client/test/uncertain.test.mjs` (4 tests).
- `work/jev-client/test/measure-kit.test.mjs` — the standard verdict arithmetic, offline with a fake asker: a planted constant (6/7 correct, same verdict everywhere) comes back DEGENERATE, a planted one-item margin with a near-threshold decider comes back WEAK (the 010dd96 correction encoded), a clear separator DISCRIMINATES, and the driver counts drift flips and transport errors. Run: `node --test work/jev-client/test/measure-kit.test.mjs` (4 tests).
- `work/omp-jev-failure/test/failure.test.mjs` — planted errored-tool arms for the MULTICLASS classifier: `failure_classified` carries one class plus its full distribution at `schemaVersion: 2` and no longer carries `scores`, the call itself is ONE choice question over the three mutually-exclusive classes (`classes`, never a question map) — the shape that took the committed eleven cases from 9/11 with two structurally impossible answers per run to 11/11 with none, `failure_error` without a class, non-error ignored, and fail-open append/classifier failures. Run: `node --experimental-strip-types --test work/omp-jev-failure/test/failure.test.mjs` (5 tests).
- `work/omp-jev-foreman/test/foreman.test.mjs` — local-trigger progress observer: healthy window no trigger, repeated-command score, classifier error without scores, and fail-open host. Run: `node --test work/omp-jev-foreman/test/*.test.mjs` (4 tests).
- `work/omp-jev-route/test/route.test.mjs` — pre-staged peer route observer tests. Run: `node --experimental-strip-types --test work/omp-jev-route/test/route.test.mjs`.
- `work/omp-jev-route/test/process.test.mjs` — skillranker process slice: `__none__` abstention, empty-roster unavailable, explicit local resolve, fit/exclude/already-loaded, structured JSON envelope, fail-open writer. Run: `node --test work/omp-jev-route/test/process.test.mjs`.
- `work/omp-jev-route/test/gate.test.mjs` — copied 0/1/2 loss table, always-abstain counterexample (their `expected_values.v1.json` cohort), `diagnostic_synthetic` cannot promote. Run: `node --test work/omp-jev-route/test/gate.test.mjs`.
- `probes/fast-jev-probe.mts` — our black-box probe of the compaction library against a fake Jev. Run: `npx tsx probes/fast-jev-probe.mts` → 8 assertions.

- `work/dogfood-logger/test/logger.test.mjs` — append-only decision/outcome logger: joined false-positive scoring, malformed/orphan record handling, concurrent append preservation, and rotation. Run: `node --test work/dogfood-logger/test/logger.test.mjs` (4 tests).
- `work/omp-jev-observer/test/observer.test.mjs` — observe-only OMP tool_call extension: cost-present, missing-cost, error-cost-absent, timeout, ID, and absent-context sentinel paths. Run: `node --test work/omp-jev-observer/test/observer.test.mjs` (8 tests).
- `work/taste-loop/test/detect.test.mjs` — shared path/tool/regex gates for the taste-loop packages: write-tool set, user-facing path exclusions, heckle planted class, destructive vs way-back, onboarding/skip, preselection/form, first-look paths, event readers, headline/CTA extract. Run: `node --experimental-strip-types --test work/taste-loop/test/detect.test.mjs` (9 tests).
- `work/omp-jev-heckle/test/heckle.test.mjs` — observe-only error/empty/loading copy scorer: planted dead strings take the regex and do not call Jev, remainder unset-key/`heckle_error`, throwing transport, scored probabilities, 200-without-answers is an error, appendEntry throw still undefined, wire pins `next_action` only. Run: `node --experimental-strip-types --test work/omp-jev-heckle/test/heckle.test.mjs` (8 tests).
- `work/omp-jev-firstlook/test/firstlook.test.mjs` — first-screen choice scorer: non-first-look writes ignored, empty buffer on session_stop writes 0 rows, unset key → `firstlook_error`, throwing transport, scored choice, 200-without-answers is an error, appendEntry throw, wire pins `lost|hunting|got_it`. Run: `node --experimental-strip-types --test work/omp-jev-firstlook/test/firstlook.test.mjs`.
- `work/omp-jev-fork/test/fork.test.mjs` — two-variant choice: first write 0 decisions, same-content second write does not call Jev, different second write unset key → `fork_error`, scored A/B/none, appendEntry throw. Run: `node --experimental-strip-types --test work/omp-jev-fork/test/fork.test.mjs`.
- `work/omp-jev-promise/test/promise.test.mjs` — headline vs CTA: missing headline/CTA 0 rows, exact-verb match → `promise_regex` and no fetch, remainder unset key → `promise_error`, scored `keeps_promise`. Run: `node --experimental-strip-types --test work/omp-jev-promise/test/promise.test.mjs`.
- `work/omp-jev-jargon/test/jargon.test.mjs` — engineering-stoptoken gate then noul: copy without tokens 0 rows, `hydrate the payload` unset key → `jargon_error`, scored `client_word`. Run: `node --experimental-strip-types --test work/omp-jev-jargon/test/jargon.test.mjs`.
- `work/omp-jev-undo/test/undo.test.mjs` — destructive UI: non-destructive 0 rows, way-back copy → `undo_regex` and no fetch, no-exit unset key → `undo_error`, scored `way_back`. Run: `node --experimental-strip-types --test work/omp-jev-undo/test/undo.test.mjs`.
- `work/omp-jev-field/test/field.test.mjs` — form battery: non-form 0 rows, unset key → `field_error`, scored three nouls, wire pins `placeholder_dup|recoverable|user_language`. Run: `node --experimental-strip-types --test work/omp-jev-field/test/field.test.mjs`.
- `work/omp-jev-default/test/default.test.mjs` — preselection remainder: no defaultChecked 0 rows, unset key → `default_error`, scored `serves_client`. Run: `node --experimental-strip-types --test work/omp-jev-default/test/default.test.mjs`.
- `work/omp-jev-skip/test/skip.test.mjs` — onboarding exit: non-onboarding path 0 rows, `Skip for now` → `skip_regex` and no fetch, `Continue` unset key → `skip_error`, scored `can_leave`. Run: `node --experimental-strip-types --test work/omp-jev-skip/test/skip.test.mjs`.
- `work/omp-jev-uncanny/test/uncanny.test.mjs` — product-as-observer noul: ordinary copy 0 rows (prefilter gate), `I noticed you haven't` unset key → `uncanny_error`, scored `watching`. Run: `node --experimental-strip-types --test work/omp-jev-uncanny/test/uncanny.test.mjs`.
- `work/omp-jev-heat/test/heat.test.mjs` — brief-vs-yak choice on `context`: empty context 0 rows, unset key → `heat_error`, scored five-label choice `golden_path|supporting|yak|hygiene|none`. Run: `node --experimental-strip-types --test work/omp-jev-heat/test/heat.test.mjs`.
**This list is machine-checked.** `foundation/gates.d/70-tests-registry-sync.sh` fails when a
tracked test file is not named here, or when a named path no longer exists — because a hand-written
registry goes stale the hour a sibling lands a suite, and a stale registry reads authoritative
while being wrong. Add the path when you add the test; the gate is the consumer that makes it stay
true.

Everything else under this root is a **vendored clone** and its tests belong to its owner
(section 2). They are not tracked here by design — see `.gitignore`'s allowlist, which is also why
`git ls-files` can be an exhaustive scan.

---

## 1. Ours — first-party, offline, no key

| Suite | Command | What it proves | Count at last run |
|---|---|---|---|
| `probes/fast-jev-probe.mts` | `npx tsx probes/fast-jev-probe.mts` | black-box behavior of the compaction library against a **fake** Jev: verbatim text preservation, message order, truncation-to-head+note on drop, unknown-answer-key ⇒ keep (the fail-safe direction) | 8/8, reduction ratio 0.91 |
| `foundation/run_calibration.py` | `cd foundation && python3 run_calibration.py` | our thresholds against the labelled held-out set; emits a receipt under `foundation/runs/` | ECE 0.061, Brier 0.020, Noul 58/60, Choice 19/20 (receipt `20260917T224444Z.json`) |
| `foundation/gates.sh` | `cd foundation && ./gates.sh` | **every** wired stage against the real tree — the suite globs `gates.d/[0-9]*-*.sh`, so the stage count is derived, never fixed here | **8/8 PASS** at `a503b9a`; this row said `4/4` and `the four gate stages` for four stages' worth of additions (pane 2, `3e198bb`) |
| `foundation/gates.sh --selftest` | `cd foundation && ./gates.sh --selftest` | **every stage proves it can go RED** on a planted bad input | **8/8 PASS** at `a503b9a`; same stale-count correction |
| `githooks/commit-msg-verification-level.sh --selftest` | as written | the commit-edge hook refuses a level-less subject and accepts a level-carrying one | 4 known-bad refused, 4 known-good passed, 1 prose-not-claim refused |
| `compaction/` (sibling-owned) | see that directory's own scripts | the omp transcript adapter and its known-bad (a trailing `toolResult` must be kept) | gate `40-omp-compact-replay.sh` PASS |

**Rule:** a green here is the only green we may call *ours*.

---

## 2. Upstream's — each vendored clone runs its own suite

We do not own, extend, or fix these. A failure is a **finding about that clone**, recorded in
`EVAL.md`, never a task to fix by editing it.

| Clone | Command | Recorded result |
|---|---|---|
| `fast-jev-compaction` | `npm run typecheck && npm test && npm run build && npm run validate:plugin` | 29/29, plugin validates |
| `jev-review` | `npm run validate` (tsc + `node --test` + esbuild) | 13 tests green |
| `jev-mcp` | `npm test` (9, no key) · `npm run test:e2e` (4, **live**) | 9/9, 4/4 |
| `jev-ultrafast` | `uv sync && uv run ruff check . && uv run pytest` | 31/31 · `scripts/check_guards.py` 21/21 vs real headless Chrome |
| `awesome-jev-by-typesafe` | `uv run pytest tests/` | 11/11, stdlib only |

The full census (~20 clones, growing) is derived, never hardcoded — see `AGENTS.md`
§ *The census*. A clone with no row above is `EXPLORED`, not tested.

---

## 3. What no offline suite can show

- **Model behavior.** Only a live call against `jev-latest` shows it, and it is budgeted, stated,
  and recorded with N + model version (`jev-1.13.0` at time of writing).
- **Calibration over time.** A receipt is evidence for the exact fixture bytes it names;
  `20-receipt-freshness.sh` enforces that.
- **An omp seam firing.** Rungs L2 (loads) → L3 (fires, and a known-bad makes it refuse) → L4
  (survives a session) in `AGENTS.md`. Nothing reaches L3 without a pasted frame or transcript.

## Deliberately not here

Coverage percentages. This lane's test surface is a handful of first-party files plus other
people's suites; a repo-wide coverage number would average our 8 assertions against ~20 vendored
projects and mean nothing. Per-suite counts above are the honest unit.

## 4. Routing backtest — first-party offline

- `demos/routing-backtest/test/reader.test.mjs` — transcript denominator extraction and the empty-classifiable-set ERROR arm. Run: `cd demos/routing-backtest && npm test`.
- `demos/routing-backtest/src/counterfactual.test.mjs` — deterministic cheap-route policy, recorded-spend preservation, missing-price ERROR, unknown-model fixture RED arm, and missing-spend failure. Run: `cd demos/routing-backtest && npm test`.
- `demos/routing-backtest/test/hostile-input.test.mjs` — the §4 hostile-input arm: four named refusal codes (MALFORMED_JSONL, INVALID_USAGE_TOKENS, DUPLICATE turn index, NON_STRING_SESSION_ID), asserting the reader REFUSES and executes nothing rather than crashing or silently accepting. 6 tests. Run: `cd demos/routing-backtest && npm test`.
- `demos/retransmit-whatif/test/whatif.test.mjs` — known-shape recovery of all four token fields plus denominator, and malformed/negative usage recorded as failures. 2 tests. Pane 3's grade (`docs/demos/duel-2/runs/whatif-grade-20260918T150327Z.json`) records the gap: no test asserts the 25/50/75 scenario outputs, which are the product's actual figures. Run: `cd demos/retransmit-whatif && npm test`.
- `demos/usage-shape/test/shape-bin.test.mjs` — the §4 tests box for the shipped `bin/shape.mjs`: directory input walks JSONL and reports exact denominator/share/residual, and an empty directory FAILS CLOSED rather than emitting a green empty result. 2 tests. Authored by a non-author of bin/shape.mjs per the authorship rule. Run: `cd demos/usage-shape && npm test`.
- `compaction/test/omp-binding.test.ts` — the omp pre-compaction BINDING: it registers a `session_before_compact` handler, REFUSES a malformed envelope (no messages, empty messages) rather than guessing, returns `undefined` when the compactor declines so omp keeps its own summarizer, never presents a non-shrinking result as a compaction, and its default export throws rather than installing without a configured `JevAsker`; plus a REAL omp transcript (179 events, 11 tool results paired) driven through `omp-adapter.ts`, which reaches the Jev-outage branch the synthetic fixtures could not and asserts the reason is reported verbatim; and the `decisionLogPath` sink, which appends one line per decision and degrades to silence on an unwritable path rather than breaking the handler; and the PRODUCTION envelope, pinned from a real `/compact`: the transcript arrives at `preparation.messagesToSummarize`, not `messages`, and its messages carry `role: custom` with `content` as a bare string. 9 tests. Run from the repo root: `npx tsx --test compaction/test/omp-binding.test.ts`.
- `compaction/test/ab-verdict.test.ts` — the stochastic-verdict withhold rule: a single observation carries spread and establishes nothing, a differing sample set REFUSES a verdict, and only zero-spread samples permit a requested one. 3 tests. Run: `cd compaction && npm test`.
- `demos/routing-backtest/test/adapt-claude.test.mjs` — the Claude-shape adapter's two DECLARED rules and its refusals: no price sheet exits 2 rather than inventing rates, an unpriced model is refused and named, prompt tokens are input + cacheRead (the rule the backtest's NO_BASELINE_CANDIDATES floor forced), cache multipliers apply as declared, and the emitted table marks converted models `recorded` while the cheap candidate stays `scenario`, and a sheet still carrying the template's REQUIRED placeholders is refused rather than used; plus the chain's CLI contract, that a --max-prompt-tokens run records the EFFECTIVE policy in its receipt rather than the default, and that the receipt's blockedBy histogram names each blocked turn's reason without ever aggregating as `unrecorded`. 8 tests. Run: `cd demos/routing-backtest && npm test`.
- `demos/doc-drift/test/judge.test.mjs` — the doc-drift judge's decision surface. Registered
  2026-09-18 after `foundation/gates.d/70-tests-registry-sync.sh` fired RED on it live: it was
  tracked and unnamed here, a sibling landing whose registry update never happened. Run:
  `cd demos/doc-drift && npm test`.
- `demos/preaction-abstention/test/gate.test.mjs` — the pre-action abstention gate's own suite,
  the same landing-without-registry-update class. Run: `cd demos/preaction-abstention && npm test`.

**How these two were found, because it is the point of gate 70 and of this file.** Neither was
discovered by anyone reading `TESTS.md`. `foundation/gates.sh` globs `gates.d/[0-9]*`, so gate 70 was
**auto-wired and RED on the live tree**, and pane 3's registry audit
(`audit-gates-registry-20260918T110806Z.json`, `85d75a0`) surfaced it: *"it fires RED on the live
tree right now and nothing else watches `TESTS.md`."* **The conductor had not run
`foundation/gates.sh` this session and so did not know the suite was failing.**

### `ensemble/test_decorrelation.py` — 5 tests

Covers the predicate behind `RECIPES.md` recipe 4: oppositely-shaped errors make averaging pay;
phi is reported; mismatched lengths and empty input are refused with the lengths named. The
load-bearing one is the **planted negative** — averaging a scorer with *itself* must buy exactly
zero and report `AVERAGE_DID_NOT_PAY`, because a measurement that showed a gain there would be
measuring arithmetic rather than decorrelation. Run: `cd ensemble && python3 -m unittest test_decorrelation`.

### `ensemble/run_all.py` — runner, not a test suite

Reproduces recipe 4's predicate across three pairs from upstream's committed out-of-fold scores
(no API key, no training). Not registered as a test because it asserts nothing; its value is the
printed ordering, including the **correlated control** (`logreg + naiveBayes`, same features,
phi +0.53) which loses accuracy when averaged. The assertions live in
`ensemble/test_decorrelation.py`. Run: `python3 ensemble/run_all.py`.

## `work/toolcall-judge-v3/rules-v4.test.mjs` — 10 tests

Run: `node --test work/toolcall-judge-v3/rules-v4.test.mjs` (no API key; pure classification).

Guards the mention-vs-use stripper, which is load-bearing: every "false positive fixed" claim in
`docs/demos/upstream-repro/judge-seat-ruling-20260920.md` rests on it, and all 28 of the v3
regex's fires on 77,767 real commands were mention-not-use.

1. stripper removes heredoc bodies, so text ABOUT a command does not fire
2. stripper removes quoted prompt payload
3. PLANTED NEGATIVE: the real command still fires after stripping
4. PLANTED NEGATIVE: stripping must not hide a real secret write
5. J2 from real traffic: the reassuring echo does not suppress the finding
6. token capture via login --plain fires
7. credential scraped out of a settings file fires
8. ordinary traffic stays silent — the fleet lives here
9. v3 fires on quoted payload where v4 does not — the measured defect, pinned
10. stripQuotedPayload only removes, never invents

Tests 6 and 7 FAILED on first run and caught a real bug: `"$(...)"` and backticks are quoted but
EXECUTED, so stripping them hid real token capture. Command substitutions are now protected
before quote removal and restored after.

## `work/jev-score-register/register.test.mjs` — 10 tests

Run: `node --test work/jev-score-register/register.test.mjs` (no API key; pure local I/O).

Guards the two properties jevcache got wrong, which is why they are planted negatives rather than
happy paths: the raw input must be unrecoverable from the register, and two different inputs must
never share an identity.

1. PLANTED NEGATIVE: the jevcache collision cannot happen here
2. PLANTED NEGATIVE: no field is dropped, whatever it is called
3. PLANTED NEGATIVE: the raw input is not recoverable from the register
4. register file is created 0600, not 0644
5. identity is stable across key order
6. rows round-trip, and a torn final line does not lose the rest
7. a failed call is recorded as a gap, never as a passing score
8. recording() does not change the wrapped answer
9. recording() records a failure without inventing a score
10. recordScore refuses a row it cannot attribute

Test 1 encodes the measured jevcache defect directly: `{"command_id":"rm -rf --no-preserve-root /"}`
and `{"command_id":"echo hello"}` shared a fingerprint there and it served the benign answer for
the destructive command. Here they must differ.
