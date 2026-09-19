# Q77 Specification: `other_reason` Metadata

**Decision:** use a versioned sidecar, not STATUS column 11.

`other_reason` does not affect score-lineage routing: every `other` value is non-score. Adding a STATUS column would impose a schema migration and consume the parser's one-column migration budget for metadata that the gate does not need. The reason is valuable for audit and vocabulary review, so preserve it in a sidecar with exact receipt binding.

## Location

Create and version:

```text
docs/demos/duel-2/runs/receipt-other-reasons.json
```

This is documentation/provenance metadata, not a lane-status column and not a gate input. It may be replaced only by an explicit versioned sidecar revision; history remains in git.

## Sidecar schema

```json
{
  "schema": "jev.receipt-other-reasons.v1",
  "status_source": "docs/demos/STATUS.tsv",
  "entries": [
    {
      "candidate": "demo-3-claim-check-gate",
      "receipt": "docs/demos/duel-2/BASELINE_claimcheck_vs_jev_COD.md",
      "receipt_digest": "<content-normalized sha256>",
      "receipt_type": "other",
      "other_reason": "design",
      "evidence": {
        "path": "docs/demos/duel-2/BASELINE_claimcheck_vs_jev_COD.md",
        "locator": "status/design section",
        "explanation": "comparison design, not implementation or benchmark result"
      },
      "assigned_by": "<opened-content auditor>",
      "assigned_at": "<UTC timestamp>"
    }
  ]
}
```

Allowed `other_reason` values:

```text
design | mapping | unresolved | mixed
```

The three current entries are:

- demo-3 → `design`;
- MU-H2 → `design`;
- COD-H2 → `mapping`.

## Verification contract

A future `receipt-other-reasons-check` verifier must:

1. Parse `STATUS.tsv` using the exact current column count; do not infer from filenames.
2. Select rows whose declared `receipt_type` is `other`.
3. Require exactly one sidecar entry keyed by `(candidate, receipt path, receipt_digest)` for each such row.
4. Reject missing, duplicate, or extra entries.
5. Require `other_reason` to be in the controlled vocabulary.
6. Open the referenced receipt and verify its current content-normalized digest matches the sidecar and STATUS binding.
7. Verify the evidence locator and explanation support the reason from content. A path or filename alone is not evidence.
8. Report unresolved `other_reason=unresolved` without converting it to another type.

A sidecar mismatch is a metadata/audit failure. It must not turn an `other` receipt into a score receipt or alter the score-lineage gate's non-score behavior.

## What this enables

Today the gate can answer only the necessary question: `score` versus non-score. The sidecar adds capabilities the gate does not need:

- a verifier can reproduce why each `other` assignment was made;
- vocabulary review can count design, mapping, unresolved, and mixed separately;
- a receipt mutation is detected through the digest binding;
- a future enum decision can be based on opened-content evidence rather than filename frequency;
- auditors can distinguish “deliberately other” from “typing unresolved.”

The sidecar does not claim a new gate branch, change STATUS ordering, or make `other` semantically equivalent to any new enum value.

## Why not column 11

Column 11 is structurally possible after the current ten-column migration, but it is the wrong boundary:

- the score-lineage gate does not route on `other_reason`;
- a column would force every parser and fixture through another schema migration;
- sidecar entries can be added without changing the gate's fail-closed score/non-score contract;
- exact receipt digests prevent sidecar drift from silently changing a reason;
- a future need for routing can promote the metadata into a deliberate schema migration with new arms.

## Re-examination condition

Re-examine the sidecar boundary when:

- a gate needs different behavior for `design`, `mapping`, or another `other_reason`;
- sidecar coverage falls below 100% of `other` rows;
- `mixed` becomes a dumping ground or exceeds 25% of `other` rows;
- an `other` reason is repeatedly used to conceal an actually score-bearing receipt;
- receipt digests or evidence locators cannot remain stable;
- a new receipt type is supported by enough opened examples to justify a pre-registered migration.

Only then add a STATUS column or enum value, with exact-width parser validation, migration arms, and a declared retyping owner.

## Scope

This is a documentation/provenance specification. It does not implement the sidecar, alter STATUS.tsv, or change score-lineage behavior.
