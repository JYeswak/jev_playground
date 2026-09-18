# GATES.md — the jev lane

Every gate in this lane, what edge it blocks, and the command that proves it can go RED.
A gate that has only ever been observed green is decoration.

**Run everything:**

```bash
cd foundation && ./gates.sh              # all stages against the real tree
cd foundation && ./gates.sh --selftest   # every stage against its PLANTED BAD input
```

`--selftest` is the load-bearing mode: a stage passes there only by **correctly going RED** on a
known-bad specimen. Measured 2026-09-17 — `ALL GREEN` in both modes, so all four stages are
proven to trip.

## Oracle

Every gate below is *our* check. The **oracle** is the thing this lane does not control and must
agree with, and no gate substitutes for it:

| Oracle | What it arbitrates | Where |
|---|---|---|
| TypeSafe's documented response schema | whether a Jev client is correct | `docs-mirror/typesafe/api.md` — validate every field, refuse on drift |
| `system-one-adapter-python` (official) | whether Jev beats a chat model on the *same* questions | `upstream/typesafe-ai/system-one-adapter-python` — same state, same questions, differential |
| `evals.typesafe.ai` | the published eval methodology and per-model results | read before inventing a rival metric |
| `foundation/fixtures/calibration-v1.jsonl` | whether *our* thresholds are right | `foundation/run_calibration.py` → a receipt under `foundation/runs/` |
| `model-jaggedness/jev-1.13.md` | whether a surprising answer is a known model failure mode | `docs-mirror/typesafe/` — read before filing a bug |

**No oracle named ⇒ the claim is `EXPLORED`, not `PROBED`.** A gate with no oracle behind it
grades decoration on an unfalsifiable claim.

---

## Fail-closed rules

1. **An empty scan set is an ERROR.** `10-fixture-integrity.sh` on a missing fixture, `ubs` on a
   doc-only change (`exit 3`), a grep that matched nothing — none of these are green.
2. **A timeout is not a verdict.** Re-run; record `TIMEOUT_UNMEASURED`, never `ABSENT`.
3. **An acknowledgement is not an effect.** `success=true` with empty `data` is `NO_PAYLOAD`
   (`NEGATIVE_EVIDENCE.md` R7).
4. **A missing key fails the live lane, it never silently degrades it.** `30-no-secrets.sh`
   proves the key is not in the tree; the client throws when it is absent from the environment.
5. **Exit code agrees with verdict text**, and a stage that cannot reach RED is removed from
   `gates.sh` rather than counted.

---

---

## Gate wiring

Gate scripts wired into `foundation/gates.sh`, by basename:
`10-fixture-integrity.sh`, `20-receipt-freshness.sh`, `30-no-secrets.sh`,
`40-omp-compact-replay.sh`, `50-house-gates.sh`, `60-staged-deletion-lane.sh`.

`50-house-gates.sh` wraps the **foundry house gates** against this repo — `dag-validate-gate.sh`
(our bead store must be a valid DAG before anything dispatches from it), `close-evidence-gate.sh`
(a bead close must carry its proof, not assert "done"), and `commit-evidence-lint.sh` (a `perf(`
/ `fix(` subject must carry a quantified delta plus a verification token). They are wrapped, never
re-implemented; our RED arm delegates to each script's own `--selftest`.

**`neg-evidence-gate.sh` is deliberately NOT wired**, and that is an argued refusal: it enforces
"a RED tick appended to `NEGATIVE_EVIDENCE.md`" and takes `--verdict` from a tick ledger. This
lane runs no tick loop, so the gate would have no consumer — and a gate whose only consumer is
another agent is refused by `value-bearing-gates`. Wire it the day this lane gets a loop driver,
which is the same day `p12-loop-integrity` stops being N/A.

Plus `commit-msg-verification-level.sh` on the commit edge and `sync-docs.sh --check` on the
citation edge.

