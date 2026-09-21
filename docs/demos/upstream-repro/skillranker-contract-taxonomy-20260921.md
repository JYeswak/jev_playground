# skillranker contract-test taxonomy — evidence (Axis A, 2026-09-21)

> Evidence only, no plan. Every claim cites
> `/Users/josh/Developer/sr-head-retest@b9e8b34` file:line. Scope: the four
> biggest contract files — 58 tests total (context 9, coordination 21,
> ledger 13, observation 15). Read, not summarized from names.

## (1) What a `contract` test is — and what it asserts that a unit test does not

A contract file opens with a boundary id plus a **Required behavior**
bullet list, and each test proves one bullet across a real surface
(syscall, process, SQLite file, CLI exit), not one function. Three shapes,
verbatim:

**Shape 1 — multi-scenario isolation proof** (`tests/context_contract.rs:162`
`fn branch_and_worktree`, 400 lines, 6 numbered scenarios). Builds a forked
event graph with builders, resolves both leaves, and asserts the negative
space — lines 219-221:

```rust
// Assert sibling branch isolation: no B events on A's active branch
assert!(!active_a.contains_event(&EventId::new("b1").unwrap()));
assert!(!active_a.contains_event(&EventId::new("b2").unwrap()));
```

then re-runs the same topology with skewed timestamps to prove parent
links prevail over timestamp sorting (`:243-284`). An ordinary unit test
asserts one call; this asserts a *boundary holds across six adversarial
arrangements*, declared up front at `:3-11` (`Verifies boundary
p3_branch_resolution`).

**Shape 2 — typed-error + store-invariant proof**
(`tests/ledger_paired_correction_contract.rs:349`
`fn ineligible_alternative_aborts_transaction_zero_judgments`). Drives three
rejected alternatives, matches each error variant exactly (`:425-431`
`FeedbackError::IneligibleAlternative { skill_id, reason }`), then drops to
raw SQL against the real database file and asserts nothing leaked (`:473-494`):

```rust
// Crucial invariant: ZERO judgments committed to SQLite database, data_generation untouched
let jdg_count: i64 = conn
    .query_row("SELECT count(*) FROM judgments", [], |r| r.get(0))
    .expect("count judgments");
assert_eq!(
    jdg_count, 0,
    "ZERO judgments must be committed when alternative is ineligible"
);
```

The assertion is about *transactional side-effect absence*, verified at the
storage layer, not the return value alone.

**Shape 3 — real competing processes**
(`tests/coordination_contract.rs:463`
`fn real_competing_processes_and_single_flight_wide_and_rerank`). Parent
acquires a SQLite lease, spawns a REAL child OS process running the test
binary itself as worker (`:496-511`, env-var handoff, readiness file
rendezvous with 5s timeout), puts the cache entry, then completes — proving
follower delivery across process boundaries for both Wide and Rerank stages.
The helper `CapturedChild` (`:41-90`) drains both pipes with a 64 KiB bound
and reaps on parent panic, so a hung child fails loudly with diagnostics
(`:519-523`).

## (2) How a contract test fails — the message discipline

Three tiers, measured by grep over the four files (255 + 105 + 106 + 61
assert-family hits):

- **Bare `assert!` / `assert_eq!` under a normative comment.** The invariant
  lives in the comment directly above, e.g. `:272` `// Lineage must be
  strictly s_root -> s_b1 -> s_b2, ignoring timestamp ordering!` over a bare
  `assert_eq!`. On failure you get `left != right` plus the comment one line
  up — navigable, not self-describing.
- **`.expect("... must ...")` phrased as the contract itself.**
  `context_contract.rs:600` `.expect("absent first file must succeed as
  prompt_only")`, `:636` `.expect("absent prompt must overlay once")`,
  `:888` `.expect("valid symlink inside root must succeed")`,
  `coordination_contract.rs:445`
  `assert!(res.attempt_id.is_none(), "follower has no attempt id")`.
- **`match`-else-`panic!` with full debug on mistyped errors.**
  `ledger_paired_correction_contract.rs:430`
  `other => panic!("expected IneligibleAlternative, got {other:?}")` —
  names the invariant (the exact variant), names the input (the whole
  unexpected value via `{:?}`).

Verdict: the invariant is ALWAYS named (comment, expect-string, or panic
arm); the input is named when it fits in `{:?}`, otherwise carried by the
comment above. No custom assertion macros anywhere in the four files —
plain `assert!`/`assert_eq!`/`expect`/`panic!` only.

## (3) How fixtures are built — three tiers, ground truth stated

- **Inline builders, zero golden files for domain objects.**
  `EventBuilder` (`context_contract.rs:88-155`, chained `.parent()`
  `.role()` `.kind()` `.text()` `.ts()` `.branch()`), `make_snapshot` /
  `make_event` / `make_candidate`
  (`ledger_paired_correction_contract.rs:51-113`), `temp_private_dir`
  with `0o700` + pid + nanos uniqueness (`:33-49`), fixed logical
  timestamps (`created_at_unix_ms: 1_700_000_000`, `:66`). Ground truth =
  authored domain objects, deterministic by construction.
