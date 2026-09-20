# A12 local-refusal prototype — 2026-09-20 `[pending]`

**Verdict: REFUSE** (F1: refused-Y1 2 ≥ refused-empty 2). Stands on a
second leg too: R fires on the slice regex, not on the condition — fitted
to the 16 rows that motivated it, the mention-vs-use defect in policy form.

Falsifier pre-registered at `60bc0ce`
(`a12-refusal-falsifier-20260920.md`) before `score_a12_refusal.py`
existed. Corpus: locked `exports/cass-dig-rows.jsonl` +
`exports/cass-dig-hits.jsonl` (n=138; 4 known empty-success rows).
Rule R: refuse dig iff `hit_count>0` AND query matches absence-claim shape
AND top snippet lacks a query token near an error literal / in backticks.

## Counts

| | |
|---|---:|
| refused empty (of 4) | 2 — `no such field`, `no such key` |
| refused Y1 (good digs killed) | 2 — `field does not exist`, `missing field` |
| kept Y1 digs | 20 |
| R loss on absence slice (n=13) | 0.154 vs dig-iff 0.308 |

## Reading

- F1 fires exactly at the tie boundary (2 ≥ 2): R catches half the empties
  at the price of killing two good digs. No trade to ship.
- The R-loss halving on the absence slice is discounted to zero: R's
  condition-2 is the same regex family that defined S_wrong_selector, so a
  win there would be fitted, not generalizing. A shippable refusal must
  fire on the CONDITION (hits exist AND nothing Y-eligible, graded from the
  hits) — and on this export the only row-level eligibility proxy at hand
  (`n_receipt_shaped`) is maxed (10) on all 4 empties, i.e. refuted as a
  separator. No eligible-grader exists in these columns; building one needs
  snippet reads at run time, unproven here.
- Y-eligibility grading from hits remains the open piece of A12. It is not
  in this export's columns and cannot be tuned into it.

## NO-CLAIM

Post-hoc predicate (authored after eyeballing heads), stated in falsifier.
Locked export, unregenerated. Snippets truncated at 800 chars. No rebuild
started. Not a promotion (`promoted = 0`).