| Gate | Edge it blocks | RED arm (the planted bad) | Wired where |
|---|---|---|---|
| `foundation/gates.d/10-fixture-integrity.sh` | a rotten calibration fixture emitting green-looking garbage downstream | a truncated copy of the fixture | `foundation/gates.sh`, and any pass that cites a calibration number |
| `foundation/gates.d/20-receipt-freshness.sh` | citing a receipt that does not cover the **current** fixture bytes (recomputes the sha; requires a complete, non-interrupted run and a full denominator) | a receipt whose fixture sha does not match | `foundation/gates.sh` |
| `foundation/gates.d/30-no-secrets.sh` | a secret **value** entering the workspace tree (names like `TYPESAFE_API_KEY` are expected; values are not) | a planted fake key, asserted to be named in the RED output | `foundation/gates.sh`; the commit edge is now covered by `githooks/pre-commit` below |
| `foundation/gates.d/40-omp-compact-replay.sh` | an omp transcript adapter that drops a trailing `toolResult` (must be kept) | the known-bad transcript | `foundation/gates.sh`; hermetic — no network, no key |
| `foundation/gates.d/50-house-gates.sh` | our bead DAG, our bead closes, and our `perf(`/`fix(` commit subjects — by wrapping three foundry house gates against this repo | delegates to each house script's own `--selftest`, run with git config neutralized | `foundation/gates.sh` |
| `githooks/pre-commit` → `pre-commit-staged-deletion-survives.sh` | a path-limited commit that silently DROPS a staged deletion whose file is still on disk — RULE 1 failing mechanically instead of by intent | `foundation/gates.d/60-staged-deletion-lane.sh`: 1 trigger witness (refuses and names `doomed.txt`) + **5 satisfying witnesses** (plain modification, genuine deletion, path-limited with no deletion, new file, amend) | **live** — `core.hooksPath` is set to this clone's **absolute** `githooks/` (re-derive with `git config core.hooksPath`; it must be absolute, because a relative value resolves per-worktree and every worker lane would then commit unhooked); copied byte-identical from foundry (`934d4cc0d843` / `17f7abceac05`), proof is ours |
| `.git/hooks/commit-msg` → `commit-msg-verification-level.sh` | a commit subject that claims work without naming its **verification level** (`pending` / `selftest` / `test` / `mutation` / `oracle` / `live`) | `--selftest` proves both legs: a level-less subject refused, a level-carrying subject passed | live — it refused this session's first commit attempt |
| `dcg` (machine-wide) | `git add -A` / whole-tree staging in this shared worktree (`zeststream.shared_worktree:git-add-whole-tree`), and the rest of the destructive set | n/a — external guard | live — it denied a blanket stage during the `git init` |
| `scripts/sync-docs.sh --check` | citing a vendored primary source that has drifted from its committed sha256 manifest | delete or edit a mirrored file, re-run: reports `MISSING` / `DRIFT` and exits 1 | run before citing `docs-mirror/**`; `CHECK PASS 114 mirrored files` at this commit |
| `~/.claude/scripts/skill-topology-gate.sh` | skill-store divergence across the 8 agent roots | n/a — external | run after any tool install that "activates skills" |

---

## The rules these gates exist to enforce

1. **An empty scan set is an ERROR, not a pass.** `ubs` on a doc-only change exits 3 with
   *"nothing was checked (this is NOT a pass)"* — that is the correct behavior and it must never be
   cited as green. See `NEGATIVE_EVIDENCE.md` R6.
2. **Exit code agrees with the verdict text.** A stage that prints RED and exits 0 is a fail-open
   surface under a fail-closed consumer.
3. **Silent on the healthy path.** A gate that comments on every valid input gets uninstalled.
4. **Both directions or it is unproven.** Known-bad ⇒ RED *and* known-good ⇒ PASS. An attack-only
   suite ships an over-strict gate that gets routed around.
5. **A gate's own source must not trip it.** `30-no-secrets` did exactly that once during its build
   — it matched the key pattern written in its own script. The fix: assemble the plant at runtime
   and assert the RED output *names the plant file*.

---

## Not wired yet — stated, not hidden

`stamp-check.sh --repo .` at this commit: **51 PASS, 1 FAIL, 1 PARTIAL, 11 N-A (report-only)**.

> **This table was 6/7 false for about an hour and a machine caught it, not a human.** A Jev pass
> over every doc in this repo (`docs/reviews/runs/jev-doc-review-20260918T001523Z.json`) ranked
> `GATES.md` joint-highest in the corpus for internal contradiction (0.43), because the rows below
> still said HUMAN / NOT ADOPTED / CONDITIONAL for six items that had since gone PASS. Hand-verified
> against live `stamp-check`, then corrected. The lesson is the section's own: **a classification is
> a claim, and a claim needs a re-derivation path.** Re-derive this table from
> `stamp-check.sh --repo .` before citing it; do not read it as current.

Closed since the first pass, each by a mechanism rather than a reclassification: `i-staged-deletion-hook`
(the lane is wired and proven by `60-staged-deletion-lane.sh`, 2 triggers + 6 satisfying witnesses),
`p5-autofix` (wired in `--check` mode — the fixer only ever sees staged paths, and staged paths here
can only be first-party), `p6-cross-lineage` (`REVIEW-PERSONAS.md`, five lenses each owning a doc
that exists), `p7-worksheet` + `p8-session-feedback` (`.flywheel/` worksheet and feedback, filled
not scaffolded), `p18-end-of-shift` (green on a clean tree).

Still open, with their classification:

| Item | Verdict | Why |
|---|---|---|
| `p12-loop-integrity` | **FALSE FAIL (routed)** | errors `exit 3` (driver missing) and `stamp-check` calls that FAIL. This lane runs no tick-loop *driver*; the honest verdict is N-A, symmetric with `rc0` yielding N-A when there is neither a `.rust-cli-path` nor a `[[bin]]` crate. Filed on `jev-stampcheck-vendored-false-positives-lfn`. |
| `rc0-declared-path` | **FALSE_POSITIVE (routed)** | the "undeclared Rust bin crate" is `s1-rs`, a vendored clone. It is not our CLI. Same bead. |
