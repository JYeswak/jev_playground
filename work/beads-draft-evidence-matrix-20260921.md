# Bead drafts — evidence matrix program (P3 draft, 2026-09-21, NOT yet `br create`)

> Per dispatch: draft file only; pane 4's confirming round may still return
> NOT-YET. Task text follows plan v7 (`b34d3f8` §5). Edges below mirror the
> plan; the RUNTIME edge T5→T2 is stated in T2's body, never declared, or
> `br ready` will lie. M6: no Joshua verbatim behind these tasks — they
> derive from the conductor-owned plan, so no `directive,verbatim` block.

---

## 1. jev-evidence-schema (T1)

- **WHAT:** Add `evidence/SCHEMA.md` plus a commented empty
  `evidence/matrix.toml` encoding §3, including the P1 behavior-header and
  P2 contract-assertion conventions as CONVENTIONS (not checks).
- **WHY:** F1 (ship decisions persisted no evidence) and F6 (no live
  inventory): without a schema doc the first contributor invents a second
  dialect and every later claim is uncheckable.
- **ACCEPTANCE:** a fresh agent writes one valid boundary from the doc
  alone; verify with `python3.12 -c "import tomllib;tomllib.load(open('evidence/matrix.toml','rb'))"`. Rung L1.
- **Depends:** none. **Labels:** (none).

## 2. jev-evidence-validator (T2)

- **WHAT:** Add `scripts/validate-evidence-matrix.py` (stdlib only,
  `python3.12`) implementing the eight deterministic codes:
  `boundary-coverage`, `authority-<field>`, `unresolved-evidence`,
  `missing-red-arm`, `unpersisted-rate`, `uncertified-pass`, `k-drift`,
  `uncovered-bead`.
- **WHY:** F1 (phantom coverage) and F5 (probe-instead-of-enumeration);
  R70 (rates without persisted rows). The validator is what turns prose
  claims into refusable ones.
- **ACCEPTANCE:** each of the eight codes fires on a planted violation:
  run `python3.12 scripts/validate-evidence-matrix.py` against eight
  corrupted fixtures, one nonzero exit per code. Rung L3.
- **Depends:** jev-evidence-schema. **RUNTIME (not a dep):** T5's
  `evidence/authority.toml` must exist before this can run green, though
  it can be written first. **Labels:** `steward:calibration`.

## 3. jev-evidence-red-arms (T3)

- **WHAT:** Ship one planted-violation fixture per validator code plus a
  `--selftest` that exits nonzero if any RED arm stops firing; fixtures
  must not depend on live state.
- **WHY:** F4 (a documented trap recurred): today's callsite RED arm went
  inert the moment its rule was disabled. A gate only ever green is
  unproven (AGENTS.md).
- **ACCEPTANCE:** `python3.12 scripts/validate-evidence-matrix.py
  --selftest` green; delete any single fixture and it goes red. Rung L3.
- **Depends:** jev-evidence-validator. **Labels:** (none).

## 4. jev-evidence-backfill (T4)

- **WHAT:** Register all eight disabled rules, five instruments, R63–R71,
  and the live omp seams as boundaries; every rate carries `label_rows`
  or is marked `unpersisted` and may not claim `passed`; the three
  uncertified rules appear as `retired`.
- **WHY:** F6 (we cannot answer "what is live") and F1; R70/R71 (only
  persisted rows make a later diagnosis possible — structural-def's 4/20
  is undiagnosable precisely because its rows do not exist).
- **ACCEPTANCE:** validator exits 0 on the backfilled tree; `grep -c
  retired evidence/matrix.toml` accounts for the three uncertified
  rules. Rung L2. **Labels:** `steward:calibration`.

## 5. jev-evidence-authority (T5)

- **WHAT:** Add `evidence/authority.toml` plus the one-paragraph AGENTS.md
  rule that bars, n, scopes, and rungs move only by Joshua's edit.
- **WHY:** F3 (bars set and measured by the same party): without the
  second key this is a nicer spreadsheet, not a control.
- **ACCEPTANCE:** a matrix edit moving a bar fails with
  `authority-rate.bar`. Rung L2.
- **Depends:** jev-evidence-schema. **Labels:** (none).

## 6. jev-orphan-walker (T6a)

- **WHAT:** Define a case (explicit static id; `note ok` gains a leading
  id argument) and add `--list-cases` to every in-scope file
  (`scripts/selftest-*.sh` plus `*.test.mjs` under `work/*/test/`, and
  only those): normalize 5 files to the idiom, assign ids to 46 cases
  (16 interpolate today), disambiguate 5 collisions. Measured cost ~4h;
  the largest task in the program.
- **WHY:** F1 (phantom coverage) via the Axis A gap (nothing checks the
  reverse direction); my validation round proved the v2 task text
  unimplementable as written — no case IDs exist anywhere.
- **ACCEPTANCE:** `--list-cases` on every in-scope file yields a unique
  id set containing no `$`. Rung L3.
- **Depends:** jev-evidence-schema, jev-evidence-validator (NOT backfill;
  runs parallel with it). **Labels:** (none).

## 7. jev-orphan-enforce (T6b)

- **WHAT:** Enforce registration of every enumerated case against a
  **temporary fixture matrix in `mktemp -d`** — removing a row whose case
  still exists exits `orphan-case`. No test mutates the real matrix.
- **WHY:** F1: unregistered cases are phantom coverage by construction.
- **ACCEPTANCE:** the fixture-matrix removal test exits `orphan-case`;
  the real matrix is byte-identical before and after
  (`git diff --exit-code -- evidence/matrix.toml` empty — file may not
  exist yet; then the test asserts the fixture path only). Rung L3.
- **Depends:** jev-orphan-walker. (Deliberately NOT backfill: P4's round 2
  caught the false edge; acceptance needs one row, not a full inventory.)
  **Labels:** (none).

## 8. jev-evidence-gate (T7)

- **WHAT:** Wire the validator into `foundation/gates.sh` (extend stage
  `80` if it fits, per gate thrift); a matrix violation turns the gate red.
- **WHY:** R68 (an unwired validator is an unconsumed instrument — the
  phase boundary forbids adding another) and F6.
- **ACCEPTANCE:** `gates.sh --selftest` green; a planted matrix violation
  turns the gate red. Rung L4.
- **Depends:** jev-evidence-red-arms, jev-orphan-enforce. **Labels:** (none).

## 9. jev-arc-regen (T8)

- **WHAT:** Regenerate ARC.md figures from the matrix so the freshness
  guard fails on disagreement.
- **WHY:** F1 as published: our ARC.md rotted the day it shipped; a
  published number unmoored from its source repeats the day's central
  failure in the document that reports it.
- **ACCEPTANCE:** alter one matrix figure source and the guard fails;
  restore and it passes. Rung L3.
- **Depends:** jev-evidence-gate. **Labels:** (none).

---

## Dependency summary (for `br dep add` after approval)

```
jev-evidence-validator      <- jev-evidence-schema
jev-evidence-authority      <- jev-evidence-schema
jev-evidence-red-arms       <- jev-evidence-validator
jev-evidence-backfill       <- jev-evidence-validator
jev-orphan-walker           <- jev-evidence-schema, jev-evidence-validator
jev-orphan-enforce          <- jev-orphan-walker
jev-evidence-gate           <- jev-evidence-red-arms, jev-orphan-enforce
jev-arc-regen               <- jev-evidence-gate
```

RUNTIME, not declared: T5's `evidence/authority.toml` must exist before
T2 runs green. Parallel tracks after T1: {T2, T5}, then {T3, T4, T6a}.
