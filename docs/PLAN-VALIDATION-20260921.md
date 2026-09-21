# PLAN validation — implementability audit, 2026-09-21 (P3)

> Target: `docs/PLAN-EVIDENCE-MATRIX.md` at `680d11e` (279 lines).
> Method: skill://planning-workflow validation loop. Not a grade — the list
> of places a fresh agent stops. python3.12 verified present
> (`/opt/homebrew/bin/python3.12`, 3.12.13; system `python3` is 3.9.6 with
> no `tomllib`), so T2's pin note is load-bearing, no stop there.

## (1) Self-containment — T6 read alone

1. **"Walk every selftest-*.sh case" — what is a case?** Our selftests emit
   `ok <label>` stdout lines; no case IDs exist anywhere. A fresh agent
   cannot enumerate what the task tells them to walk. STOP.
2. **Which `*.test.mjs`?** No directories named. Candidates this agent can
   see: `compaction/test/`, `pi-subagents/test/`, others. STOP.
3. **Acceptance deletes a live boundary row.** Destructive test on real
   files with no restore/isolated-fixture instruction. STOP (minor — a
   tmp-matrix fixture satisfies it, but it must say so).
4. **T2 reference point:** "the first six codes" — six of thirteen, mapping
   unstated. A fresh agent guesses. STOP.

## (2) Dependency graph

Edges (from Depends lines, which overrule the picture): T1→T2, T1→T5,
T2→T3, T2→T4, T4→T6, T3→T7, T6→T7, T7→T8. No cycles. Two findings:

5. **T5 is graph-orphaned.** Nothing depends on it, yet T2's checks compare
   against the authority file at runtime. Runtime-required but
   order-invisible — a scheduler reading edges builds T2 before T5 exists.
6. **The ASCII picture disagrees with the Depends lines.** The drawing merges
   T5 into the T2→T4 edge and T3 into the T4→T6 edge. A fresh agent
   following the picture builds the wrong order. STOP — picture or text
   must change.
7. **T6→T4 is partly a false edge (independent answer to the conductor).**
   The walker + case-identity definition needs only T1+T2 and can run
   parallel with T4; only the green run needs a populated matrix, and the
   delete-row acceptance needs exactly ONE row, not a full backfill.
   Recommend T6a (walker, after T1+T2) / T6b (green run, after T4). P4's
   suspicion is directionally right; full removal is wrong.

## (3) Justification sample (5 architectural decisions)

- stdlib-only Python: GENUINE (pane environments vary).
- Fixed diagnostic codes: GENUINE (transcript secrecy).
- Joshua holds the second key: GENUINE (causal F3 story).
- Mutation twins: GENUINE (trustworthy-vs-present).
- **No hosted CI: FLAGGED.** §2 argues by imitation ("he does not have
  one either"); the actual cost/defect argument lives in §7's refusal.
  A §2-only reader gets assertion. Move the pointer, not the argument.

## (4) Steady state — v1 (662154d) vs v2 (680d11e)

+59/-6, all inside the claim schema (§3 example), the check table (§4,
+4 rows), and new §4.1. Tasks, DAG, acceptance, refusals untouched.
Structural in meaning (dual bar changes what `passed` means) but surgical
in extent. **One more focused round, then done:** fix findings 1, 2, 4, 6,
7 and the §2→§7 pointer. No full re-review needed.