- **Versioned golden JSON via `include_str!` / `include_bytes!`** for
  wire shapes: `output_contract.rs:8-12` pins four outputs
  (`output-{ranked,explicit,abstain,unavailable,replay}.json`),
  `adapter_contract.rs:40` and `:183` pin adapter payloads, all under
  `tests/fixtures/` (20 versioned `*.v1.json` files). Ground truth =
  committed bytes. (Correction to an early read: fixtures ARE used, via
  `include_*`, not `read_json`.)
- **Real built artifacts, never mocks.** Actual git repos created per test
  through a hermetic `git()` helper pinning author/committer/config
  (`context_contract.rs:67-86`); real child processes (`:496-511`); real
  SQLite files opened with NOFOLLOW/WAL/defensive pragmas
  (coordination header `:10`, `private_tree` + `DirBuilderExt :29-37`).
  Ground truth = live system behavior. No `proptest`/`criterion`/`insta`/
  fuzz anywhere in the verification path (manifest carries zero
  dev-dependencies — conductor-measured, not re-derived here).

## (4) Naming, numbering, navigation — and what enforces it

- **Test names are behavior sentences.**
  `coordinated_deadline_rejects_expired_admission_and_late_provider_without_caching`
  (`coordination_contract.rs:158`),
  `stalled_owner_a_refused_without_replacing_successor_b_body_sqlite`
  (`:1168`), `test_prose_mentions_and_arbitrary_paths_never_count_as_loads`
  (`observation_contract.rs:639`). `grep test-name` answers "what breaks if
  I change X".
- **Numbered normative sections inside big tests.**
  `context_contract.rs:163,243,286,330,454,485` (`// 1. Sibling Branch
  Isolation…` … `// 6. Worktree Resolution…`); `coordination` items 1–10 in
  the file header (`:4-14`).
- **Machine registry.** `tests/contract_matrix.toml` rows carry
  `id` + `owner_bead` + `unit_property_tests = ["tests/context_contract.rs::branch_and_worktree", …]`
  (`:779`, `:1112`) + `status`. File headers point at it
  (`cli_contract.rs:4`, nine files: "mapped in `tests/contract_matrix.toml`").
- **Enforcement is one-directional and real.**
  `scripts/validate_contract_matrix.py` resolves every matrix reference to
  a source declaration with AST-level strictness (`reference_exists`,
  `:189+`: path traversal rejected, exactly-one match, no rebinding,
  unittest-TestCase shape checks) and refuses fake-passed statuses
  (`VALID_STATUSES`, "P0 rows for future product tests are planned, never
  fake passed results", matrix header). `contract_authority.toml` is the
  reviewed-policy input the validator checks against — "never regenerated
  during validation". `scripts/test_contract_matrix.py` tests the validator
  itself with fixtures. **Gap, stated:** no orphan check found — nothing
  verifies every `#[test]` IS registered in the matrix (matrix→source only).

## (5) Portable shapes for a non-Rust, non-his-domain lane

Rule 12 binds: default ADOPT; costs below are in files and hours, deficits
stated per shape.

**P1 — Required-behavior header + numbered normative scenarios.**
Every test file opens with the boundary id and the behaviors under proof;
every multi-case test numbers its scenarios (`// 1. … // 2. …`). Cost:
one header convention (~30 lines of lane doc) + re-titling existing suites
as touched, ~2h one-time plus minutes per new file. Deficit it would NOT
have caught: silent logic errors (it organizes, does not verify). Lose by
refusing: spec drift — tests that no longer prove anything stated.
Adopt.

**P2 — Contract-phrased expect/assert messages + match-else-panic.**
`.expect("absent first file must succeed as prompt_only")`,
`panic!("expected IneligibleAlternative, got {other:?}")`. Cost: a reviewer
checklist line plus one lint pass over existing suites (~2h), near-zero
ongoing. Deficit it would NOT have caught: wrong-but-well-described
behavior. Lose by refusing: unactionable failures (bare `left != right`
with no invariant named). Adopt.

**P3 — Boundary→test registry with a validator that refuses fake passes.**
`contract_matrix.toml` shape (id, owner bead, `file::test` refs, status)
plus a ~100-line script resolving each ref to a real declaration and
rejecting `passed` without evidence. Cost: ~6h to build the TOML +
validator, ~1h per boundary to register. Deficit it would NOT have caught:
orphan tests (no reverse check — port WITH the reverse check added;
cheap: walk `#[test]`/`def test_` and require registration). Lose by
refusing: phantom coverage — the exact class our own suites risk as they
grow. Adopt, with the reverse check his tree lacks.

**Does NOT port cheaply:** real-process/SQLite e2e (needs a harness that
can spawn and reap — our `hub` processes are the analogue, unproven for
this); newtype-heavy builders (the pattern ports, the ergonomics don't).
These stay Rust-side observations, not adoptions.
