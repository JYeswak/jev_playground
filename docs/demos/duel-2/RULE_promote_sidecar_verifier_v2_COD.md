# Q97 Rule: Sidecar Verifier Promotion v2

**Decision:** do **not** promote `verify-other-reasons.sh` yet. The precondition is only partially met.

## Four-condition matrix

| Q89 precondition | Status | Evidence / gap |
|---|---|---|
| Stable copy/snapshot contract | **NOT MET** | The verifier's selftests use copies, but the live verifier still reads live STATUS/sidecar inputs. `lane-status.sh` now has bounded before/after fingerprints, but Q96 found it does not execute a private copy, lacks normalized hashes, and hardcodes the canonical sidecar path. Its transient primitive is not integrated into the verifier. |
| Revision/hash pair | **PARTIAL** | Sidecar/live/STATUS digest checks and STATUS pins exist, but there is no shared snapshot manifest binding the exact input set to one revision/hash pair. A live read can still mix revisions. |
| Copy-based known-good/bad arms | **MET** | `selftest-other-reasons.sh` has six copy-based arms and runs through stage 80's hermetic wrapper without mutating the real STATUS or sidecar. |
| `TRANSIENT_UNSTABLE` distinct from durable RED | **NOT MET** | Exit 10 exists in `lane-status.sh`, but `verify-other-reasons.sh` has no transient class. A sidecar verifier RED cannot currently distinguish a durable metadata defect from a peer's partial edit. |

Promotion requires all four, not two of four. The verifier remains hand-run.

## Why lane-status does not transfer the precondition

The lane-status transient implementation is useful evidence and should eventually protect its own receipt/schema/integrity claims. It does not automatically make the sidecar verifier safe:

- it fingerprints a hardcoded sidecar path rather than the verifier's `JEV_SIDECAR` input;
- it hashes live inputs before and after instead of validating a private copy;
- it returns transient state at the lane-status edge, while the verifier still returns only durable-style pass/fail codes.

Sharing the existence of exit 10 is not sharing the snapshot contract.

## Remaining implementation contract

Before promotion, the verifier needs:

1. explicit `JEV_STATUS` and `JEV_SIDECAR` inputs;
2. a wrapper that copies STATUS, sidecar, and referenced receipts into one private snapshot;
3. source revision plus per-file raw/normalized hash manifest;
4. post-copy source stability check with a maximum of two captures;
5. verifier result fields `snapshot_stable`, `capture_attempts`, `snapshot_id`, and `source_manifest_sha256`;
6. a distinct `TRANSIENT_UNSTABLE` result/exit code, not a durable RED;
7. copy-based arms for stable pass, stable durable RED, first-change recapture, and second-change transient;
8. a foundation wrapper that runs only against the stable snapshot and remains off the commit hook.

## Re-examination condition

Re-examine promotion when all four preconditions are demonstrated in one receipt and the following are true:

- a stable known-good copied pair passes;
- each durable bad arm fails with its durable reason;
- a peer-change arm returns `TRANSIENT_UNSTABLE` without a verifier verdict;
- a second unstable capture is bounded and names changed paths;
- no live shared path is read after the snapshot is declared complete;
- foundation execution remains explicitly non-commit-wired.

Do not promote because the current live sidecar run is green or because lane-status has exit 10. The verifier must own its own transient contract.

## Scope

This is a promotion ruling, not an implementation. The sidecar verifier remains hand-run; stage 80's hermetic selftest remains foundation-wired support evidence only.
