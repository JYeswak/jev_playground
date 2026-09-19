# Q75 Rule: Keep `other` Until Routing Needs Split Types

**Decision:** do **not** add `design` and `mapping` to the `receipt_type` enum yet. Keep `other` legal and fail-closed, and require an explicit `other_reason` annotation for auditability.

## Evidence

Q73 independently found three `other` rows out of 17:

- demo-3: design
- MU-H2: design
- COD-H2: mapping

That is 3/17 = 17.65%, rounded to 18%. The finding is real: these are recurring speech acts, not random malformed receipts. But they are all non-score for the only currently load-bearing gate: score-lineage must distinguish `score` from everything that is not a score. Both `design` and `mapping` safely route to non-score today.

Adding enum values now would improve analytics but would not improve the gate's safety. It would add two assignments that themselves need validation, migration, and future re-examination. A growing enum that names every document purpose can become another label surface without changing the decision boundary.

## Rule

The closed `receipt_type` enum remains:

```text
score | hold-resolution | verdict | measurement | other
```

`other` is valid only when:

1. the receipt was opened;
2. its primary speech act is not score, hold-resolution, verdict, or measurement; and
3. the producer or non-author maintainer records a non-empty `other_reason` from this controlled vocabulary:

```text
design | mapping | unresolved | mixed
```

`other_reason` is metadata, not a new gate type. It must never be inferred from the filename. The score-lineage gate treats every `other` value as non-score, while audits retain the reason for future vocabulary decisions.

## Existing-row migration

No `receipt_type` migration is required for the three existing `other` rows: they remain `other`.

Add the reason at the receipt metadata/audit layer from opened content:

- `BASELINE_claimcheck_vs_jev_COD.md` → `other_reason=design`;
- `BASELINE_MU-H2_vs_incumbents_COD.md` → `other_reason=design`;
- `label-id-mapping-20260918T073641Z.json` → `other_reason=mapping`.

Do not alter the gate's binary score/non-score behavior to make these rows pass a different branch. Do not backfill the reason from filenames. If a producer cannot establish the reason, use `unresolved`, not the nearest plausible type.

## Why not extend now

- The current evidence shows vocabulary incompleteness, not gate ambiguity.
- `other=3/17` is high enough to preserve a reason field and monitor, but not evidence that design and mapping need distinct gate semantics.
- `other` is the safer fail-closed fallback for unknown future receipt purposes.
- Extending the enum would require retyping and validating every affected row, plus new positive/negative gate arms, for no current decision change.
- Q19's rule already requires a closed enum and fail-closed unknown handling; this ruling avoids turning every taxonomy refinement into a gate migration.

## Re-examination condition

Reconsider adding `design` and `mapping` when any of the following occurs:

- a gate routes design and mapping differently;
- `other` exceeds 25% of typed rows, reaches five rows, or grows across two consecutive migrations;
- two `other_reason` values acquire different required fields, verification paths, or failure codes;
- an `other` receipt is incorrectly accepted as a score because the non-score boundary is no longer sufficient;
- a new recurring speech act cannot be represented by `other_reason` without `mixed` becoming a dumping ground;
- the full 17-row migration is complete and a new receipt corpus supplies enough examples to test the split.

At re-examination, add the enum values and selftests in one schema migration. Require opened-content evidence for every retyped row and preserve `other` for genuinely unresolved cases; never replace it with filename inference.

## Scope

This is a taxonomy ruling, not an implementation claim. The current gate remains correct for score versus non-score if `other` is treated as non-score and carries a reason. The vocabulary is intentionally monitored rather than prematurely expanded.
