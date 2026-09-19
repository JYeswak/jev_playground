# OMP observer cost sentinel cleanup

**Unit:** P2-33
**Source:** `work/omp-jev-observer/src/observer.mjs`
**Commit:** pending at receipt authoring

## Change

Decision records now omit `costUsd` when the classifier result does not provide a cost. A reported
numeric cost, including a measured zero, remains present. The classifier error path now omits cost
as well: failure provides no measured spend, so storing `0` would understate downstream totals and
make failure indistinguishable from a genuinely free call.

The other five STORED sentinel hits from P2-32 are out of scope for this unit: they are in probes,
an eval report, and an adapter normalizer rather than the shipped observer artifact.

## Negative arm

The existing seven observer tests were extended with a missing-cost arm and an error-cost arm. The
missing-cost arm would have been green under `costUsd: result.costUsd ?? 0`; it now asserts the
record omits `costUsd`. The error arm makes the same assertion for failed classification.

```text
node --test work/omp-jev-observer/test/observer.test.mjs
8 tests passed
```

## NO-CLAIM

Offline change only. No live-traffic, working-profile, precision, or rate claim. Promoted remains
zero. Cost absence is now distinguishable from measured zero in the observer decision schema.
