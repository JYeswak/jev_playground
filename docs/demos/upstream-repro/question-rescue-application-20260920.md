# Question rescue application — holdout-aware ship

**Unit:** P2-39
**Holdout evidence:** `docs/demos/upstream-repro/question-shape-20260919.md` at `c6b77b8`

## Shipped rescues

### `omp-jev-rerank`

Applied the measured `noise` and `definitional` rescues. The committed-case rerun was 12/12 over
the original four cases. Pane3's fresh holdout was 8/8 for `noise` and 6/8 for `definitional`; the
two definitional misses were boundary cases where the definition sat at index 3 rather than in the
first three. The README calls out that holdout sensitivity and that overfit is not ruled out.

### `omp-jev-failure`

Applied the rescued `argument` wording. The committed-case rerun was 8/11. Pane3's fresh holdout
was 6/7 with spread 0.83; the one miss tied a stale-hash rejection to the invocation. The README
states the wording did not stabilize the question; near-threshold behavior remains.

### `omp-jev-dispatch`

The `destructive` rescue was **not shipped**. Pane3's fresh holdout refuted it: 6/7 while answering
NO on all seven packets, including the true case at 0.32. The original question remains in source.
The dispatch README records the failed rescue and keeps the extension below-chance / not-shipped.
`unverifiable` and `leading` remain untouched.

## Verification

- rerank measure: 12/12 committed cases;
- failure measure: 30/33 total, 8/11 argument;
- dispatch measure after attempted polarity rescue: 8/15, rescue refuted;
- rerank and failure offline tests passed; no test files changed, so TESTS.md required no update;
- no destructive rescue was allowed to remain in the tree.

## NO-CLAIM

The rescues were validated on hand-built or same-case inputs plus the cited pane3 holdout; overfit is
not ruled out. No live-traffic accuracy, calibration, or production capability claim is made.
