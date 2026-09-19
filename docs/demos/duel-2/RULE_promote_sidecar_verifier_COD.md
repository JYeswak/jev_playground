# Q89 Rule: Keep the Sidecar Verifier Hand-Run for Now

**Decision:** do **not** promote `verify-other-reasons.sh` to `foundation/gates.sh` yet. Keep it a hand-run candidate until it reads a stable snapshot or copy rather than live shared STATUS/sidecar state.

## Why promotion is unsafe now

The verifier is read-only, but read-only is not the same as snapshot-safe. It reads two mutable shared artifacts:

- `docs/demos/STATUS.tsv`;
- `docs/demos/duel-2/runs/receipt-other-reasons.json`.

A peer can update one between the verifier's reads, or can stage/format one while the other is old. The verifier can then report an exact-coverage, digest, or binding failure caused by an in-progress state rather than by a committed defect. In a three-pane worktree, that is a transient RED that trains operators to rerun until green—the same failure mode as a gate wired to the wrong edge.

The foundation aggregate is not commit-wired, but it is still an aggregate failure surface. A foundation RED should represent a stable repository inconsistency, not a peer's partial edit.

## Current decision

- **Foundation:** leave the verifier unpromoted.
- **Commit hook:** never wire it directly under the current contract.
- **Hand-run:** permitted when the operator has established a stable read boundary and records the exact STATUS/sidecar revisions.
- **Stage 80:** its hermetic `selftest-other-reasons.sh` may remain in the foundation selftest stage; that tests the verifier's RED arms on copies and does not promote the live verifier.

This preserves the Q77 contract: the sidecar is documentation/provenance, not gate input.

## What would make promotion safe

Promote only after all of these exist:

1. The verifier accepts explicit `JEV_STATUS` and `JEV_SIDECAR` paths or a wrapper copies both files into one temporary snapshot before invoking it.
2. The snapshot carries one source revision or content hash for both inputs; the verifier records that pair in its output.
3. The wrapper cannot observe a half-written file and never mutates the real STATUS or sidecar.
4. A known-good copied pair passes.
5. Each known-bad copied arm REDs independently: missing/extra entry, wrong reason, sidecar/live/STATUS digest disagreement, invalid primary or corroborating locator, missing per-entry provenance, and short STATUS row.
6. A concurrent-writer or inconsistent-pair arm is classified `TRANSIENT_UNSTABLE`/retry, not as a durable metadata defect.
7. Foundation execution is explicitly non-commit-wired and reports whether it checked a stable snapshot.

Only then can a foundation wrapper distinguish:

```text
stable snapshot + verifier RED       => durable metadata defect
unstable or mixed snapshot            => retry / UNMEASURED
stable snapshot + verifier PASS      => metadata check passed
```

## Re-examination condition

Re-examine promotion when the snapshot contract and copy-based arms are landed. Also re-examine if:

- STATUS and sidecar begin landing transactionally in one commit;
- a file-lock or atomic snapshot protocol is available and proven;
- operators can provide a stable commit/tree revision for both inputs;
- repeated hand-runs show a durable defect rather than transient mismatches;
- the verifier's result is needed by a downstream foundation stage that can consume `TRANSIENT_UNSTABLE` distinctly from RED.

Do not promote merely because the current live run is green. A green shared read is not proof of a stable pair.

## Scope

The verifier is useful and its five selftest arms belong in the hermetic stage. The live verifier remains hand-run until its read boundary is made stable. No commit-hook wiring is authorized.
