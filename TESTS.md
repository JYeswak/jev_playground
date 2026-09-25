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
- `work/oracle-kit/test.mjs` — the shared scorer's self-test, **every case a defect
  this lane actually shipped**: a constant score must be flagged rather than
  returned as a clean `0.500` (three bogus router runs), a degenerate label must throw rather
  than yield `NaN` (the gate's feasibility arm), and a field name absent from the SDK must throw
  rather than score silence (`.distribution` / `.probability`). Plus positive observables: AUC
  separates a real signal in both directions, ECE is 0 when calibrated, and the e-process
  accumulates toward rejection while staying conservative on few observations.
  Plus **R33's mechanical fix**: `requireKey` refuses to let absence be claimed without the
  record's own key list in the error, and `inspectKey` returns that list alongside the lookup —
  written after the eighth wrong-selector failure in one session, the only one that reached a
  published receipt.
  Plus **§4(a) `decisionLoss`**: always-abstain mean loss equals nPos/n on the skillranker
  10/12 identity (0.833); false abstain costs 1, wrong/needless cost 2; a table that
  omits `false_abstention_on_positive` lets always-abstain win (planted negative).
  Plus **§4(d) selector≡claim**: `{noul:0.9}` scored as `probabilities` throws;
  `assertSdkSelector` refuses `.distribution` / an invented `helpfulNoul`;
  `refuseInventedNoulGate` refuses a second noul on a Choice pick.
  Plus **select-on-A/report-on-B** (`protocol.py` port): stratified halves are
  deterministic, `bestThreshold` keeps the lowest on ties, `selectSingleSignal`
  picks the best-A feature and reports on B, a single-signal input returns
  `selected:false` (planted `selected:true` fails `true !== false`), and a
  fitted logistic separates separable data deterministically.
  Run: `node work/oracle-kit/test.mjs` (29 checks).
- `work/oracle-kit/prevalence_threshold.py` — t*(π) on frozen priors 30/186449 and 488/50149.
  Run: `python3 work/oracle-kit/prevalence_threshold.py` (exit 0; prints the 1:2300 identity).
- `work/oracle-kit/selector-guard.mjs` — scorers cannot silently read `.distribution` / `.probability`.
  Run: `node work/oracle-kit/selector-guard.mjs` and Run: `node work/oracle-kit/selector-guard.mjs --selftest` (7 planted real answer reads RED, tool-details reads pass; jev-56o4 made the selftest its own row).
- `work/oracle-kit/voi_harm_rule.py` — VOI of paid Jev vs free regex on the frozen harm-rule corpus.
  Run: `python3 work/oracle-kit/voi_harm_rule.py` (exit 0; VOI ≤ 0; NO-CLAIM).
- `scripts/promotion-four-gates.py` — four-gate VIEW over existing receipts; empty evidence fails.
  Run: `python3 scripts/promotion-four-gates.py --selftest` (exit 0) and
  `python3 scripts/promotion-four-gates.py UP-R5-jev-toolcall-gate` (exit 1 today; STATUS not written).
- `work/ci-main-status/test_ci_main_status.py` — `scripts/ci-main-status.py` (jev-bfku) against
  trimmed real gh output in `work/ci-main-status/fixtures/`, no network: green is one line and exit
  0 with no log fetch; the ff8316d red run (36059723283) names `registered-suites` and its
  `test_runner_gates.py … FAIL` row, exit 1, and stays exit 1 when the log fetch fails; a green with
  newer unfinished pushes gets a STALE line; gh failing, gh absent, gh unauthenticated (gh 2.94.0's
  own stderr), gh hanging past the timeout, no completed run, and a cancelled run all print NOT_RUN
  and exit 2; log rows: gates `RED` stage plus its `FAIL` checks, `RED named`, and the runner's
  echoed script source is not a row; the newest scheduled/workflow_dispatch README stranger run is
  reported with result, age, first mismatch, and STALE after 36 h, with no completed run as NOT_RUN.
  Planting `failure` into GREEN fails 2 tests.
  Run: `python3 -m unittest work/ci-main-status/test_ci_main_status.py` (19 tests).
- `work/omp-jev-review/test_judge_usage.py` — the judge-role section of
  `work/omp-jev-review/surface-census.py` and its `--fleet-line` (jev-xpk1), on row shapes copied
  from real omp 18.3.0 session files, no model calls: success rows are calls, tokens and cost by
  kind/day/purpose/profile/project; the planted-failure shape (`stopReason: "error"` +
  `errorMessage`, what `TYPESAFE_BASE_URL=http://127.0.0.1:9` wrote) and `aborted` count as
  failures and the line names the last reason; a `/tmp` probe session stays out of the real counts;
  another provider's judge-role error and a row older than 24h are not counted; no session files is
  `NOT_RUN`, never "0 failures"; `scripts/fleet-idle-watch.py --once` prints the line and keeps exit
  0 with a failure in it; a HOME under `/tmp`, `/private/tmp` or a `probe` dir still counts real
  sessions (is_probe reads only the path below the sessions root plus cwd; the old whole-path rule
  failed 5 of 7 on Linux CI 36079745187). Planting "drop failure rows" in `judge_rows` fails 4 of 8.
  Run: `python3 -m unittest work/omp-jev-review/test_judge_usage.py` (8 tests).
- `work/omp-jev-review/test_skill_census.py` — the `Skills 24h:` line of
  `work/omp-jev-review/surface-census.py --fleet-line` (jev-yy7f), on row shapes copied from real
  omp session files, no model calls: a `read` of `skill://<name>` or `skill://<name>/<file>`, a read
  under `.claude/skills/<name>/` or `.agents/skills/<name>/`, a skill file as an argument of a bash
  file reader (grep/cat/sed/..., `python3 -c "open(...)"`), an `eval` cell calling `read(`,
  `tool.read(` or `open(` on one (py and JS cells, copied from codex sessions), and the
  `skill-prompt` invocation row each count; a glob or directory listing, a skill path inside a
  message (`ntm send '...'`, `br comments add "..."`, pane 1's real dispatches), a Python cell that
  only quotes a read call in a string, a toolResult that quotes the header, non-skill reads, a `/tmp`
  probe session, a row older than 24h and a call whose toolResult is `isError: true` ("Unknown
  skill" in a pane older than the install) do not; a skill missing from
  `~/.claude/skills/THIRD-PARTY-SKILLS.tsv` counts in the total only; no ledger is
  `third-party NOT_RUN (no ledger)` and no session files is `NOT_RUN`, never zero; the CLI prints
  the judge line, the skills line, then the key exposure line (jev-9ov4),
  `scripts/fleet-idle-watch.py --once` shows them, and a census timeout is NOT_RUN for all three.
  Plants, each restored byte-identical: drop the absolute-path
  branch fails 5 of 17; e9d037e's any-mention bash rule 1; drop the bash reader branch 2; drop
  `python -c` 1; drop the eval branch 2; Python cells by regex instead of ast 1; ignore error
  results 2; HEAD's watcher fails the timeout test.
  Run: `python3 -m unittest work/omp-jev-review/test_skill_census.py` (17 tests).
- `work/omp-jev-review/test_key_exposure.py` — the `Key exposure 24h:` line of
  `work/omp-jev-review/surface-census.py --fleet-line` and its pane-1 page in
  `scripts/fleet-idle-watch.py` (jev-9ov4), keyless: every key is generated per run with the live
  shape (`apikey_` + 35 + `_` + 64 of `[a-z0-9]`, the pattern read from `.omp/secrets.yml`) and
  each output is checked for key text first, with a message that never quotes it. A session file
  holding one counts and the line names its path and mtime, never the key; two 106-character near
  misses (34 before the `_`, 63 after) and a file last modified 25h ago do not count; a `/tmp`
  probe session under `~/.omp/agent/sessions` does; the newest 3 of 4 paths, newest first; many
  keys in one file is one file; `flags: "i"` and `/.../i` literals are honoured; a missing or
  unparsable `secrets.yml` (empty, plain-only, a regex that does not compile, not `key: value`, a
  bad quoted value) and no session files are `NOT_RUN`, never zero; the CLI prints it as the third
  line. Marked fakes (35-character segment starting `fakefake`, what our tools generate): a file
  holding only them is not counted and is reported as `M hold only marked fakes`; a marked fake
  ahead of an unmarked key, on the same line or an earlier one, still counts. Page: a new path
  pages pane 1 once (send injected), a second round and a restart (fresh module, same state file)
  page nothing, a second path pages only itself, a failed send is retried, a file holding only
  marked fakes pages nothing, 0 or NOT_RUN pages nothing and writes no state, an unreadable state
  file is `Key page: NOT_RUN`, and the forever loop pages in its first round. Plants, each restored
  byte-identical: drop the 24h window fails 1 of 18; print the match 11 (0 key-shaped strings in
  the failure output); page every round 4; ignore the marker 2 of 21; only the first match on a
  line 1 of 21.
  Run: `python3 -m unittest work/omp-jev-review/test_key_exposure.py` (21 tests).
- `work/omp-jev-review/test_jev_tool_census.py` — the `Jev tools 24h:` line of
  `work/omp-jev-review/surface-census.py --fleet-line` (jev-x28o), keyless, on session fixtures in the
  real row shapes: `write`/`read` calls to `xd://<tool>` and a call made by the tool's own name count
  per tool of the shipped roster (`.omp/tools/jev-*.ts`, `jev-rerank.ts` -> `jev_rerank`); tools with
  zero calls are named, or `every tool called`; a call whose `toolResult` is `isError: true`, a probe
  session (`omp-test` profile, a `/tmp` cwd), a load probe (`<tool>_ext_probe`), a call older than
  24h and a tool outside the roster do not count; no sessions and no roster are `NOT_RUN`. Plants,
  each restored byte-identical: count failed calls 1 fails; count probe sessions 1; drop the roster
  filter 2; drop the 24h window 1. The census CLI now prints four lines, and the watcher's census
  fallback names all four (`test_skill_census.py`, `test_key_exposure.py`).
  Run: `python3 -m unittest work/omp-jev-review/test_jev_tool_census.py` (8 tests).
- `work/fleet-idle-watch/test_fleet_idle_watch.py` — `scripts/fleet-idle-watch.py`'s classifier
  on process evidence (jev-6con), no tmux or ps: fixtures are the real process trees of jev panes
  0, 2, 4, 5 and two real screens, 2026-09-25. Both measured false readings: a screen with no
  status line over a live omp reads idle or working, never `no-agent`; an idle `❯` over a live
  `infisical run -- docker run` reads `working (child: docker run ...)`. Plus a bare zsh is
  `no-agent`, a helpers-only omp with a 600 s old session file is `idle`, the 60 s freshness
  boundary, omp's helpers (`OMP_HELPERS`) are not tools while a subprocess of its eval kernel is,
  and the status-line `--selftest` (7/7). The HEAD screen-only classifier fails both false-reading
  fixtures; planting "ignore descendants" in `omp_processes` fails 3 of 14. Agent Mail pages
  (jev-lqfm), on archive files written per test in the real `…__42478.md` shape with the send
  injected: urgent and high page pane 1 once each as `MAIL <importance> from <from>: <subject>
  (id <id>, <HH:MM>Z)`, normal never; a second poll pages nothing; a restart (fresh module, same
  state file) pages nothing, including an urgent from before start - 15 min that the first run
  kept as history; a new high after round 1 pages; an id already in the state file does not; a
  malformed front matter is named in the `Inbox:` line, not raised; a failed send is retried; a
  missing inbox dir and an unreadable state file are `Inbox: NOT_RUN`; `--once` prints the Inbox
  line after the skills line. Plants, each restored byte-identically: page every importance fails
  7 of 24; drop the persisted set fails 7 of 24. README stranger failures from the CI line
  (jev-gbdb) page pane 1 once per run id, including stale failures; failed sends retry and
  success/NOT_RUN never page.
  Wait marker (jev-t54m, jev-oxdq): a wait with a session idle 600 s+ and nothing but helpers or
  nothing at all under omp is `stalled-wait`; a CPU-active child, or a live child at 0.0 CPU (a
  paced `work/openrouter-incumbents/run.py`, session idle 900 s), is `working`. Plant "require
  CPU again" fails 1 of 30.
  Run: `python3 -m unittest work/fleet-idle-watch/test_fleet_idle_watch.py` (33 tests).
- `work/omp-secret-probe/test_omp_secret_probe.py` — verdicts of `scripts/omp-secret-probe.py`
  (jev-doc7), the live check that omp hides a TypeSafe-shaped key from the model (jev-xw3f), on
  the answer shapes real sessions gave on 2026-09-25. REDACTED needs positive placeholder
  evidence: the claude placeholder (`$$TYPES` .. `:L$$`, 33 characters), the codex one without
  `$$` (`TYPESAF` .. `21:L`, 29) and an unlabelled `$$3P8W5` .. `:L$$`. LEAKED is any head or
  tail that is a piece of the fake key, also in quotes or backticks, off by one, miscounted, with
  only the head right, or with only the tail right. Everything else is UNCLEAR, never REDACTED:
  the non-author check's live `LEN=UNAVAILABLE ...` answer (planted file gone), a `cat:` error
  line, `none`, a missing field, a placeholder with the full 107-character length (also written
  `107.`), a placeholder
  head with a non-placeholder tail. No answer is NOT_RUN. The fake key has the live shape,
  differs per run, and starts its 35-character segment with the `fakefake` marker the key census
  skips (jev-9ov4). Plants, each restored byte-identical: REDACTED on the length alone fails 4 of
  12; tail-only leak detection 1; head-only leak detection 1; head OR tail placeholder 1; no quote
  stripping 2; only `$$` heads count 1; an unmarked fake_key() 1 of 13.
  Run: `python3 -m unittest work/omp-secret-probe/test_omp_secret_probe.py` (13 tests).
- `work/citation-check/test/check.test.mjs` — citation extraction and fail-safe folding: planted
  cookbook rows, curly-quote normalization, missing-key review, transport-error review, invalid
  labels, empty claims without a model call, and README/nonce location behavior. Run:
  `node --experimental-strip-types --test work/citation-check/test/check.test.mjs` (7 tests).
- `work/pokeagent-emerald/test_capture_state.py` — offline state-receipt percentile statistics.
  Run: `python3 -m unittest work/pokeagent-emerald/test_capture_state.py` (1 test).
- `work/pokeagent-emerald/test_macro_choice.py` — the keyless Emerald macro Choice builder
  (`macro_choice.py`, jev-jy7t.1.12): the request is a `Choice` pinned to the model over the
  harness's legal inputs, changes when player position changes, carries only the PORYMAP ASCII
  block from `state_text`, and never carries the full state_text or screenshot; the budget reports
  rate (20 requests/s), time, tokens and cost from state sizes without any network call. The worker
  test also parses every written line and requires `kind`, `code_sha256`, and UTC `recorded_at_utc`.
  Typed SKIP on Python < 3.12. Run: `uv run python -m unittest work/pokeagent-emerald/test_macro_choice.py` (4 tests).
- `work/pokeagent-emerald/test_run_baselines.py` — keyless state-blind control policy: the
  pool is derived from all 6,449 committed `live-results.jsonl` button rows, seeded sampling is
  reproducible, and `run_one` uses only pooled buttons.
  Run: `uv run python -m unittest work/pokeagent-emerald/test_run_baselines.py` (3 tests).
- `work/pokeagent-emerald/test_segment2_baselines.py` — keyless Emerald segment-2 setup
  (jev-jy7t.1.13): the segment comes from recorded reversible transitions in
  `states/emerald-boot.jsonl`, seed setup alternates the observed positions by replaying the
  recorded trace, the goal is a position change from the episode start, state-blind sampling is
  seeded and uses the segment-1 pool, the live receipt records `key_status`, and the power loader
  selects state-blind rows. Not yet non-author verified. Typed SKIP on Python < 3.12.
  Run: `uv run python -m unittest work/pokeagent-emerald/test_segment2_baselines.py` (8 tests).
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
- `work/omp-harm-rule/install-harm-rule.sh` — temp-`OMP_HOME` installer arms: missing install RED, install GREEN, check GREEN, idempotent rerun, empty block list, and inline-list refusal. Run: `sh work/omp-harm-rule/install-harm-rule.sh --selftest` (10 arms in a throwaway `OMP_HOME` under the temp dir, exit 0; no real profile is read or written; jev-7xjv). By hand, run against a disposable profile, never a real one — exit codes `1`, `0`, `0`, each taken **unpiped** (`| head` reports head's status and showed a false `0` on the refusal arm). Full arm table, plus the three defects these arms caught, in [`installer-grade-20260919.md`](docs/demos/upstream-repro/installer-grade-20260919.md) and `NEGATIVE_EVIDENCE.md` R35.
- `work/omp-jev-preaction/test/preaction.test.mjs` — deterministic preaction gate: all six policy patterns fire (wipe-root, wipe-star, mkfs, dd-device, forkbomb, chmod-root); the false-positive arm proves ordinary daily commands do NOT fire, including a scoped `node_modules` delete, `chmod +x`, a `dd` to a file rather than a device, and the pattern quoted inside an `echo`; non-bash tools ignored; a missing or non-string command never throws; a throwing host still returns undefined; and every fire names what matched. Run: `node --experimental-strip-types --test work/omp-jev-preaction/test/preaction.test.mjs` (6 tests).
- `work/omp-jev-commit/test/commit.test.mjs` — commit-message-vs-diff scorer: non-commit and message-less commands ignored, the `-F <file>` form (which this repo mandates) is read from the FILE not the command line, a `-F` pointing at a missing file is ignored rather than crashing, an inline `-m "..."` is parsed, unset key -> `commit_error` with no scores, and a throwing host still returns undefined. Run: `node --experimental-strip-types --test work/omp-jev-commit/test/commit.test.mjs` (6 tests). **Three arms are conditional on a staged diff existing in the cwd and therefore pass on a no-op** — the unconditional proof of the scored path is `live-probe.mjs`, which builds a real throwaway repo with a real staged diff.
- `work/omp-jev-rerank/test/rerank.test.mjs` — observe-only search-result scorer: non-search tools and errored results ignored, short lists skipped, a bare-string `result` (the shape I invented) rejected rather than accepted, a scored list reports real hit count vs capped scored count, unset key -> `rerank_error` with no scores, transport throw -> `rerank_error`, and a throwing host still returns undefined. Run: `node --experimental-strip-types --test work/omp-jev-rerank/test/rerank.test.mjs` (7 tests).
- `work/nev-rerank/test/rank.test.mjs` — rerank ordering, offline: negation trap ranks first lexically, asker-ordered passage first by score, failed asker returns input order unclaimed, missing score never zero-filled, single passage makes no model call, expected level matches jev.py on a four-bin distribution, non-number probability refused. Run: `node work/nev-rerank/test/rank.test.mjs` (7 tests).
- `work/nev-rerank/test/live.test.mjs` — liveAsker wiring with injected fake fetch only (no key, no network despite the name): every passage through askJevScore typed guards with unchanged expected-level reduction, transport throw degrades to ok:false never throws. Run: `node work/nev-rerank/test/live.test.mjs` (2 tests).
- `work/rerank-tool-scifact/run.mjs` — jev-k9z.7 driver for the shipped `jev_rerank` path (`rank.ts` `rerank` + `live.ts` `liveAsker`) on BEIR SciFact, selftest only (no key, no network, no corpus): a fake asker on 2 real shortlists maps passage ids back to doc ids in BM25 order as `title\ntext` and writes no text into rows; an `ordered=false` query gets exactly one resume attempt and keeps BM25 order; the shipped `liveAsker` with no key returns `ordered=false reason=unconfigured` with 0 HTTP calls, no throw, and stops dispatch; through a fake transport it counts 20 calls, the usage tokens and the response model per query. Without `work/sdk` installed it fails naming `npm ci --prefix work/sdk` (runner SKIP). Run: `node work/rerank-tool-scifact/run.mjs --selftest` (exit 0, SELFTEST PASS).
- `work/rerank-tool-scifact/score.py` — jev-k9z.7 keyless scorer and the bead's fixed rule, on planted tool rows over the real shortlists and the committed Noul rows: oracle order gives KEEP, constant scores reproduce BM25 order exactly and give SWITCH, 3 unordered queries are scored while 4 make the run NOT-SCORED, the KEEP/SWITCH/MIXED table passes 7 cases, and a ranking outside the shortlist is refused. Run: `python3 work/rerank-tool-scifact/score.py --selftest` (exit 0, SELFTEST PASS). Receipt re-score, prose not a suite: `python3 work/rerank-tool-scifact/score.py --check-receipt docs/demos/upstream-repro/rerank-tool-scifact-20260924.md` (RECEIPT MATCH).
- `work/two-bit/test/two-bit.test.mjs` — two-bit admissibility gate: RED arms refuse with exit 2, GREEN arm admits with exit 0, unknown candidate refused not measured, missing flag is usage exit 1. Run: `node work/two-bit/test/two-bit.test.mjs` (5 tests).
- `work/omp-jev-review/test/review.test.mjs` — advisory diff review scorer with the deterministic applicability gate (bead jev-deep-kit-8q7.11 retired the Jev noul pre-gate: 98.1% agreement on the 686-commit draw, zero calls, cannot flip on wording): ignores non-diff tool calls, unset key records `review_error` not a pass, throwing transport records `review_error`, a real score records `review_scored` with probabilities, a 200 with no probabilities is an error, a throwing host still returns undefined, the scorer asks exactly the two MEASURED questions and no more (the `scope` question was cut as degenerate and mis-ordered; the test pins the call's `Object.keys(questions)` so it cannot silently return), and the gate: an empty diff and a 10k-line vendored diff record `review_not_applicable` with zero Jev calls (jev-k9z.2), vendored sections are cut before scoring so Jev never sees vendored text while our own code in the same diff still scores, `isVendoredPath` takes directory segments and lockfiles but not look-alike file names, a thin diff records `review_not_applicable` with zero Jev calls, a docs-only diff records `non-code-diff` with zero calls, a >100-line code diff still scores, with `isThinDiff` boundaries (hunks, 9-vs-10 lines, headers never count) and `touchesCodeFile` cases (draw-derived .ts/.mjs/.py/.sh only; extensionless pre-commit is not code by extension). A pipe, `&&`, `;` or redirect command is never run or scored and records `review_not_applicable` (`not-a-plain-diff-command`), not `review_error` (9 of the first 17 real fleet rows after the 2026-09-25 rollout were such commands); a plain git that fails to run is still `review_error`. The advisory line: boundary at `BOUNDARY_COMMENT` (0.9) appends exactly one line to that call's git output, keeps the output verbatim and fires once; below it, on another call, or on a failed git call the result is untouched. Run: `node --test work/omp-jev-review/test/review.test.mjs` (21 tests; 8 planted defects each RED).
- `work/jev-client/test/client.test.mjs` — the ONLY sanctioned systemOne caller: asserts the exact wire shape (`model` + `state` + `questions` as an object of `{type:'noul',instructions}`), unset key -> `unconfigured` with the infisical fix in the error, a key with no installed SDK (fresh clone) -> `sdk-missing` with the `npm ci --prefix work/sdk` fix in the error and no call made, HTTP 400 surfaced with the server body, `.probability`/`.distribution` rejected, non-JSON, transport throw, partial answers, and empty questions refused before any network call. Also the MULTICLASS caller `askJevChoice`: `{type:'choice',instructions,criteria}` with `criteria` a MAP (the SDK refuses a list), a degenerate class set refused before any network call, and five plausible-looking 200s — a label never offered, no `choice`, `.distribution` instead of `.probabilities`, a label missing from `probabilities`, non-numeric `confidence` — each refused rather than read, because a scorer that shrugs at a missing field fabricates a finding instead of crashing. Also `readRow`, which handles BOTH omp session row shapes (`customType` as an object with nested `data`, and `customType` as a string with top-level `data`) — a reader that handles one silently reports "no rows" on the other, which is the root cause of R33 and R44. Also usage (jev-bmn): every answer shape (noul, choice, score, bundle with a text state) returns `usage = {input_tokens, output_tokens, billing_units, extra}` when the response carries it, `billing_units` is `null` (never 0) when the wire omits it, and a response with no usage answers without throwing and leaves `usage` absent on all four shapes; three planted mutants each turn tests red (billing_units zero-filled: 7 fail; the missing-usage guard removed: 19 fail; the bundle not passing usage: 2 fail). Run: `node --experimental-strip-types --test work/jev-client/test/client.test.mjs` (26 tests, 41 including subtests).
- `work/jev-billing-units/measure.test.mjs` — the jev-bmn re-score on a fresh clone, NO Jev calls: with the gitignored docs mirror absent, the price check reports `NOT_RUN` with `./scripts/sync-docs.sh` in the output while the committed rows still score (no failures); a mirrored price line that moved is a failure, not NOT_RUN; an intact mirror passes. Two planted mutants (absent read as mismatch, mismatch read as NOT_RUN) each fail exactly their own test. Run: `node --test work/jev-billing-units/measure.test.mjs` (3 tests).
- `work/jev-client/test/uncertain.test.mjs` — uncertainty-ranked selection, deterministic random audit sampling, coarse score buckets, and no-near-threshold negative. Run: `node --test work/jev-client/test/uncertain.test.mjs` (4 tests).
- `work/jev-client/test/measure-kit.test.mjs` — the standard verdict arithmetic, offline with a fake asker: a planted constant (6/7 correct, same verdict everywhere) comes back DEGENERATE, a planted one-item margin with a near-threshold decider comes back WEAK (the 010dd96 correction encoded), a clear separator DISCRIMINATES, and the driver counts drift flips and transport errors. Run: `node --test work/jev-client/test/measure-kit.test.mjs` (4 tests).
- `work/jev-client/test/timeout-leak.test.mjs` — the SDK abort-leak guard, two local hangs x 8 timed-out requests each: a server that never sends headers (the `guardedFetch` deadline must abort) and one that flushes headers then hangs (the original W7.0 T9 shape; the SDK's own timer ends the body wait unless headers arrive after the guard deadline). Every result must be `{ok:false, reason:transport}` with a `timed out` error and latency at least the client's exported `guardDeadlineMs(50)` minus 5 ms clock/timer tolerance (the old fixed 40 ms floor sat above the 25 ms guard deadline and flaked, jev-rw2), and node:test fails the run on any unhandled rejection (pre-fix: `unhandledRejection` from `dist/index.mjs:636 Timeout._onTimeout`). Run: `node --test work/jev-client/test/timeout-leak.test.mjs` (2 tests, 16 timeouts).
- `work/jev-client/test/key-provider.test.mjs` — where a pane's Jev calls get the key (Joshua, 2026-09-25: roll out every Jev feature to every pane; no pane process has `TYPESAFE_API_KEY` in its environment): the key comes from the call, then the environment, then an installed provider; the environment wins and the provider is never asked; a provider that finds nothing, returns an empty string or throws is `unconfigured` and sends nothing; with no provider an unset key stays `unconfigured`; `useInfisicalKey()` never replaces a pinned provider. The Infisical provider runs the exact command the omp profiles' `models.yml` use, caches for 10 minutes then refetches (a rotated key is picked up), shares one lookup across concurrent callers, caches a failure or whitespace output for 60 s only, never writes the key into the environment, and prefers `~/.local/bin/infisical`. The four `.omp/tools` factories install it only when no fake asker is injected; tests that mean "no key anywhere" pin `setKeyProvider(async () => undefined)`. Run: `node --experimental-strip-types --test work/jev-client/test/key-provider.test.mjs` (10 tests; 5 planted defects each RED).
- `work/jev-question-writing/trial-labels.test.mjs` — offline smoke over the question-writing loop's own artefacts, NO Jev calls: the pass4/5/7 label files parse with the candidate key matching, boolean truths (8, 8, 4+4), unique names, and non-empty state fields; plus verdict arithmetic recomputed by `gradeQuestion` on the RECORDED live scores (pass 4 8/8 DISCRIMINATES, pass 5 8/8 DISCRIMINATES, pass 7 4/4 + 4/4 DISCRIMINATES including the 0.49 closest call) and a planted constant-scores arm that stays DEGENERATE. Run: `node --test work/jev-question-writing/trial-labels.test.mjs` (7 tests).
- `work/jev-prevalence-first/prevalence-check.test.mjs` — near-threshold count printed BEFORE the own-constant bar before the verdict (order asserted per arm): unanimous set DEGENERATE at constant 1.0, skewed set DISCRIMINATES 6/6, one-item-margin-with-near WEAK; a choice set that loses to its majority class is WEAK and one that always answers one label is DEGENERATE; labels-only prints the bar and defers; an unlabeled set refuses with no constant and no verdict number; labels joined from a second file by id reach the binary check; CLI exits 0/3/2/64. A planted removal of the unlabeled-refusal branch fails the CLI test. Run: `node --test work/jev-prevalence-first/prevalence-check.test.mjs` (9 tests).
- `work/jev-dcg-override/override.test.mjs` — structural test over the explain-before-override rule: all five conductor refusal cases present with alternatives, pane-3 verified denial strings quoted (rm-rf-general, redirect-truncate, rm-rf-root-home, EXPLICIT-SINGLE-FILE-REMOVE-OK), planted negative refuses an entry without a safe alternative. Run: `node --test work/jev-dcg-override/override.test.mjs` (3 tests).
- `work/jev-exec-data/exec-data.test.mjs` — executed-vs-data distinguisher (R44 trigger), offline, NO Jev calls: data-literals in `-e`/`-c` programs suppress (incl. flags-with-values and nested-program shapes), exec-fed/eval/bare/mixed triggers stand (fail-closed), no-span input stands, coordinates preserved. Run: `node --test work/jev-exec-data/exec-data.test.mjs` (11 tests).
- `work/omp-harm-rule/harm-exec-data.test.mjs` — R44 trigger pinned at the shipped rule: data-literal probe declines (harm_pass), executed literal fires (0.96), bare trigger fires. Run: `node --test work/omp-harm-rule/harm-exec-data.test.mjs` (3 tests).
- `work/jev-persona-eval/adopt.test.mjs` — persona-clone adopt delta mechanics, offline, NO Jev calls: trap-answered rows survive the join and read as TRAP-LEAK, golden-style verdicts get majority-share constant + seeded chance baselines, unanimous set constant 1.0. Run: `node --test work/jev-persona-eval/adopt.test.mjs` (3 tests).
- `work/jev-eval-honesty/*.test.mjs` — the eval-honesty delta, all offline, NO Jev calls: outcome-join parses both row shapes with selector verification (missing-field lands in selectorReport, unparseable counted, empty input zeroHit) and configurable verdict keys (dcg-bridge `{kind,toolCallId}` rows match); co-presence REFUSEs on zero-hit and distinguishes absent-next-to-firing (not-loaded, never 'no traffic') with a regression test for the keyOf shape bug that made PRESENT unreachable; random-judge gives seeded chance-floor and majority-share constant baselines; judge-run (jev-vbh.3) prints near-threshold, own-constant, and random-judge before the rule verdict, calls a near pile WEAK, and refuses a missing truth with no verdict. Run: `node --test work/jev-eval-honesty/outcome-join.test.mjs work/jev-eval-honesty/co-presence.test.mjs work/jev-eval-honesty/random-judge.test.mjs work/jev-eval-honesty/judge-run.test.mjs` (23 tests). The committed run is `node work/jev-eval-honesty/judge-run.mjs --q injection=work/nev-differential/fresh-20260923/jev-injection-662.jsonl:p:label --q toolout-plain=work/jev-toolout-flag/rows-jev-plain-attacks.jsonl:p:label --q toolout-criteria=work/jev-toolout-flag/rows-jev-criteria-attacks.jsonl:p:label` → `work/jev-eval-honesty/judge-run-20260924.txt`. Zero new calls.
- `work/skillranker-eval/test/contract.test.mjs` — offline mirror of skillranker's EVAL CONTRACT: frozen 0/1/2 loss vs pulled `evaluation_policy.v1.json`, `expected_values.v1.json` recomputed, always-abstain 10/12=0.833, coin-flip worse than abstain, planted wrong-pick scores 2 and REDs if weakened, ≥0.90 gate is a hard FAIL at 0.800 and still not promotable at 0.900 on `diagnostic_synthetic`, overflow case flagged as installable≠offered, JSONL export rows are not a product claim, judge shape is one Choice plus `__none__` with no second noul, invented `helpfulNoul` gate refused. Loss numbers come from `oracle-kit/decisionLoss` (reuse, not a second table). Run: `node --test work/skillranker-eval/test/contract.test.mjs` (12 tests).
- `work/jev-real-corpus-eval/test/score.test.mjs` — frozen toolcall corpus scorer: identity lock n=7846 / GOOD=1665 / BAD=6181 / sha256, GOOD/BAD → allow/abstain via `decisionLoss`, Studio always-abstain **0.212210043** (1665/7846) and isError-only **1.495284221** (11732/7846), python3 reprint, planted false-allow scores 2, a 10-row diagnostic_synthetic substitute is REFUSED, missing outcome / one-class refused. Run: `node --test work/jev-real-corpus-eval/test/score.test.mjs` (10 tests).
- `work/omp-jev-failure/test/failure.test.mjs` — planted errored-tool arms for the MULTICLASS classifier: `failure_classified` carries one class plus its full distribution at `schemaVersion: 2` and no longer carries `scores`, the call itself is ONE choice question over the three mutually-exclusive classes (`classes`, never a question map) — the shape that took the committed eleven cases from 9/11 with two structurally impossible answers per run to 11/11 with none, `failure_error` without a class, non-error ignored, and fail-open append/classifier failures. Run: `node --experimental-strip-types --test work/omp-jev-failure/test/failure.test.mjs` (5 tests).
- `work/omp-jev-foreman/test/foreman.test.mjs` — local-trigger progress observer: healthy window no trigger, repeated-command score, classifier error without scores, and fail-open host. Run: `node --test work/omp-jev-foreman/test/*.test.mjs` (4 tests).
- `work/omp-jev-route/test/route.test.mjs` — pre-staged peer route observer tests. Run: `node --experimental-strip-types --test work/omp-jev-route/test/route.test.mjs`.
- `work/omp-jev-route/test/process.test.mjs` — skillranker process slice: `__none__` abstention, empty-roster unavailable, explicit local resolve, fit/exclude/already-loaded, structured JSON envelope, fail-open writer. Run: `node --test work/omp-jev-route/test/process.test.mjs`.
- `work/omp-jev-route/test/gate.test.mjs` — copied 0/1/2 loss table, always-abstain counterexample (their `expected_values.v1.json` cohort), `diagnostic_synthetic` cannot promote. Run: `node --test work/omp-jev-route/test/gate.test.mjs`.
- `work/omp-jev-route/turns-32.test.mjs` — eww turn-set shape, offline, NO Jev calls: 32 distinct turns, boolean truths, named trap subsets at 10/10/6/6, every question key resolving to a boolean truth (guards the mapping bug that silently voided a whole verdict column). Run: `node --test work/omp-jev-route/turns-32.test.mjs` (3 tests).
- `work/omp-jev-route/shadow-32.test.mjs` — shadow tier mapping, offline, NO Jev calls: confident heavy/light route, trap-short shape does not route heavy, near-threshold pairs abstain, kill switch forces abstain on a would-route row. Run: `node --test work/omp-jev-route/shadow-32.test.mjs` (5 tests).
- `probes/fast-jev-probe.mts` — our black-box probe of the compaction library against a fake Jev. Run: `npx tsx probes/fast-jev-probe.mts` → 8 assertions.

- `work/dogfood-logger/test/logger.test.mjs` — append-only decision/outcome logger: joined false-positive scoring, malformed/orphan record handling, concurrent append preservation, and rotation. Run: `node --test work/dogfood-logger/test/logger.test.mjs` (4 tests).
- `work/omp-jev-observer/test/observer.test.mjs` — observe-only OMP tool_call extension: cost-present, missing-cost, error-cost-absent, timeout, ID, and absent-context sentinel paths. Run: `node --test work/omp-jev-observer/test/observer.test.mjs` (8 tests).
- `work/omp-jev-observer/test/screen-log.test.mjs` — screen verdict logger: a record needs a sessionId and a known verdict, a row carries the schema and a hash but never the screened text, the wrapper returns the screen's result unchanged and appends exactly one matching row, and a malformed verdict records `review` with a null probability. Run: `node --test work/omp-jev-observer/test/screen-log.test.mjs` (4 tests).
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
- `work/bicameral-gate/test_redirect_readers.py` — jev-xxy: both sample-B label readers (`label-b.py` reader 2, `real-sample-b.py` reader 1's redirect pattern) must NOT read `>=`, `=>`, `->` or `>` inside a heredoc body as a write outside /tmp — including the three frozen sample-B risky rows 25, 39, 80 that rested on that bug — and MUST still count real overwrites (plain, `~/`, no-space, `cat > f <<EOF`, a redirect after a heredoc opener, a heredoc fed to `bash`). Red on the pre-fix readers (`git show 9519e94:<file>` for both files into a dir, `READERS_DIR=<dir>`: 10 subtests fail), green after. Run: `python3 -m unittest work/bicameral-gate/test_redirect_readers.py` (4 tests).
- `work/jev-claim-check/claim-check.test.mjs` — the `jev_claim_check` omp tool (`.omp/tools/jev-claim-check.ts`), no key, fetch armed to throw: cuts inclusive at 0.8 (supported) and 0.2 (unsupported) with 0.7999/0.2001 unsure, confidence is max(p, 1−p), the verdict follows the probability and not a claim that says "supported", the REAL live asker with the key deleted returns `not_run`/`NOT_RUN` without touching the network, asker failures and a thrower are `not_run`, a malformed answer (string, NaN, null, missing, 1.2, −0.1, Infinity) is `refused` with no probability, and empty input is refused before the asker runs. Five mutants of the tool each turn a test red (`CLAIM_CHECK_TOOL=<mutant>`; receipt `docs/demos/upstream-repro/jev-claim-check-20260924.md`). Plus the numeric scope (bead jev-5cz): any claim containing a number (75/219, 2.6e-13, 96.0%, and the 18 numeric README claims of jev-sp5) refuses with `numeric-out-of-scope` and never reaches the asker. 19 qualitative README sentences still get verdicts. Versions, names and dates are not numbers, and the description names the limit. Removing the refusal line turns the numeric test red; the file was restored byte-identical. Run: `node --test work/jev-claim-check/claim-check.test.mjs` (10 tests).
- `work/jev-claim-check/numeric-v2.test.mjs` — the numeric claim check's tokenizer and evidence narrowing (bead jev-h8s), no key: a 12-row table where each fragment must parse to exactly its tokens (`2.6e-13`, `0.0614`, `75/219`, `1,145`, `96.0%`, `1.1-4.7%` whole; `60,97,143,250` split; `1.13.0`, `SST-5`, `top-1` skipped) with offsets pointing at the text; a planted-red arm (the jev-2mp tokenizer must fail the scientific-notation and list rows); narrowed evidence identical for a planted value and its original, including a plant that collides with another number in its clause (a text-based anchor filter fails it); the matching row kept and the header dropped; no evidence for a clause that matches nothing. Run: `node --test work/jev-claim-check/numeric-v2.test.mjs` (7 tests).
- `work/jev-claim-check/cli-guard.test.mjs` — the entry-point guard of `check-close.mjs`, `numeric.mjs` and `numeric-v2.mjs` (bead jev-tzv), no key. Each is run with no arguments through its real path and through a symlink to its directory; each run must print usage and exit 64, never a silent 0. The regression came from 8210e02: with the old `import.meta.url === file://argv[1]` guard, a symlinked absolute path (macOS `/tmp`) skipped main() and exited 0 with nothing checked. It was fixed with a realpath compare in 3738322. Planted red on 2026-09-24 via `CLI_GUARD_DIR=<copy>`: the 3738322^ scripts fail 4/4, and a HEAD copy with only numeric-v2's guard reverted fails 2/2. Run: `node --test work/jev-claim-check/cli-guard.test.mjs` (6 tests).
- `work/jev-claim-check/numeric-choice.test.mjs` — the Choice-based numeric check (bead jev-25r), no key. The comparison contract: exact, thousands commas and a claim that rounds its evidence match (`0.068` vs `0.0684`); a changed digit, evidence that rounds the claim (`0.6846` vs `0.68`), a `%` mismatch and a role value (`240` vs `940`) never match. The option list holds each evidence number once, in order, with dates blanked, plus `not_stated`. The masked question is identical for an original and its plant. The +7 digit rule never collides with the jev-2mp or jev-h8s plant rules. Run: `node --test work/jev-claim-check/numeric-choice.test.mjs` (5 tests).
- `work/openrouter/test_provider.py` — the OpenRouter incumbent provider (bead jev-14qk), no key, no network: a `:free` model builds the adapter's own `AsyncOpenAIProvider` against `https://openrouter.ai/api/v1` with `api="chat_completions"`, the given key and SDK retries off (the adapter's RetryPolicy owns retries); a non-`:free` id is refused before any client exists; an unset `OPENROUTER_API_KEY` is refused rather than sent empty; all six listed models are `:free`. Planted red 2026-09-24: `api="responses"` fails the first test, removing the `:free` guard fails the second. Run: `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python -m unittest work/openrouter/test_provider.py` (4 tests).
- `.omp/hooks/post/jev-gate-observe.test.mjs` — the observe-only gate hook, no key: frozen row keys, the flag false below and at exactly the cut, a secret-bearing command skipped with the asker never run, and a key straddling the 200-char prefix scrubbed rather than logged as a stub; plus the full-command sidecar (bead jev-izhc): secret-shaped and filter-error commands write no sidecar row, the sidecar text equals the command Jev scored and joins the prefix row by `cmdSha` while the prefix row keeps its shape, a failing sidecar write still logs the scored row, and the default writer creates mode 600 and narrows a pre-existing 644 file. Every test routes both writers to memory, so the suite never appends to the real sidecar. Planted red 2026-09-24: writing the sidecar before the filter fails 3 tests, writing the redacted prefix fails 1, dropping the chmod fails 1. plus the billing hold (bead jev-nhv9): after an HTTP 402 the next call inside 15 minutes makes no ask and writes `NOT_RUN reason=billing-hold`; at the window one ask is made and a 200 does not start a new hold; a 429, a 503, and a transport error that mentions 4020 set no hold. Planted red 2026-09-24 by a non-author of 7a0a4e7: ignoring the hold fails the 402 test (calls 2 !== 1); holding on any http error fails the 429 case (second row not-run). Run: `node --experimental-strip-types --test .omp/hooks/post/jev-gate-observe.test.mjs` (19 tests). Unregistered until 2026-09-24: stage 70's pattern skipped `.test.mjs` outside a `test/` dir.
- `.omp/hooks/post/session-stop.test.mjs` — the worker stop hook's `decideStop`: missing demos are one continuation, ready work continues with the mission, a stand-down continues even when the file list is complete, and `stop_hook_active` never continues. Run: `node --experimental-strip-types --test .omp/hooks/post/session-stop.test.mjs` (11 tests). Unregistered until 2026-09-24, same stage-70 hole.
- `work/jev-triage/advisory-veto.test.mjs` — the advisory veto, no key: the threshold is the leave-one-out-stable 0.25, not 0.5; a numeric refuse is a skip and never a veto; a low noul on a numeric SHIP is `would_veto` but still not a block; a confident-wrong high noul is `would_not_veto`. Run: `node --test work/jev-triage/advisory-veto.test.mjs` (6 tests). Unregistered until 2026-09-24, same stage-70 hole.
- `work/jev-triage/baseline.test.mjs` — the triage baseline over `work/jev-triage/cases.json`: SHIP needs hits, rate, labels and no concentration; FP exactly 0.30 still ships (inclusive); 14 hits is TOO_RARE even at a passing rate; a rate above 5 is NUISANCE. Run: `node --test work/jev-triage/baseline.test.mjs` (14 tests). Unregistered until 2026-09-24, same stage-70 hole.
- `work/nev-injection/seat-guard.test.mjs` — the seat-faithful injection screen, no key, no network: the seat cut is 0.5 inclusive (0.499 passes), a planted hostile flags, a planted benign passes, trigger words with a low score still pass (the verdict follows the score, not the words), and a malformed answer, an unconfigured asker or a thrower is `review`. Run: `node --test work/nev-injection/seat-guard.test.mjs` (9 tests). Unregistered until 2026-09-24, same stage-70 hole.
- `work/openrouter-incumbents/test_run.py` — the OpenRouter comparator runner (bead jev-3e2i), no key, no model call: each of the five pinned samples it reads with `git show` equals the unit's committed sample (SST-5 500, Banking77 400, CLINC150 750, SciFact 400, FEVER 400); FEVER's question is SciFact's object; STS-B's question comes from its runner at `8e4bda9` (instruction literal present in that source, six criteria); every paid id (`openai/gpt-5`, `openai/gpt-5-nano`, `deepseek/deepseek-v4-flash`) refuses with `PaidComparisonStopped` through `provider_for` and `main` with no client built (jev-lbgk), and an unset `OPENROUTER_API_KEY` is refused; a `:free` id builds the adapter's own provider on `https://openrouter.ai/api/v1` with `api="chat_completions"`. Amendment 2 (free arm): `score.comparators()` returns run 2's qualifiers in order (dots, nex-n2.5-mini, lfm-2.5) and no paid id (Amendment 3); a daily-cap 429 is a quota error and a provider 429 is not; and `run_free()` with a faked adapter client waits out provider 429s, fails the row on the 4th, records one quota row and stops, writes no row for a request the cap refused, and stops after 5 failures of one class with a single resume pass. Planted: always waiting on a quota 429, or writing the cap-refused row, fails its test. Run: `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python -m unittest work/openrouter-incumbents/test_run.py` (13 tests).
- `work/sr-adopt/test_phase_gate.py` — the attempt-before-phase comparison is ours (jev-3w8). skillranker's PhaseGate (adapter.rs:124, :569) gave the name and stores a phase; it does not compare. `composed_phase_gate` has no caller outside this test. A ready attempt returns; an attempt before its phase raises AttemptPanic. Planted negative: a function that returns ready instead fails `test_early_attempt_panics`. The consumed mechanism is `require_bar`, tested in `test_prereg.py`. Run: `python3 -m unittest work/sr-adopt/test_phase_gate.py` (2 tests).
- `work/sr-adopt/test_prereg.py` — preregistration consumer (jev-3w8): a dirty or untracked bar constructs no provider, including through `work/grok-incumbent-3/run.py`. The runner loader is stubbed, so deleting that gate fails on `provider constructed` under plain python3, not on a missing `typesafe_sdk`. The seven hand-checked pairs pass `audit_bars.py`; a reversed pair under `/tmp` exits 1. Run: `python3 -m unittest work/sr-adopt/test_prereg.py` (6 tests).
- `work/sr-adopt/test_matrix_status.py` — matrix status validator (jev-7ge): planned/executed/passed/failed pass; status `done` exits 1; a header-only ledger exits 1; a missing file exits 2 with no traceback; the status column is found by header, not position; the trace `class` column is the ledger. Run: `python3 -m unittest work/sr-adopt/test_matrix_status.py` (6 tests).
- `work/sr-adopt/test_runner_gates.py` — bar gate on the runners that next spend a key (jev-8ec2): rerank-scifact, clinc150 run-variance, banking77 run_jev, and nev-differential run-jev. A dirty bar raises AttemptPanic with zero constructions. A clean bar and no key still exits 2. Deleting each gate in a /tmp copy constructs a stubbed provider and fails the AttemptPanic test. The banking77 Haiku arms left this file with jev-sybt: they now refuse before the bar is read. Run: `python3 -m unittest work/sr-adopt/test_runner_gates.py` (3 tests).
- `work/anthropic-stop/test_anthropic_stop.py` — no paid comparisons (jev-sybt, jev-lbgk; AGENTS.md 'No paid comparisons', 1cc7876): a comparator is a `:free` OpenRouter model or nothing. Census: every tracked code file naming a paid comparator is one of 24 guarded runners or one of 17 named keyless files (none of which builds a client or names a model endpoint), and a new one fails until classified. Naming means a Claude model id in any shape (`claude-3-5-sonnet-…`, `claude-2.1`, `claude-instant-…`, `claude-haiku-4-5`, `anthropic/claude-…`) or an Anthropic client (the adapter's `AnthropicProvider`, the SDK, the endpoint, the provider name `"anthropic"`); a grok id (`grok-4`, `grok-4.20-…`), `XAI_API_KEY`, `api.x.ai` or an `xai/`/`x-ai/` label; an OpenRouter client (`openrouter.ai`, `OPENROUTER_API_KEY`, `openrouter_provider`) or a quoted OpenRouter id without `:free`. A pattern arm pins those shapes and six non-matches (`grokbot`, `grok's`, a `:free` id, a repo path). Static: each guarded entry imports and calls `refuse_paid_comparator` or `require_free_comparator` before any paid reference. Behaviour: each of the 27 guarded entries, with keys set, every provider stubbed and sockets refused (connect and DNS), raises `PaidComparisonStopped` (a SystemExit, so a per-row `except Exception` cannot swallow it) and constructs nothing, as do three CLI mains (openrouter-incumbents with `openai/gpt-5-nano`, second-incumbent, rerank-scifact `grok`); with the call deleted from the same source it no longer refuses, except the three layered OpenRouter entries whose provider refuses a paid id again (the static arm covers their deletion). `require_free_comparator` passes a `:free` id and refuses `openai/gpt-5-nano`, `deepseek/deepseek-v4-flash`, `x-ai/grok-4`, `anthropic/claude-haiku-4.5` and a `:free-trial` suffix. The Jev arms of noul-scifact, score-quixbugs, score-sst5, score-yelp, noul-toxicity and score-stsb still return 2 with no key, and a `:free` id still builds its provider through `work/openrouter/provider.py` and openrouter-incumbents `provider_for`. Planted 2026-09-24 in a /tmp clone: deleting the refusal from `work/second-incumbent/run.py` `run()` fails the static, behaviour and CLI arms (3 failures); a new tracked runner building a `deepseek/deepseek-v4-flash` client on OpenRouter with no refusal fails the census. No network, no key. Run: `python3 -m unittest work/anthropic-stop/test_anthropic_stop.py` (9 tests).
- `work/poke-jev/test_replay.py` — PokéJev Stage A labeller, options and floors (jev-jy7t.1.3), stdlib only, no key: a switch before any move is a choice and a switch after one is forced; `|cant|`, `|drag|`, a `[from]` or locked move, Struggle and fainting first make the turn unobservable; tera declared earlier in the turn is carried; snapshots track actives, faints, tera and moves revealed before the turn; the usage-frequency floor is a distribution weighted by usage with +1 smoothing and puts all mass on the only kind of action available. The file puts its own directory on `sys.path`, so it runs from the repo root. Run: `python3 -m unittest work/poke-jev/test_replay.py` (19 tests).
- `work/poke-jev/test_player.py` — PokéJev player option construction regression: the Showdown placeholder `nothing` is filtered before both normal and Terastallize orders; venv-only because the PokéChamp clone requires Python 3.12, with a typed prerequisite skip under system Python. Run: `cd work/poke-jev && python3 -m unittest test_player` (1 test).
- `work/poke-jev/test_policy.py` — PokéJev Stage B search policy and answer validator (jev-jy7t.1.3), stdlib only, no key: a Jev distribution with a missing or extra label, a non-finite or out-of-range value, or a sum off by 0.02 is refused (no action from it); the opponent pick covers 0.8 of the mass with at most 4 actions and turns an all-zero map uniform; the player pick is the prior's top 3 plus PokéChamp's damage-calculator move; expectimax weights each branch by the opponent model, lets a likely punish flip the prior's preference, and breaks ties on the prior. The file puts its own directory on `sys.path`, so it runs from the repo root. Run: `python3 -m unittest work/poke-jev/test_policy.py` (12 tests).
- `work/poke-jev/stage_b.py` — PokéJev Stage B harness selftest (jev-jy7t.1.3), keyless: uniform fake Jev completes without fallback, hostile labels are refused, a 6-second fake response falls back within the clock, and the planted 20-second slow player loses with `lost due to inactivity`. Run: `env -u TYPESAFE_API_KEY work/poke-jev/.venv/bin/python work/poke-jev/stage_b.py selftest` (4 arms; no network).
- `work/jev-if/test_puct.py` — offline PUCT/JeV adapter tests (jev-jy7t.1.5): deterministic PUCT math, uniform-prior and single-code-path parity, hostile-answer validation and missing-key refusal; stdlib `unittest`, no key or network. Run: `python3 work/jev-if/test_puct.py` (32 tests).
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
| `foundation/run_calibration.py` | `cd foundation && python3 run_calibration.py` (**LIVE**: needs `TYPESAFE_API_KEY` and makes one Jev call per fixture row through the SDK's `system_one`, so no keyless CI step runs it; stage 20 checks that a committed receipt covers the fixture sha, jev-56o4) | our thresholds against the labelled held-out set; emits a receipt under `foundation/runs/` | ECE 0.061, Brier 0.020, Noul 58/60, Choice 19/20 (receipt `20260917T224444Z.json`) |
| `foundation/gates.sh` | `cd foundation && ./gates.sh` | **every** wired stage against the real tree — the suite globs `gates.d/[0-9]*-*.sh`, so the stage count is derived, never fixed here | **8/8 PASS** at `a503b9a`; this row said `4/4` and `the four gate stages` for four stages' worth of additions (pane 2, `3e198bb`) |
| `foundation/gates.sh --selftest` | `cd foundation && ./gates.sh --selftest` | **every stage proves it can go RED** on a planted bad input; the aggregator also proves a RED row names a failing sub-check that is past the first 300 bytes and outside the last 12 lines (`--red-row-selftest`) | **8/8 PASS** at `a503b9a`; same stale-count correction; red-row arm added jev-80lj |
| `githooks/commit-msg-verification-level.sh` | Run: `bash githooks/commit-msg-verification-level.sh --selftest` | the commit-edge hook refuses a level-less subject and accepts a level-carrying one; hermetic temp repos, never the real index | 4 known-bad refused, 4 known-good passed, 1 prose-not-claim refused, 3 receipt/suggestion arms |
| `githooks/pre-push-ci-red-warning.sh` | Run: `bash githooks/pre-push-ci-red-warning.sh --selftest` | the push-edge hook warns and never blocks: five real `git push`es from a throwaway repo into local bare remotes, with a stand-in `gh` serving `work/ci-main-status/fixtures` (no network). Red CI: the push lands and stderr names `work/sr-adopt/test_runner_gates.py`, then the fix-or-say-why line. Green: silent, and the stand-in was called. gh absent: one `CI status NOT_RUN` line. A push to another ref: script not run. A gh that hangs: `NOT_RUN: timed out` within the bound plus 5 s | 5/5 arms; in a /tmp clone, a planted `exit 1` on the red path and a planted `exit 0` before its print each fail arm 1 (jev-rt33) |
| `compaction/` (sibling-owned) | see that directory's own scripts | the omp transcript adapter and its known-bad (a trailing `toolResult` must be kept) | gate `40-omp-compact-replay.sh` PASS |
| `work/skillranker-eval/test/contract.test.mjs` | `node --test work/skillranker-eval/test/contract.test.mjs` | skillranker EVAL CONTRACT process: frozen loss via oracle-kit `decisionLoss`, always-abstain 0.833, coin-flip worse, planted wrong-pick RED at loss 2, ≥0.90 hard FAIL, JSONL export, judge shape, invented noul gate refused | 12/12, this PR |
| `work/jev-real-corpus-eval/test/score.test.mjs` | `node --test work/jev-real-corpus-eval/test/score.test.mjs` | frozen toolcall corpus (n=7846): Studio 0.212210043 / 1.495284221 reprinted, isError-only loses, planted RED | 10/10, this PR |
| `work/omp-guard-rule/guard-rule.test.mjs` | `node --test work/omp-guard-rule/guard-rule.test.mjs` | the omp `tool_call` guard classifies the live class (`grep-as-proof`) and stays observe-only: every path returns `undefined`, `guard_error` exists so a throw is never scored as a pass, and `pipe-exit` is absent — dropped under R51 for a 55.2% fire rate | 5/5, this PR |
| `scripts/selftest-lane-status-pipe.sh` | as written | the lane's honesty signal survives a pipe: good-path in-band line matches the real rc, and a PLANTED missing receipt yields rc=3 both unpiped and through `| tail` — the exact shape that read this gate 223 times in the dcg harvest | 3/3, mutation-proven (delete the in-band printf and 2 of 3 arms go RED) |
| `scripts/selftest-ttsr-rules.sh` | Run: `env -i HOME="$HOME" PATH="$PATH" JEV_GATES_PORTABLE=1 bash scripts/selftest-ttsr-rules.sh` (every key unset: `omp ttsr test` makes no model call; without omp it is the typed SKIP, exit 8, which the runner reports as SKIP naming omp) | every project TTSR rule fires on its known-bad and stays QUIET on a near-miss differing by one element of the defect (no glob / stderr visible / no pipe); plus an arm that fails if a rule file exists with no test. omp absent is RED (exit 1), not a pass; under `gates.sh --portable` it is `SKIP (missing prerequisite: omp, ...)`, exit 8. The system-wide arms (retired ft-* pack, inline-flag, unsafe-router, and the project-vs-`~/.agents` drift guard) need `~/.agents/rules`: with no such root they print `n/a` and a `SCOPE:` line, never ok; a root that exists but lost a rule is RED (jev-hjzz) | 106 ok here with `~/.agents/rules`; 67 ok, 0 failed, 4 n/a in a fresh HOME; both absent directions proven jev-80lj |
| `scripts/selftest-ttsr-assert-disabled.sh` | Run: `env -i HOME="$HOME" PATH="$PATH" JEV_GATES_PORTABLE=1 bash scripts/selftest-ttsr-assert-disabled.sh` (same key-free, typed-SKIP form) | a claimed TTSR disable is proven by enumeration in both scopes, never by probe silence: RED arm a live rule exits 1 and names project/global; GREEN arm `absence-from-one-probe` is absent both; a rule planted in a throwaway HOME's `~/.agents/rules` must be named in GLOBAL scope, so the global leg is proven on a machine with no user rules (jev-hjzz); no-args exits 2. omp absent is RED (exit 1); under `--portable` it is a named SKIP, exit 8 | 5/5 here and in a fresh HOME; both absent directions proven jev-80lj |
| `.omp/extensions/kit-guard/kit-guard.test.ts` | Run: `bun test ./.omp/extensions/kit-guard/kit-guard.test.ts` | revised single-suite guard coverage: shell lexer and nested shell bodies; quoted/abbreviated/env/config hook bypasses; B5 fail-closed regardless of `KIT_GATE_EDIT`; protected `cfg://` settings and gate paths; heredoc/substitution boundaries; required-pattern/config failure arms; root-policy selection from subdirectories; `session_start` root-policy loading; `agent_end` AGENTS re-read and missing-pattern refusal; `session_compact` current-config re-anchor; healthy and known-bad extension decisions | 137/137, gate-edit-7 revised mutation set |

| `work/miniwob-jev/v3_options_test.py` | Run: `if [ -x /tmp/jev-miniwob-jev/venv/bin/python ]; then /tmp/jev-miniwob-jev/venv/bin/python work/miniwob-jev/v3_options_test.py; else echo "SKIP (missing prerequisite: gymnasium)"; fi` | isolated `MINIWOB_V3_ARM` option construction: every arm keeps a text-input `type [` action; quoted/page/color/date/drag/none surfaces are isolated; default v1 options/state match `dd04baf`; row writer adds code hash and UTC start/finish provenance through a fake Jev; `--sanity-reference`/`--sanity-after` fake click-only stop-row gate, restart refusal, 150+60 prior-row resume seeding, run_plan-level prior-row seeding, and comma-separated combined arm list enables only named arms; the same test was RED on `c7651c4` because `type_spans[r]` was dropped | 10/10 current HEAD; RED reproduced on c7651c4 |

| `scripts/row-provenance-check.py` + `work/row-provenance-check/test_row_provenance_check.py` | Run: `python3 -m unittest work.row-provenance-check.test_row_provenance_check && python3 scripts/row-provenance-check.py` | experiment rows, Jev answer rows (any row with `probabilities`) and decision/action logs must carry `code_sha256` or `run_py_sha256` plus an ISO-8601 UTC timestamp; a file whose first line is not JSON fails (the db038a0 backslash-n shape); SHA-pinned exemptions cover legacy files and drift fails; pre-cutoff/non-experiment JSONL skips; first bad file/row is named | 16/16 offline; live 12 row files / 4360 rows / 2 decision logs / 6 exempted files; parse-error and answer-row plants RED |
| `scripts/arm-sanity.py` + `work/arm-sanity/test_arm_sanity.py` | Run: `python3 -m unittest work/arm-sanity/test_arm_sanity.py` | keyless action-type mix gate over committed PokéJev and MiniWoB fixtures: r3 code vs stage-b mix-v1 rejects, mix-v1 vs control passes, c7651c4-window vs pre-window rejects with `type=type arm=0.000`, difference-only shift rejects without concentration, too few eligible rows is `NOT_RUN`, and dropping the offered-type filter is a planted RED | 6/6 offline; mutation RED |
| `scripts/key-status.py` + `work/key-status/test_key_status.py` | Run: `python3 -m unittest work/key-status/test_key_status.py` | fake keys only: a fake whose 16-hex sha256 prefix is on a test revoked list exits 3 without printing the key; any other fake is `OK` (0); an unset key is `NOT_RUN` (2); the MiniWoB live asker, the OSWorld Best-of-N live runner and the gate-question live pass each refuse a revoked fake key before any request (jev-30q7) | 6/6 offline |
| `work/miniwob-jev/run-after-rotation.sh` + `work/miniwob-jev/run_after_rotation_test.py` | Run: `python3 -m unittest work/miniwob-jev/run_after_rotation_test.py` | rotation-ready MiniWoB v3 sheet: key-status gates every isolated arm and combined heldout step; fake mode runs two episodes per selected step, validates row provenance, revoked fake stops at step 1, combined mode reads the committed passed-arm list (`quoted`, `none`), and stale heldout output refuses unless `--resume` | 5/5 offline; revoked/stale/arm-list plants RED |
| `work/jev-usage-router/trial-choice.mjs` + `work/jev-usage-router/trial-choice.test.mjs` | Run: `node --experimental-strip-types --test work/jev-usage-router/trial-choice.test.mjs` | usage-router trial on real goals (jev-vbh.4), fake answers only: the seeded sample keeps every non-local goal and an equal local draw; the trial sends the router's exact request on `jev-1.13.0`; an off-label answer from the real client counts incoherent, not transport, and is never scored; three consecutive 402s stop the run; drift, majority action and the short-goal cell count abstentions as safe; rows carry `code_sha256` + UTC; no key prints `NOT_RUN` and exits 2 | 10/10 offline; 5 planted defects each RED |
| `scripts/jev-state-size.py` + `work/jev-state-size/test_state_size.py` | Run: `python3 -m unittest work/jev-state-size/test_state_size.py` | will each request fit jev-1.13's documented 32k input limit (RULE 15 feasibility): on the real OSWorld table (`calibration-osworld-r3.tsv`, 337 requests, 12 refused `max_tokens_exceeded`) no refused request is `FITS`, every `FITS` request was answered and no answered request is `OVER`; the old bytes/4 estimate lets refusals through; question bytes count; `--field`, compact UTF-8 bytes, exit 0/1/2 and `NOT_RUN` without a usable calibration table | 11/11 offline; 5 planted defects each RED |

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
- `demos/test/live-refusal.test.mjs` — every demo whose source parses `--live` (17 today, discovered, not listed), run with no key: `--live` must exit 2 and say `NOT_RUN` or name the missing key, and the recorded lane of the same demo must exit 0 (jev-6smc). Planted `process.exit(0)` back into rag's refusal turns exactly the rag case red; on the pre-fix demos it is red on chief, compact, consistency, consistency-noul and rag. compact is skipped until `./scripts/bootstrap-compaction.sh` has built its upstream. No network. 18 tests. Run: `node --test demos/test/live-refusal.test.mjs`.
- `demos/test/live-state.test.mjs` — runs the consistency and consistency-noul `--live` lanes offline: a preloaded `fetch` stands in for the TypeSafe endpoint, records each request's `state` and `questions`, and answers with a valid shape (a placeholder key, no network). Each of the 3 repeats must send the cookbook's state shape, `{uid, post}` / `{uid, claim}`, carrying the cookbook post (text, link domain, report reasons, strikes) or claim (description, line items summing to the amount, rental coverage, exclusions, auto-triage note) (jev-s0f1), and the cookbook's questions: the 8 Choice instructions with every label's description, and the 14 Noul instructions, each set pinned by the sha256 of its canonical JSON as derived from the cookbook (jev-t6yt). Plants: the pre-fix demos fail the state tests; restoring the generic "Pick the single most applicable label" builder fails only the Choice-questions test; rewording one Noul instruction fails only the Noul-questions test; spreading the post into the state fails only the post-state test. Prerequisite: the TypeSafe SDK in `work/sdk` (`npm ci --prefix work/sdk` once); without it the client refuses as `sdk-missing` before any request and every test fails naming that command. 4 tests. Run: `node --test demos/test/live-state.test.mjs`.
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

## `work/toolcall-judge-v3/rules-v4.test.mjs` — 14 tests

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

## `work/jev-retransmit-killer/adopt-gate.test.mjs` — 5 tests

Run: `node --test work/jev-retransmit-killer/adopt-gate.test.mjs` (no API key; temp trees only).

A gate nobody has seen fail is a decoration, so four of the five tests are PLANTED BAD TREES: the
gate is pointed at a temp repo where exactly one thing is wrong and the exit code is asserted.

1. a clean tree passes with exit 0
2. PLANTED: moving the preregistered bar is caught, not silently honoured
3. PLANTED: a receipt gutted of its finding is caught, not just its presence
4. PLANTED: a missing receipt is caught
5. PLANTED: an installed production compaction hook is caught and exits 1, not 2

Test 2 is the load-bearing one. Lowering `SAVE_BAR`/`LOSS_BAR` in `fair-oracle.mjs` is the
cheapest possible way to turn REJECT into ADOPT, and it would leave every other check green.
Test 5 pins the exit codes apart on purpose: 1 means there is a real install to remove, 2 means
the evidence the doctrine rests on has rotted, and collapsing them would hide the second.

## `work/jev-score-register/register.test.mjs` — 15 tests

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
11. recordingChoice records every label, not just the argmax
12. recordingChoice does not misfile a successful choice as a failure
13. recordingChoice stores no raw state and no label text

Tests 11–13 cover `recordingChoice`, added because four extensions (failure, firstlook, fork,
heat) call `askJevChoice`, whose result carries `probabilities` and no `scores`. Test 12 is the
planted negative for that: it asserts that the ORIGINAL `recording()` misfiles a successful
choice result as `ok:false`, which is the silent misattribution that would have written four
extensions' good calls into the register as errors. Test 13 repeats test 3's discipline for the
choice path — neither the value nor the FIELD NAME of a placeholder secret may appear.

Test 1 encodes the measured jevcache defect directly: `{"command_id":"rm -rf --no-preserve-root /"}`
and `{"command_id":"echo hello"}` shared a fingerprint there and it served the benign answer for
the destructive command. Here they must differ.

## `work/jev-eval-honesty/outcome-join.test.mjs` — 6 tests

Run: `node --test work/jev-eval-honesty/outcome-join.test.mjs` (no API key; pure local join).

Guards the outcome-join mechanism — one of the three absent from the `evaluation-framework` skill
we adopt for everything else. The zero-hit guard is the load-bearing one: a join that silently
matches nothing is the defect this package exists to prevent.

1. mixed Shape-A/Shape-B rows both match
2. row missing an expected field lands in selectorReport, never dropped
3. unparseable line is skipped and counted
4. non-decision and keyless decision rows land in unmatched
5. empty input returns zeroHit:true
6. readRow accepts already-parsed objects (Shape A object form)

Registered by the conductor when the files were found STAGED-BUT-UNCOMMITTED during a peer
branch switch; the author's own registry entry supersedes this one if it differs.

## `work/omp-jev-observer/test/emits-rows.test.mjs` — 5 tests

Run: `node --test work/omp-jev-observer/test/emits-rows.test.mjs` (no API key; host is stubbed).

The tests §16 proved were missing. `safeAppend` was called at four sites and defined at none, so
the first `tool_call` threw ReferenceError into the outer catch and the observer emitted NOTHING,
deterministically, for as long as the package existed. Every pre-existing test passed the whole
time, because they asserted the handler does not throw — and a handler that swallows everything
does not throw. These assert the opposite: that rows ARE produced.

1. PLANTED NEGATIVE for the safeAppend defect: a tool_call produces at least one row
2. a decision row is emitted, not only diagnostics
3. the decision row carries the toolCallId it observed
4. a failure still emits a decision row carrying the error, never silence
5. an unwritable host does not throw into it — the swallow is deliberate, and now tested

Test 1 fails against the pre-fix tree (0 rows). Test 4's assertion was corrected during authoring:
it originally expected an injected `classify` error, but the API-key check runs BEFORE classify, so
on an unconfigured machine the recorded error is the key error. The contract under test is the
same one §16 found broken — a failure must be RECORDED, not swallowed.

### `work/toolcall-judge-v3/rules-v4.test.mjs` — four arms added 2026-09-20 (R44 trigger)

11. R44 TRIGGER: a sed program survives the strip — it is code, not payload
12. R44 TRIGGER: macOS `sed -i ""` form also survives
13. R44 PLANTED NEGATIVE: a quoted PROMPT is still stripped — -p is not a code flag
14. R44 PLANTED NEGATIVE: python3 -c is code, python3 script.py --note is not

Arms 13 and 14 are the load-bearing pair: they pin the distinction the whole rule rests on. A
quoted span is code when it occupies the slot after an interpreter code-flag (-c/-e/-i/
--expression), NOT when its binary happens to be an interpreter. `-p` is deliberately excluded
and arm 13 proves why: `perl -p` is code but `omp -p "..."` is a prompt, and including `-p`
broke the quoted-prompt arm.

## `work/omp-jev-review/behaviour-label.test.mjs` — 6 tests

Run: `node --test work/omp-jev-review/behaviour-label.test.mjs` (no API key; reads git only).

Guards the COMPUTED behaviour label built for jev-fzw. The incumbent label was a mechanical
proxy — any non-test source edit counts — which called a MISS when the model correctly said a new
standalone script changes no caller behaviour. The label was the bottleneck, not the score.

1. the label is deterministic — same commit, same answer
2. PLANTED NEGATIVE: a docs-only commit is not behaviour-changing
3. PLANTED NEGATIVE: a .md mention is not a caller
4. a registered entry point counts as reachable even with zero importers
5. the row always carries a reason — a bare verdict is not a label
6. mechanical and computed are both reported, so disagreement stays visible

Test 3 pins a defect found in this rule on its first run: it reported "referenced by README.md"
and counted a documentation mention as a caller — mention-vs-use, inside the rule written to fix
a bad label.
- `work/poke-jev/test_watch_mode.py` — credential-free owner filter: exact, spaced, hyphenated, empty, spaces-only, and near-miss usernames; no network or Jev calls. Run: `.venv/bin/python -m unittest work/poke-jev/test_watch_mode.py` (6 tests; typed-skip exit 8 on Python <3.12, matching `work/poke-jev/test_player.py`, 3b8cf17).

### `work/loss-depth/pokejev-components/battle/test_run.py` — 4 tests

Offline fake-Jev tests for the frozen leaf arms: the code arm never calls Jev, the
code+Noul arm makes exactly one asker call per leaf, HTTP 401/402 stops instead of
falling back, and a frozen-weight SHA-256 mismatch refuses to start. Run:
`work/poke-jev/.venv/bin/python -m unittest work/loss-depth/pokejev-components/battle/test_run.py`.
Typed skip (exit 8) on Python <3.12, matching `work/poke-jev/test_player.py`.
| work/miniwob-jev/test_external_rates.py | python3 -m unittest work/miniwob-jev/test_external_rates.py | committed Table 3 extraction carries PDF URL and SHA-256; all four projected values match every published row after n/a normalization; one planted book-flight aggregate mismatch fails | 2/2 keyless; mutation RED |
| work/miniwob-jev/test_text_candidates.py | python3 -m unittest work/miniwob-jev/test_text_candidates.py | page-text candidate builder (jev-9gtw.4.2) on the 7 captured real observations. KNOWN DEFECT at 026d1230, found by pane 1: the builder inserts the grader's answer (`derive_needed_text`) into its own candidates, so the coverage test passes by construction; a fix is in IvoryCreek's working tree, not committed. Registered so the registry is complete, not as evidence | 3/3 keyless; tautological, see jev-9gtw.4.2 |
| scripts/test_bar_reachable.py | uv run python scripts/test_bar_reachable.py | jev-1ww3 bar-reachability gate: jev-jjwt held-out split exits 1 (max discordant wins 2, minimum p 0.5); R112 337-task split exits 0 (observed b=2,c=8; 48-win headroom); planted headroom defect turns tests red; no Jev calls | 3/3 keyless; mutation RED |
