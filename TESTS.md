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
  known-bad (a trailing `toolResult` must be kept). Gated by
  `foundation/gates.d/40-omp-compact-replay.sh`.
- `compaction/test/hook-compact.test.ts` — the omp compaction hook surface (sibling-owned, bead
  `jev-compact-hook-hbs`).
- `probes/fast-jev-probe.mts` — our black-box probe of the compaction library against a fake Jev.
  Run: `npx tsx probes/fast-jev-probe.mts` → 8 assertions.

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
| `foundation/gates.sh` | `cd foundation && ./gates.sh` | the four gate stages against the real tree | 4/4 PASS |
| `foundation/gates.sh --selftest` | `cd foundation && ./gates.sh --selftest` | **every stage proves it can go RED** on a planted bad input | 4/4 PASS |
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
