# Q92 Specification: `TRANSIENT_UNSTABLE`

**Purpose:** prevent a live shared-worktree read from being mistaken for a durable RED or a clean result.

## Snapshot contract

For the receipt/integrity portion of a lane-status or sidecar-verifier run, capture one immutable temporary snapshot containing:

1. `docs/demos/STATUS.tsv`;
2. `docs/demos/duel-2/runs/receipt-other-reasons.json` when sidecar verification is requested;
3. every receipt path cited by the captured STATUS row set;
4. an input manifest containing each relative path, byte count, raw SHA-256, normalized SHA-256 where the existing contract defines one, and the repository `HEAD` used for the observation.

The snapshot is built in a private temporary directory. Never truncate, rewrite, or restore the shared source files. Copy bytes first; then hash the source paths again. A source hash or byte count changing during capture means the snapshot was not stable.

The verifier runs only against the copied snapshot. Its output carries:

```text
snapshot_id
capture_attempts
source_head
input_manifest_sha256
snapshot_stable=true|false
```

A stable snapshot is a bounded observation, not a claim that the worktree cannot change after capture.

## Revision/hash binding

`source_head` binds the snapshot to the repository revision when capture began. The per-file raw SHA-256 binds the actual bytes. For receipt files, the existing content-normalized digest is recorded in addition to raw SHA-256; it does not create a second semantic identity.

After copying, recompute the source file's raw byte count and raw SHA-256. The copy is valid only when the source and copy match and the second source read matches the first capture manifest. The verifier must also ensure that every STATUS receipt path resolves inside the captured root and that the sidecar's receipt path and digest agree with the captured STATUS row.

`HEAD` alone is insufficient: uncommitted files are part of the shared worktree. Hashes alone without the path/row manifest are also insufficient: a different file set can hash cleanly.

## Bounded instability algorithm

Use at most **two capture attempts**:

1. Capture all inputs and perform the post-copy source re-read.
2. If any source changed during attempt 1, discard that snapshot and capture once more.
3. If attempt 2 is stable, validate it even if its result is RED. Report `capture_attempts=2` and `snapshot_replaced=true`; do not rerun merely to obtain green.
4. If attempt 2 is also unstable, return `TRANSIENT_UNSTABLE` with both changed-path lists and no substantive verdict.
5. If a stable snapshot validates and the verifier finds a defect, return the durable verifier RED. If it passes, return PASS.

There is no unbounded retry loop. Re-running after `TRANSIENT_UNSTABLE` is a new operator invocation and must carry a new snapshot ID; it is not an automatic green-seeking retry.

## Exit code

Current lane-status codes use 2 through 9. Reserve:

```text
10 = TRANSIENT_UNSTABLE
```

Code 10 means the input set could not be captured atomically enough to support a verdict. It must be accompanied by `snapshot_stable=false`, changed paths, attempt count, and no PASS/RED claim for the affected check.

Environment/usage errors remain code 2. Durable schema, missing-receipt, digest, concurrence, and type failures retain their existing codes after a stable snapshot is established.

## Lane-status ruling

`lane-status.sh` **should gain this contract for receipt/schema/integrity claims**. The exposure is not negligible: three panes share the worktree, peers edit STATUS and receipts, and a partial edit can produce the same apparent RED as a real defect. A single conductor read is not a writer exclusion.

The rest of lane-status—pane state, beads, uncommitted deliveries, and artifact byte totals—is inherently a point-in-time observation. Label those fields `observation_time`/`live_observation` rather than pretending they share the receipt snapshot's durability. Do not block a commit on the mutable live surfaces.

The sidecar verifier should use the same snapshot contract before foundation promotion. Until then it remains hand-run, as Q89 ruled.

## Re-examination condition

Re-examine this contract when:

- a file-lock or atomic transaction makes a stronger snapshot possible;
- a two-attempt cap produces repeated `TRANSIENT_UNSTABLE` results during normal operation;
- a verifier needs more than two attempts to complete capture;
- a caller treats code 10 as RED or PASS rather than retry/UNMEASURED;
- a peer-edit race is reproduced on a stable copy and the changed-path evidence is insufficient;
- STATUS/sidecar move to a storage layer with an atomic revision boundary.

Any change must retain bounded attempts and make the snapshot identity visible.

## Scope

This is a contract, not an implementation. It does not change current lane-status exits or promote the sidecar verifier. It defines the precondition for making either claim durable in a shared worktree.
