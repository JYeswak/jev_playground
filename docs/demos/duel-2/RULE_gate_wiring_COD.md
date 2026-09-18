# Q83 Rule: Wiring the Hand-Run Gates

**Decision:** wire only the hermetic metadata verifier to the foundation edge; keep live-state and historical-lineage instruments hand-run. None of the three belongs on the commit hook today.

## Wiring decisions

| Instrument | Decision | Edge | Reason |
|---|---|---|---|
| `scripts/lane-status.sh` | **LEAVE HAND-RUN** | Tick's first instruction | Reads the mutable shared worktree, STATUS, receipts, panes, beads, and uncommitted deliveries. A commit-edge invocation would inspect transient partial state and can block all three panes in a shared worktree. The tick instruction is its current consumer; its output must remain explicit existence/integrity state, not a hidden hook. |
| `scripts/audit-score-lineage.sh` | **LEAVE HAND-RUN** | Manual/history audit only | It exits `6` on the current historical untyped score/verdict coincidences by design. Wiring it to foundation or commit would turn a correct `UNTYPED` result into a worktree-wide block before the declared-type migration/history replay is complete. It is an audit of history, not a commit-local predicate. |
| `scripts/verify-other-reasons.sh` | **WIRE TO `foundation/gates.sh`**, not commit hook | Hermetic foundation stage | It validates committed STATUS/sidecar metadata, exact coverage, normalized digest binding, and evidence locators. It has no network/key dependency and its failure is a real metadata inconsistency. It must remain a standalone metadata failure, not a score/verdict gate. |

The associated selftests are support evidence:

- `selftest-lane-status-integrity.sh` may run as a foundation stage once its fixture harness is wrapped without reading the shared STATUS file.
- `selftest-score-lineage.sh` may run as a foundation stage because it uses temporary pair fixtures and does not replay the untyped historical repository.
- `verify-other-reasons.sh`'s planted bad arms must run in its foundation wrapper against copies, never by truncating or mutating the real STATUS/sidecar.

These support selftests do not authorize wiring the live-state or historical instruments themselves to the commit edge.

## Why not the commit hook

A commit hook is the wrong edge for all three today:

- `lane-status.sh` observes worktree state that is intentionally incomplete while agents work;
- `audit-score-lineage.sh` has a legitimate nonzero historical result (`rc=6`), so it would block every pane;
- sidecar verification is documentation integrity, but a commit can legitimately stage STATUS and its sidecar in separate, exact-path commits during a migration. The foundation edge gives one explicit aggregate failure without making every commit impossible; a future staged-pair hook would require a separate transactional contract.

The existing commit hook should continue to enforce only commit-local properties: verification-level subject, staged deletion survival, and other already-wired first-party checks. Do not smuggle lane-wide history or mutable-state audits into it.

## Foundation wrapper contract

The wrapper for `verify-other-reasons.sh` must:

1. run from the repository root with the real committed STATUS/sidecar;
2. use the verifier's own `--selftest`/fixture mode once one exists, with copies for planted bad rows;
3. propagate `0` as PASS and `1` as RED; reserve `2` for environment/missing-input failure;
4. print that the result is documentation-only and does not alter lane verdicts;
5. fail closed on exact-coverage, digest, locator, or width failures;
6. never rewrite STATUS, the sidecar, or receipts.

`foundation/gates.sh` already aggregates executable numbered stages and turns any nonzero stage into RED. The wrapper belongs there only after the verifier's five bad arms are exercised without shared-tree mutation.

## Re-examination condition

Re-examine wiring when:

- a tick driver is added and can consume `lane-status.sh` continuously without treating transient shared-worktree state as a commit failure;
- `audit-score-lineage.sh` replays history with all receipt types declared and returns clean/typed status, including a selftest for untyped historical rows;
- a transactional staged-pair contract exists for STATUS plus sidecar, making a commit-edge metadata check satisfiable;
- any wired verifier returns a nonzero code on a known-good fixture or fails to RED on a planted bad copy;
- a gate is found to block unrelated panes, mutate shared state, or require unavailable credentials/network.

At re-examination, promote one instrument at a time and require a positive known-good and known-bad arm before changing its edge.

## Scope

This is a wiring ruling, not an implementation. Current state remains: lane-status is tick-run, audit-score-lineage is hand-run, and verify-other-reasons is the only candidate for foundation wiring after its non-mutating selftest wrapper lands. No commit-hook wiring is authorized by this document.

## Q87 recheck — current registry agrees; wiring remains conditional

The current GATES.md rows still describe all three instruments as not wired to a commit edge. That is correct. The decision remains:

- lane-status.sh: hand-run by the tick, not foundation or commit; it reads mutable shared state.
- audit-score-lineage.sh: hand-run only; its intentional rc=6 for untyped history would block every pane if wired.
- verify-other-reasons.sh: foundation-stage candidate after its copy-based selftest wrapper lands; not commit-hook wiring.

The foundation aggregator is the appropriate future edge for the sidecar verifier because it is a repository-consistency check, not a transient worktree or historical-score check. No implementation or wiring claim is made by this recheck.
