# Level vocabulary confusion matrix — 2026-09-20 `[pending]`

Mechanical re-label of 1,043 commits (1,040 non-merge + 3 new) under the
proposal (`receipt` for docs-only; strong words require runnable change).
Dataset regenerated: `node work/commit-mine/mine.mjs` (~13s, read-only).
`mutation` (2) and unlevelled (1) kept as-is, outside the proposal.

## Matrix (old → proposed)

| old | keep | → receipt |
|---|---:|---:|
| live (210) | 87 | 123 |
| oracle (97) | 19 | 78 |
| test (494) | 305 | 189 |
| selftest (30) | 23 | 7 |
| pending (209) | 48 | 161 |

**Moved: 558/1,043 = 53.5%.** Exceeds the ~40% bar: the proposal as a
re-label is a rewrite of the past, not a fix for the future. Preferred:
add `receipt`, bind going forward, grandfather history. The hook's
`[receipt-candidate]` refusal tonight (conductor's own commit) proves the
vocabulary gap live: the most common thing we commit has no word.

## NO-CLAIM

Mechanical path-based rule; "runnable" approximated from
has_script/has_fixture/non-docs-non-test paths — "claim produced by
running" is not mechanically checkable and the matrix does not try.
test/selftest-no-test-path commits kept (grandfathered) per the
mention-vs-use correction: `[test]` describes verification performed.
