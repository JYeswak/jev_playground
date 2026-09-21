# Axis B: skillranker's gate ladder + CI machinery (evidence)

Source: `~/Developer/skillranker-probe` @ `1d42b2c`
(Dicklesworthstone/skillranker). Read 2026-09-21. All paths below are
relative to that checkout. No `cargo test` run — evidence is structural
(fourth-oracle-adjacent: his tree describing itself, verified by reading,
not by executing). A live `cargo test --locked` is the obvious follow-up.

## 1. What a "gate" is

A gate is ONE `#[test]` fn named `all_pN_invariants_verified` that walks
an entire phase pipeline end-to-end and asserts every invariant,
especially the fail-closed directions:

- `tests/p1_gate.rs:73` — `all_p1_invariants_verified` (1 test in file).
  Transport/runtime readiness: codec, retry, admission, accounting.
  Opens with a canary secret (`p1_gate.rs:27`,
  `CANARY_SECRET = "test-canary-secret-never-leak-12345"`) so redaction
  is exercised on every run, not described.
- `tests/p2_gate.rs` — 2 tests in file (the only multi-test gate):
  `eligible_output_maps_to_currently_authorized_local_records` and
  `unreadable_or_malformed_records_leave_no_eligible_output`
  (both named in `tests/contract_matrix.toml:703` row).
- `tests/p3_gate.rs:76` — `all_p3_invariants_verified` (783 lines).
  Context/privacy foundation. Representative arm, `p3_gate.rs:82-97`:
  conflicting sources must resolve to `Err(ConflictingFlags)`; the
  discovery closure is `|_, _| panic!("must not discover")` — the test
  fails if the code even *attempts* the unsafe path, not just if it
  returns wrong. Temp dirs are real (`p3_gate.rs:51-61`, pid+atomic
  unique, retained — repo policy forbids auto-deletion).
- `tests/p4_gate.rs:187` — `all_p4_invariants_verified` (713 lines).
  Full pipeline: scoring math, directive resolution, JSON/table output,
  offline demo, dry-run, fenced cache. Mocks ONLY at the paid seam
  (`GateMockTransport`, `p4_gate.rs:52-70`, records requests for
  assertion); cache is a REAL SQLite (`open_cache`, `p4_gate.rs:37`).

How it differs from a contract test: contract tests
(`tests/*_contract.rs`, ~100 files) assert one boundary's schema and
invariants in isolation. A gate asserts the phase's boundaries COMPOSED
— source selection INTO redaction INTO rendering INTO receipts — plus
the negative arms (conflict, malformed, unreadable) in the same
function, so a phase cannot pass on happy paths while its refusals rot.
Gates are cumulative phase acceptance, not feature coverage.

Full ladder (matrix `tests/contract_matrix.toml` + AGENTS.md phase
table): P0 bootstrap/contracts, P1 transport/runtime, P2 roster/
privacy/Quill, P3 exact-session context, P4 core CLI/ranking/cache,
P5 ledger/observation/replay, P6 shadow hook/install, P7 advisory
rollout, P8 calibration/rollback, P9 TUI/retrieval. Gate rows found:
`p1_acceptance_gate` (matrix :419, status executed),
`p2_acceptance_gate` (:703, planned),
`p3_acceptance_gate` (:933, planned),
`p4_core_cli_acceptance` (:1185, member_beads = 19 beads — the gate
aggregates nineteen work items). P1 AND P2 gate files exist and both
are in the matrix. Note: AGENTS.md's phase table lists
P0/P2/P4–P9 but OMITS P1 and P3 — the table is capability marketing,
the matrix is the authority.

## 2. What runs in CI, in order, what may fail

There is NO `.github/` directory (verified: `ls -a` root, no
`.github`, no yaml workflows). CI is mechanized as lane procedure +
scripts, in `AGENTS.md:555-559`:

1. `cargo fmt --check`
2. `rch exec -- cargo check --locked --all-targets`
3. `rch exec -- cargo clippy --locked --all-targets -- -D warnings`
4. `rch exec -- cargo test --locked`
5. `ubs --diff`

(`rch` = remote-build fleet; without it the bare cargo commands are
the gates. `--locked` everywhere: lockfile drift fails the build,
it never resolves silently.)

Allowed to fail: `#[ignore]` tests requiring what CI cannot have —
`tests/jev_smoke.rs:240,618,627,842` (live PAID requests, need
explicit consent + exported key), `tests/cass_adapter.rs:389`
(requires installed cass 0.8.0 binary). Convention: ignore reason
names the missing capability; "infrastructure failure is not a test
pass" (AGENTS.md). E2E suites live in `scripts/e2e/` (roster, context,
core-cli, cache, parser-corpus + `runner.py` harness + `suites/*.json`
declarations) and are referenced per-boundary in the matrix
(`e2e_suite`, `e2e_cases`), but execution status there is mostly
`planned` — the matrix is honest about that (see §3).

## 3. Ratchet: yes, two of them, neither a threshold variable

No single "threshold may only move one direction" constant was found
(grep `ratchet`: zero hits in src/tests/docs/scripts). What exists:

