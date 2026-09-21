# Axis D — the contract matrix, measured by running it

**Pane 1. Every claim below was executed, not read.** Target:
`/Users/josh/Developer/sr-head-retest`, verified against `origin/HEAD` = `77f302b3`.

## What nobody here had ever done

We have used `sr` as a binary and filed one bug against it. We had never run a single one of its
112 test harnesses, read its contract taxonomy, or executed its validators. This is the first
execution.

## The shape of the tree

| measure | value | command |
|---|---:|---|
| source LOC | 51,613 | `find src -name '*.rs' \| xargs cat \| wc -l` |
| **test LOC** | **63,051** | `cat tests/*.rs \| wc -l` |
| test files | 112 | `ls tests/*.rs \| wc -l` |
| **dev-dependencies** | **0** | `Cargo.toml` has no `[dev-dependencies]` section |
| CI workflows | **0** | `.github/workflows` does not exist |
| validator scripts | 11 | `ls scripts/*.py` |
| contract docs | 21 of 56 | `ls docs/*contract*.md` |

**Tests exceed source by 22%, with zero test frameworks.** No proptest, no criterion, no insta,
no fuzz target. 63k lines of verification hand-built on `#[test]` and std — the same
zero-dependency discipline the Jev clients show, applied to the side everyone else outsources.

**There is no CI.** Rigor is mechanized as *runnable validators in the tree*, not as a hosted
pipeline. That is portable to us; a GitHub Actions file would not be.

## The manifest carries invariants with their reasons

`Cargo.toml:39-43` — `unsafe_code = "forbid"`, `clippy::all = "warn"`.
`Cargo.toml:21-33` — every third-party dep pinned **exactly** (`=0.5.0`, `=6.0.0`, `=1.0.3`,
`=0.40.2`); both `frankensearch` crates pinned by **rev**.
`Cargo.toml:35-37` — `[patch.crates-io]` whose comment states the hazard it exists to control:
*"Quill's Cx and our Cx must come from exactly the same package source."* Type identity enforced
in the build graph, with the why written next to the how.
`Cargo.toml:15-18` — `tui = []`, commented *"Reserved boundary; no TUI implementation or terminal
dependency ships yet."* **A named seam that deliberately ships nothing.**
`rust-toolchain.toml` — `channel = "nightly-2026-08-31"`, `profile = "minimal"`, components
`clippy` + `rustfmt`. A pinned date, not a floating channel.

## The keystone: a two-key contract matrix

`tests/contract_matrix.toml` — **92 boundaries**, 1,671 lines.
`tests/contract_authority.toml` — **79 boundaries**, 955 lines.

Each boundary binds the plan to its evidence:

```toml
[[boundaries]]
id = "p0_bootstrap"
owner_bead = "sr-roadmap-l1i.1.1"                                   # the plan
member_beads = ["sr-roadmap-l1i.1.1"]
phase = "P0"                                                        # the ladder
title = "Bootstrap the single Rust 2024 package and reproducible build boundaries"
unit_property_tests = [
    "tests/bootstrap_cli.rs::version_reports_package_version"       # exact evidence
]
e2e_suite = "not-applicable"
e2e_cases = []
assertion_ids = []
platforms = ["linux"]                                               # scope of the claim
features = []
status = "executed"                                                 # planned|executed|passed|failed
```

**Why two files.** `validate_contract_matrix.py:342` requires
`set(rows) == set(expected)` against the *authority*, then `:348-349` requires byte-equality on
every `BOUND_FIELD` (`owner_bead, phase, title, member_beads, platforms, features, e2e_suite,
e2e_cases, assertion_ids`). The authority file is **reviewed policy**; the matrix is the working
declaration. **You cannot widen your own coverage claim** — the bar lives behind a second key.

Further binding: `:343-345` pulls non-epic roadmap beads from `.beads/issues.jsonl` and requires
coverage; `:369` requires every `assertion_id` to exist in a catalog (`unknown-assertion`).

**The epistemics are in the code, not a README.** Module docstring, `:3-5`:

> *"Declaration validation is never a test-execution or product acceptance receipt. The separate
> authority file is reviewed policy, not generated runtime evidence."*

And `:189-190`, `reference_exists`: *"Resolve source declarations only; this is not an execution
receipt."* He distinguishes *declared*, *reviewed*, and *executed* in three separate places.

`class InvalidMatrix(ValueError)` — *"Fixed diagnostic codes avoid copying file contents into
logs."* Failures emit a code (`boundary-coverage`, `authority-phase`, `unknown-assertion`), never
a content dump.

`TRUSTED_CHECK_ENTRYPOINTS` is a **frozenset allow-list** of three `path::main` entrypoints, with
the reason: *"Any other plain function is a helper, not test evidence."*

## Executed results

```
$ python3.12 scripts/validate_contract_matrix.py
invalid contract matrix: boundary-coverage
rc=1
```

**RED at HEAD, and deterministically so** — both inputs are tracked files, `.beads/` is present,
and the same counts hold at `origin/HEAD`: matrix 92, authority 79.

The 13 unblessed ids are exactly `p4_cache_isolation`, `p4_explain_exclusion_stages`,
`p4_parser_corpus`, `p4_rank_pipeline`, `p4_table_and_decision_views`,
`p4_versioned_json_failure_envelopes`, `p5_ledger_exposure_lifecycle`, `p5_ledger_init_migration`,
`p5_ledger_paired_correction`, `p5_ledger_retention_prune_clear`, `p5_observation_watermark`,
`p5_quota_headroom`, `p5_replay_isolation` — **every one of them P4 or P5**.

**This is not a defect and must not be filed.** The matrix is RED *during* phase development and
goes green when the phase is blessed into the authority file. The mechanism is working: six P4
and seven P5 boundaries are declared and not yet reviewed. Checking this before filing is the
second bad report avoided today.

## The calibration fact that should reframe our claims

Status across all 92: **33 `executed`, 59 `planned`.**

By its own declaration, **64% of this tree's contract boundaries are not executed** — and it says
so in a tracked, machine-validated file. A project with 63k lines of tests publishes that it is
36% executed.

Our lane spent today discovering it had shipped eight rules on unauditable numbers. The
difference is not that he is more careful in prose; it is that **his coverage claim is a data
structure a validator can refuse.**

## Boundary

Not run: the 112 harnesses themselves (`cargo test`) — the toolchain is pinned to
`nightly-2026-08-31` and a local build is denied by construction here; the cross-build path
exists but a full suite run was not attempted. No claim is made about whether his tests pass.
Everything above is manifest, matrix, validator, and counts. `--require-mechanics`,
`--smoke-receipt`, and `--certificate-receipt` were not exercised.
