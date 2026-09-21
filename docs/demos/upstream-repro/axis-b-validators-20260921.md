# Axis B — the eleven validators as plumbing (2026-09-21)

> Evidence only, no plan. All paths under
> `/Users/josh/Developer/sr-head-retest@b9e8b34`. Supplements Axis D, which
> fully characterized `validate_contract_matrix.py` — not re-derived here.
> Per P4's axis-C finding (2500 lines of Jev tests certify the WIRE, never
> the JUDGE), this axis is plumbing: what runs, what refuses, what proves
> the check can fire. Our judgment stays ours.

## (1) The other ten validators — invariant, failure code, RED arm

| script (lines) | invariant enforced | failure code | RED arm |
|---|---|---|---|
| `check_dependency_graph.py` (129) | banned ML/network deps (`tokio`, `reqwest`, `tantivy`, `candle`, `ort`… `:16-20`); Quill+core same Git source/rev (`:56`); required packages present; feature power-set bounded — >8 non-default features REFUSES (`:29`) | `ValueError`, exit 1 | `test_dependency_graph.py` (8 tests): prohibited packages refused, oracle features can't hide behind safe packages |
| `check_native_storage_boundary.py` (236) | slice build of `src/sqlite_engine.rs` + platform files against EXACT lock pins; slice manifest injects `unsafe_code = "forbid"` (`:95`); only locked source/version/checksum identities permitted (`:98-114`) | `ValueError`, exit 1 | `test_native_storage_boundary.py` (15 tests on synthetic lock graphs; fixture docstring: "not a replacement for production Cargo.lock") |
| `check_platform_boundary.py` (149) | probe crate assembled from exact reachable lock blocks, no copied Rust (`:4-5`); **refuses simulated evidence** — non-Darwin `--native-macos`, missing toolchain, or ambient `RUSTFLAGS`/`CARGO_ENCODED_RUSTFLAGS` all `parser.error` (exit 2); returns the real `cargo test` rc otherwise | exit 2 (refused premise) / 1 (failed) / cargo rc | NONE FOUND — no `test_platform_boundary.py` exists; the strictest-talking check has no adversarial test |
| `test_contract_matrix.py` (490) | adversarial fixtures corrupting matrices (duplicate IDs, invalid phases, future passed claims) must be rejected with clear errors | unittest failures | self-testing (is itself the RED arm for the matrix validator) |
| `test_dependency_graph.py` (89) | synthetic GOOD graph accepted with exact counts (`package_count == 4`) | unittest failures | same file (each row is its own arm) |
| `test_eval_policy.py` (435) | 43 mutation tests: corrupt one semantic field → `SystemExit` (false abstention scored correct, coverage≠recall, averages hiding loss, unstarted cases disappearing, family-independence replacing model assumptions) | `SystemExit`, unittest failures | same file; artifacts kept in tmpdir, never deleted ("Keep synthetic artifacts for diagnosis") |
| `test_native_storage_boundary.py` (192) | synthetic lock-graph validation logic | unittest failures | same file |
| `validate_eval_policy.py` (521) | frozen v1 policy fixture — see §2 | `validation failed: <reason>`, exit 1; CLI misuse sanitized (`SafeArgumentParser` hides argv contents — "can contain private paths or credentials", `:488-493`) | `test_eval_policy.py` (every semantic has a corrupt-it-must-fail twin) |
| `validate_public_contracts.py` (201) | docs consistency WITHOUT execution or network: heading anchors, links, JSON/TOML examples re-parsed strictly (duplicate keys rejected, non-finite floats rejected, surrogate halves rejected, `shape()` compares field/type contracts) | `InvalidDocument`, exit 1 | NONE FOUND — no `test_public_contracts.py`; docs-consistency is unguarded by its own tests |
| `scripts/e2e/` (`runner.py`, `runner_contract.py`, `evidence.py`, suites, `product.sh`…) | 19 scenarios incl. deliberately-failed inner runs that **must remain failed** when outer certification succeeds (`runner_contract.py:17-19`); MUTATIONS list (schema-mismatch, duplicate-terminal, …) | scenario verdicts `failed/{exit,signal,timeout,…}` | the deliberately-failed scenarios ARE the RED arms |

Two gaps, stated: the platform-boundary check (loudest epistemic claims) and the docs-consistency validator have no adversarial test files.

## (2) His eval policy — what it is and what stops it drifting