(a) **The matrix status vocabulary** (`validate_contract_matrix.py:37`:
`VALID_STATUSES = {"planned", "executed", "passed", "failed"}`) plus
the header rule (matrix :11-13): "Status is a declaration, not an
execution receipt. P0 rows for future product tests are planned, never
fake passed results." Movement planned→executed→passed is
procedural, enforced by `scripts/validate_contract_matrix.py` (declaration
shape) and `scripts/test_contract_matrix.py` (mechanics receipts) —
a status ratchet: you may advance the claim only by producing the
receipt the next rung demands.

(b) **The authority file** (`tests/contract_authority.toml:1-3`):
"independent validator input, never regenerated during validation."
The reviewed policy cannot be rewritten by the thing it validates —
a review ratchet against self-grading.

Nearest non-mechanized: "Freeze dataset, split, metrics, and
acceptance thresholds before tuning" (AGENTS.md) — a freeze
convention, stated not enforced. For our 3.6x-labelling-error wound:
his answer is (a)+(b)+gates that persist receipts — rows ARE the
artifact (`assertion_ids`, `e2e_cases` per boundary).

## 4. rust-toolchain.toml

```toml
[toolchain]
channel = "nightly-2026-08-31"
profile = "minimal"
components = ["clippy", "rustfmt"]
```

Pinned nightly + minimal profile + the two lint components as
installables. `grep #\[feature src` returned NOTHING — the crate uses
zero nightly-only language features, so the pin buys reproducibility
of clippy/rustfmt Diagnostics, not language access. If it drifts:
`cargo fmt --check` and `clippy -D warnings` are the first two gate
rungs, so a toolchain move surfaces as format/lint diffs before any
test runs — drift fails loudly at rung 1–2, never silently in test
semantics. (Our lane: no toolchain file at all; our fmt equivalent
is `ubs --diff`, which is not version-pinned.)

## 5. scripts/ contents: doctors and self-checks, not build steps

No build script exists (cargo owns building). Contents:

- **Self-checks (validate the tree, not the product):**
  `validate_contract_matrix.py` (matrix declaration shape + fixed
  diagnostic codes, "avoid copying file contents into logs"),
  `validate_eval_policy.py` (executable, 30 KB),
  `validate_public_contracts.py` (doc links/anchors, JSON/TOML/shell
  syntax "without execution" — explicitly "never runtime support"),
  `check_dependency_graph.py` + `test_dependency_graph.py`.
- **Executors with their own tests:**
  `test_contract_matrix.py`, `test_eval_policy.py`,
  `test_runner*.py`, `test_product_cases.py` — the scripts that check
  are themselves checked.
- **E2E:** `e2e/run.sh` dispatches `--suite roster|context|core-cli|
  cache|parser-corpus` to suite scripts, else `runner.py`;
  `e2e/suites/*.json` (context, runner-contract, runner-smoke,
  transport) declare suites as data.
- **Doctor:** YES — product surface `sr doctor` + `tests/doctor_
readiness.rs` (real binary checks in isolated homes, cleared env,
`CANARY` synthetic key) + `docs/doctor-readiness.md`. The doctor is
a tested product feature, not a script.

## 6. Highest leverage for us (Rule 12: default ADOPT)

Cost in files/hours is for our lane (shell + docs, no Rust).

1. **Matrix row per boundary with status-as-declaration + validator.**
   One TOML/JSONL row per instrument: id, phase, evidence command,
   e2e cases, assertion ids, status ∈ {planned, executed, passed,
   failed}, with a script that rejects malformed rows and a rule
   that `planned` rows are never cited as results. This is what stops
   "25 verdict rows for 33"-class staleness AND the un-diagnosable
   3.6x labelling error: rows persist, receipts attach.
   Cost: 1 schema file + 1 validator script + N rows
   (~4 hrs, mostly backfill).
2. **Single-fn phase gate with negative arms first.**
   Our selftests already do fire/quiet arms; his increment is ONE
   function per phase that composes the instruments (consumer-check
   INTO exposure INTO gates) and asserts the refusal directions in
   the same run, with `panic!("must not ...")` closures that fail if
   the unsafe path is even attempted. Cost: 1 script per phase,
   ~2 hrs.
3. **`never regenerated during validation` authority input.**
   A second file (our EVAL ledger is the candidate) that the gate
   script reads but cannot write — human-edited expectations the
   automation checks against, so the tool cannot grade its own
   homework. Cost: split one file into expectation vs receipt,
   ~1 hr + discipline.

Refusal test (Rule 12): none refused. The defect class each would
NOT have caught: (1) would not catch wrong-but-well-formed evidence;
(2) would not catch cross-phase drift; (3) would not catch a stale
human expectation. What we lose by adopting: ~7 hrs backfill + the
ongoing tax of updating rows. What we lose by NOT adopting: the next
labelling error is again un-diagnosable — measured today, not
hypothetical.

## Plan (next)

1. Bead per mechanism (3 beads, this repo, prefix jev).
2. Smallest honest v1: ledger-row schema + validator for (1);
   single composed gate script for (2); EVAL-vs-receipt split for (3).
3. Each lands with a RED arm (malformed row rejected; gate fails
   with refusal removed; validator fails when run against its own
   output as input).
