# Q19 Rule: Declared Receipt Types

**Decision:** replace filename inference with a declared `receipt_type` field in the status schema. `SCORE_RECEIPT` must stop being a regular expression over filenames.

## Minimal vocabulary

`receipt_type` is a closed enum:

- `score` — the cited artifact records or adjudicates a candidate score/rating, including a score matrix, demand score, hunt score, or rung-2 score;
- `hold-resolution` — the cited artifact resolves, discharges, or changes the prerequisite that held a candidate, without itself changing the candidate score;
- `verdict` — the cited artifact changes or records a candidate verdict without being a score receipt;
- `measurement` — the cited artifact reports a measured result used by a gate but is not itself a candidate score;
- `other` — a cited receipt that does not fit the preceding operational classes.

The vocabulary is intentionally semantic and closed. Adding a new type requires changing the schema, parser, and selftests together. A filename is never evidence of a type.

## Assignment and timing

1. The **receipt producer** assigns `receipt_type` when the receipt is written. The type belongs in the receipt's top-level machine-readable metadata, next to its schema/version, not in prose alone.
2. The **status-row author** copies that declared value into `STATUS.tsv` in the same change that cites the receipt. Copying is a consistency check, not an inference.
3. `audit-score-lineage.sh` reads only the status-row field. It may verify that the receipt exists and, when implemented, that the receipt's embedded type matches the row. It must not derive type from the path, filename, commit message, or nearby prose.
4. A score change whose row does not have a declared type is a schema failure, not evidence that the receipt is a non-score receipt.

This separates authorship from classification: the producer knows the receipt's purpose; the status maintainer binds it to the row; the gate observes the declaration.

## Empty values and fail-closed behavior

An empty field, missing column, `unknown`, or value outside the enum means **receipt type unresolved**. It is not equivalent to `other` and it is not equivalent to `hold-resolution`.

The score-lineage gate fails closed on unresolved type:

```text
score delta + verdict change + any unresolved receipt_type
    => SCHEMA_ERROR / HOLD, not a clean result
```

The gate must print the affected candidate and row, and return a distinct schema-error code. It must not silently convert an empty value into a non-score value, because that would recreate the permissive under-fire defect under a new spelling.

This is the same safety posture as `kill_concurrence`: absence is not permission. A deliberately non-scoring receipt must state `hold-resolution`, `verdict`, `measurement`, or `other` explicitly.

## Column position

Append `receipt_type` as **column 10**, after the current `receipt_digest` column:

```text
candidate  rung  score  verdict  author  receipt  blocked_on  kill_concurrence  receipt_digest  receipt_type
```

Do not reuse or reorder column 8. The lane already has a column-8 collision history around `kill_concurrence`; append-only migration preserves positional meaning and avoids another shared-worktree overwrite. The header must be updated in the same schema migration. Parsers must require exactly 10 fields for data rows after the migration and must preserve empty fields while reporting them as schema errors.

## Migration of the 17 existing filename-inferred rows

Do **not** backfill `receipt_type` from filenames. That would reproduce the exact `SCORE_RECEIPT` label-defining-regex defect R17 is removing.

Perform the migration in two explicit steps:

1. Add column 10 and write `unknown` for every existing row whose type has not been declared. Commit the schema migration. The instrument must report those rows as unresolved and must not claim a clean score-lineage result.
2. For each cited receipt, its producer or an identified non-author maintainer opens the receipt and records one enum value with a source path/field and revision. Update the receipt metadata and STATUS row together. A missing producer is not permission to infer the type; leave it `unknown` and keep the gate held.

The current 17 rows may be manually classified only from opened receipt content and explicit authorship evidence. A filename-shaped classification is invalid even when it happens to be correct. Until all rows that participate in score-lineage comparisons are typed, historical “0 trips” is a partial result with `schema_incomplete`, not a clean pass.

## Re-examination condition

Re-examine this rule when any of these occurs:

- a new receipt purpose cannot be represented by the enum;
- a receipt's declared type disagrees with the STATUS row;
- a score delta or verdict change reaches the gate with an empty/unknown type;
- a receipt format changes and its top-level metadata is no longer machine-readable;
- all 17 legacy rows are typed and a history replay plus positive/negative selftests can prove the declared-type branch discriminates.

At re-examination, add the new type and fixtures before changing the gate. Never restore filename inference as a fallback.

## Scope

This rule closes the schema decision only. It does not claim that `audit-score-lineage.sh` already implements the ten-column schema, that the 17 rows are typed, or that the historical zero-trip result is fully integrity-checked.