`validate_eval_policy.py` validates three frozen fixtures under
`tests/eval/` (`evaluation_policy.v1.json`, `synthetic_cases.v1.jsonl`,
`expected_values.v1.json`), stdlib only, and declares up front what it is
not (`:2-6`: "does not evaluate SkillRanker, call Jev, inspect harnesses,
or claim benchmark pass").

The policy fixture carries its own anti-drift payload:

- **Status + non-claims are load-bearing fields.** `status` must equal
  `frozen_contract_not_evidence` (`:195`); ≥4 non-claims must contain the
  phrases "not an evaluator", "not a 300-family", "synthetic", "no live"
  (`:197-200`). The fixture cannot silently become a claim.
- **Cohorts with exact numbers.** Relevance 300/150/100/50, controlled harm
  150 independent family pairs for any zero-event iid claim, operational
  500 invocations incl. provider outages (`:204-229`); cohorts must stay
  separate (`:210`, `:221`).
- **Loss table 0/1/2 exact**, integers-not-booleans, equal-loss tie-break
  prefers fewer failures (`:231-244`).
- **Method pinned with assumptions.** Relevance intervals =
  `two_sided_95_wilson_with_one_primary_case_per_independent_family`
  (`:247-249`); top-one precision needs rate 0.90 AND Wilson lower 0.80
  (`:263`); harm uses one-sided 95% Clopper-Pearson (`:219`).
- **Baselines frozen including the negative control.**
  `always_abstain` + 6 cookbook/choice/fit/blend/latest-request baselines
  (`:250-253`); the expected-values fixture must PROVE always-abstain loses
  (`:429` "always-abstain counterexample must make always abstain worse").
- **Missing/failed/unstarted have semantics, not nulls.**
  `not_estimable`, `unfinished_partial_report`, attempted failures keep
  full loss 2 (`:271-277`, `:443-463`).
- **Twelve case kinds**, each with an executable oracle contract
  (`validate_case_oracle`, `:163-190`: e.g. near-miss must not count as
  correct; overflow coverage at 254; roster-change must not publish t0).
- **Byte-level hygiene throughout**: 1 MiB artifact cap, 64 KiB record cap,
  10k record cap, no blank JSONL rows, no duplicate keys anywhere, nesting
  cap 64, FIFO-safe file opens (`O_NONBLOCK`, `:39-45`).

What refuses drift: `test_eval_policy.py`'s 43 tests each corrupt ONE
semantic and demand `SystemExit` — the policy cannot soften by a word
without a red test naming the field.

Our parallel, honestly: our `foundation/` has schemas + fixtures + run
receipts, but no frozen-policy-with-mandated-non-claims and no
corrupt-one-field-must-fail suite. That pair is the adoptable gap.

## (3) With no CI, what tells an agent what to run when

No Makefile, no justfile, no `.github/`. Three mechanisms:

1. **`AGENTS.md` gate block**: after substantive Rust changes, `cargo
   fmt --check`, `rch exec -- cargo check/clippy/test --locked`, `ubs
   --diff`; doc-only changes get links/examples/license/hygiene and
   explicitly "do not manufacture a Cargo result". Plus a **boundary
   evidence table** (session/context → concurrent sessions, compaction…;
   Jev/scoring → real fixtures, duplicate IDs, invalid sums…; runtime →
   slow stdin, DNS/TLS, pipe saturation…) telling the agent what KIND of
   real evidence each boundary demands.
2. **Runnable scripts with argparse `--help`** — every validator is
   directly invocable (`python3 scripts/validate_eval_policy.py`).
3. **Standing doctrines**: "Retain adversarial assertions and honest
   success counterparts"; "Infrastructure failure is not a test pass";
   "Never put personal transcripts or credentials in fixtures."

## (4) Three mechanisms that port, with costs

Rule 12 binds (default ADOPT; costs in files/hours; deficits stated).

**P1 — Frozen-policy fixture with mandated non-claims + exact re-assertion**
(`validate_eval_policy.py` shape, 521 lines). Cost: 1 JSON policy + 1
stdlib validator (~200 lines for our scale), ~6–8h; ~1h per threshold
change. Catches: threshold/wording drift in our own eval gates. Deficit it
would NOT catch: a consistently-enforced garbage policy (validates
consistency, not quality). Adopt.

**P2 — Corrupt-one-field-must-fail tests per validator**
(`test_eval_policy.py` shape, 43 tests). Cost: ~2h per existing
validator/check reusing current fixtures. Catches: dead checks — a
validation that cannot fire (our UBS TTSR lesson: a guard only ever green
is unproven). Adopt.

**P3 — Docs-consistency validator without execution**
(`validate_public_contracts.py` shape, 201 lines, stdlib only). Cost:
~3–4h port. Catches: rotting prose claims (links, anchors, JSON/TOML
examples). Note his own gap: NO adversarial test file for it — port WITH
one (corrupt an anchor, demand failure). Adopt, improved.

**Does NOT port cheaply:** the e2e runner (needs harness process infra),
the native/platform boundary builders (needs our toolchain story told
first). Observed, not adopted.
