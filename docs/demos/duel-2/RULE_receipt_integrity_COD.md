# Q58 Rule: Receipt Integrity Without Hook Deadlock

**Decision:** choose **(c) content-normalised digests**.

The lane-status instrument must pin a digest for every cited receipt, but the digest is computed over a canonical byte representation that strips only the final run of trailing whitespace bytes (`0x20`, `0x09`, `0x0a`, `0x0d`) from the file. It must not parse, reorder, reindent, or otherwise rewrite JSON. A one-time baseline is required after the current hook-normalised state is committed.

## Why this option

- **(a) Raw-byte digests** would fail on the known one-newline autofix mutation. That would make the integrity gate red on ordinary commits before it had a satisfiable repair path. A dead gate is not a high bar.
- **(b) Existence only** is honest about the current script but leaves receipt substitution and substantive mutation invisible. It is insufficient for a receipt-based lane claiming reproducibility.
- **(c) Content-normalised digests** reject substantive changes while explicitly accepting the only observed hook drift: one terminal newline. They preserve a satisfiable gate without pretending that every byte is immutable.

The normalisation exception is deliberately narrow. Whitespace inside JSON strings, between structural tokens, or anywhere except the final trailing-whitespace run remains hashed. A formatter that changes indentation or key ordering therefore changes the digest.

## Required instrument output

For every cited receipt, `lane-status.sh` must print two separate results:

```text
receipt=<path> exists=YES integrity=NORMALIZED_SHA256_OK sha256=<digest>
```

or:

```text
receipt=<path> exists=YES integrity=DRIFT normalized_sha256=<actual> expected=<pinned>
```

Missing artifacts remain a separate failure:

```text
receipt=<path> exists=NO integrity=UNASKABLE
```

The summary must state counts independently:

```text
RECEIPTS: existence_checked=<n> missing=<n> integrity_checked=<n> drifted=<n> normalization=terminal-whitespace-only
```

A reader must never infer integrity from an existence-only `OK` line. The current instrument should retain its existing missing-receipt exit code and add a non-zero integrity-drift exit code once pinning is deployed.

## Baseline and repair

1. Run one explicit normalisation commit so the five known one-newline changes are in the committed state.
2. Generate the pinned normalized digest manifest from the committed receipt set.
3. Add integrity verification to `lane-status.sh` and a positive-control test that changes a non-terminal byte and expects `DRIFT`.
4. Add a separate test proving one terminal newline does not drift.
5. Keep missing-receipt and digest-drift diagnoses separate; do not collapse either into a generic failure.

The baseline manifest must itself be versioned and cited. A digest map that is not committed is another trust claim.

## Re-examination condition

Re-examine this rule before accepting any of these changes:

- the autofix hook begins changing non-terminal whitespace, JSON structure, or string content;
- receipts move to a format whose canonicalisation is not defined;
- a receipt becomes intentionally byte-addressed, where terminal whitespace is evidence;
- the normalized digest has a collision or substitution finding;
- the integrity gate produces a drift without an accompanying raw-diff classification.

At re-examination, prefer raw-byte pinning if the hook has become stable and the receipt contract requires byte identity. If the lane cannot state a satisfiable normalization and repair path, mark the integrity gate HELD rather than silently returning to existence-only verification.

## Scope

This rule does not claim that the current `lane-status.sh` verifies integrity. It currently verifies existence only. It specifies the next instrument contract and keeps the distinction explicit until implementation lands.
