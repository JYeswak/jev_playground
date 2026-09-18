# Q21 Rule: Integer Score Prose

**Decision:** retire integer score prose as a state-of-record surface. Do not build a second score watcher over PLAN.md/RULING.md.

## Finding

The available history proves **zero verified upward integer-prose moves for the same candidate**. It does not prove that no such move ever occurred.

The trace is bounded, not exhaustive:

- Q64's 69-commit PLAN audit is complete for `mean <decimal>` lines: 0 modifications, 0 upward, 0 downward.
- Q63/audit-score-lineage is complete for the STATUS table: 7 score changes, 0 upward across 33 STATUS-touching commits.
- Integer prose (`score 905`, `820 non-author`, `re-scored`, `repriced`) is not a stable identity-bearing syntax. It appears in prose, quotations, grouped ranges, corrections, stale historical sections, and reflowed paragraphs across PLAN.md and RULING.md.
- A history scan found no verified same-candidate upward transition, but cannot establish a finite upper bound on unobserved transitions without a per-candidate prose schema. The honest bound is: **verified upward moves = 0; untraceable candidates/events = unknown**.

The known concrete failure is staleness in the retired decimal surface: demo-7's old mean remained after repricing. That is not evidence of integer upward smuggling.

## Does Q64's retirement reasoning transfer?

**Yes for authority; no for the failure mode.**

The authority reasoning transfers exactly: `STATUS.tsv` is the sole state of record for score and rank. A number in prose cannot change a candidate's score, cannot trigger a lineage gate, and must not be used to claim a current rank unless it points to the authoritative STATUS row.

The observability reasoning does not transfer cleanly. Decimal mean headings had a stable heading shape and a bounded 69-commit audit. Integer prose has no equivalent stable identity: `905` can be a current score, a quotation of an old score, an example, a grouped range, a correction, a non-author score, or a number belonging to another candidate. Mechanising it as a regex would recreate the label-defining-regex defect that made COD-H2 rung 4 UNASKABLE.

Therefore the correct action is retirement, not a weaker regex watcher.

## Rule

1. `STATUS.tsv` is authoritative for candidate score and rank.
2. Integer score prose is historical/context annotation only.
3. A prose score may be cited only with an explicit candidate name and a STATUS receipt/path or revision that establishes its temporal meaning.
4. Prose integer claims must never feed promotion, lineage, score-change, or rank gates.
5. A stale or contradictory prose integer is a documentation defect, not a score event. Correct it or strike it when the owning document is next edited; do not rewrite old prose solely to make it agree with current STATUS.
6. Grader spread, disagreement, and per-rater scores remain valid context when they are explicitly identified as context rather than the candidate's authoritative score.

## Re-examination condition

Re-examine this retirement if any of the following occurs:

- a commit uses an integer prose assertion to change a candidate's score or rank without a STATUS change;
- a gate or receipt begins consuming integer prose as a decision input;
- a future lane gives prose score claims stable candidate IDs, receipt pointers, and temporal versioning;
- a documented audit finds a same-candidate upward integer-prose move that affected an outcome;
- STATUS stops being the authoritative score/rank table.

At re-examination, first add a structured receipt/type field to the authoritative state. Do not revive filename or prose regex inference as a fallback.

## Scope

This ruling claims no upward integer-prose move was verified, not that exhaustive historical tracing is possible. It does not alter the measured STATUS result of 7 score changes, 0 upward, or Q64's decimal-mean result of 0 modifications.
