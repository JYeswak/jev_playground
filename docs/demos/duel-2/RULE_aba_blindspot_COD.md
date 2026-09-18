# Q98 Rule: A→B→A Blindspot

**Decision:** close the A→B→A residual as negligible for this lane. Do not add a filesystem watcher or polling loop.

## What is and is not covered

A before/after fingerprint detects a durable change between the two observations. A private snapshot additionally makes the verifier's read internally consistent. Neither is a history watcher: a file can move A→B→A entirely inside the observation window and leave equal endpoint hashes.

This is a real theoretical blindspot, not an absent class.

## Producer plausibility

A plausible producer exists: an autofix/formatter, a pane edit, or a human can rewrite a JSON/TSV file and restore it before the scan's final fingerprint. A sibling's repair attempt could also write a temporary form and restore the original. The Q93 syntax-error witness proves shared mutation during a gate run is not hypothetical.

The missing piece is not plausibility; it is durable value. An A→B→A mutation leaves no source-state difference for a before/after verifier to report. If the verifier reads B, the Q99 private snapshot plus source recheck catches a snapshot/source mismatch when the final source is A. If it copies A or runs entirely before/after the mutation, the mutation did not affect the verified snapshot. A watch would detect activity, but not improve the correctness of a stable snapshot without becoming a new always-on subsystem.

## Ruling

Close as **CLOSED-AS-NEGLIGIBLE-CURRENT-LANE**:

- no filesystem watch;
- no unbounded polling;
- no attempt to reconstruct edits that left no durable evidence;
- private snapshot/source binding remains the remedy for the material intra-scan consistency risk.

This closure must not be phrased as “A→B→A cannot happen.” It means the lane does not pay for a watcher whose only output would be a transient event with no durable state to audit.

## Re-examination condition

Re-open this ruling if any of these occurs:

1. an A→B→A mutation is observed to change a verifier result or cause a snapshot/source mismatch;
2. a production tool intentionally performs reversible writes during the verifier window;
3. a foundation consumer requires a complete mutation history rather than a stable snapshot;
4. a bounded, low-cost event source becomes available without a resident watcher or shared-worktree interference;
5. repeated transient reports show that endpoint equality is hiding operationally meaningful edits.

A re-opened design must first prove the event has decision value, then compare a bounded journal/event counter against a watch. “Warn on every write” is not an acceptable default.

## Scope

This is a cost-and-evidence closure, not a correctness proof that no ABA mutation occurs. It leaves Q99's snapshot manifest as the required material consistency mechanism.
