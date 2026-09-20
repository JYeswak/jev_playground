# Multiclass hold-out: both framings 8/9 with the SAME miss — structure holds, superiority does not (2026-09-19)

## Method

`work/omp-jev-failure/measure-multiclass-holdout.mjs` (beside the framing under test, not
in jev-client: this tests one unit's conversion, not wording guidance). Nine fresh
failures: six mined from a different session log (clutterfreespaces.ios 2026-08-29 —
four wrong paths, two infra timeouts) plus three produced in /tmp/mc-holdout (bad node
flag, failing assertion, TypeError on undefined). Binary = shipped question strings;
multiclass = FAILURE_QUESTION + FAILURE_CLASSES imported from src (shipped by
construction). Case-level scoring as in measure-multiclass.mjs. 9 x 2 x 3 = 54 calls,
zero errors, zero flips in either framing.

## Table (run 1; identical all three runs)

| case | expected | binary | multiclass |
|---|---|---|---|
| 4 mined wrong paths + bad flag | argument | 5 HIT | 5 HIT |
| grep-timeout | transient | MISS (argument) | MISS (argument, margin 0.90) |
| slb-timeout | transient | HIT | HIT (margin 0.96) |
| assert `2 !== 3` | bug | HIT | HIT (margin 1.00) |
| map of undefined | bug | HIT | HIT (margin 0.98) |
| totals | | 8/9, no incoherent rows | 8/9, DROP 11/11→8/9 |

## Reading

The conversion is NOT earned by accuracy: multiclass holds (one-case DROP) but binary
holds equally, with zero incoherent rows on these nine — the structural defect the
conversion removes did not fire here. What the hold-out supports is narrower: multiclass
is no worse, cannot go incoherent by construction, and decides at margins 0.90–1.00 with
zero drift. That is a robustness argument for the conversion, not a superiority result.

The shared miss is the most honest cell: grep-timeout judged argument by both framings at
high margin. My transient label is disputable — the invocation supplied an over-broad
path and the error tells the caller to change it, so "wrong invocation" is a defensible
reading and both framings agree with each other against me. A label both framings reject
is evidence about my label, not about either framing. The set contains no genuinely
mixed cause (flaky dependency exposed by a real bug), in either framing, by anybody.

## NO-CLAIM

Nine cases, six selected for legibility and three produced knowing the answer; no mixed
causes; single session log plus /tmp. This earns conversion consideration on robustness
grounds, not conversion. src/index.ts unchanged.
