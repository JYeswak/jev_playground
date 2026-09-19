# Reconcile C5 With Preview Sufficiency

**Status:** COD-H2 phase-1 seam ruling
**Decision date:** 2026-09-18
**Inputs:** `preview-sufficiency-20260918T065500Z.json`, `CLAUSE_locally_reversible_COD.md` at `50b0a67`, and `verifiable-labels-mu-clause-20260918T074520Z.json`

## Decision

Both artifacts yield, but in different respects.

1. The Q44 preview-sufficiency predicate yields as a **complete evidence test**. It measures whether the preview contains the token used to assign the corpus stratum. It does not prove that the clause can locate every deletion operand or establish C5.
2. The Q52 clause yields only in its **input description**: C5 must not be read as “the 160-character preview is the evidence.” C5 requires a complete evidence span, either in the manifest or in a relocatable full command. A preview may be a useful index, never the authoritative evidence object.

The operational precedence is:

```text
manifest evidence span / relocatable full command
    -> C5 scope-and-operand check
    -> clause outcome

preview-sufficiency predicate
    -> tells whether stratum-assignment evidence is visible
    -> does not override C5
```

Therefore a case can pass Q44 sufficiency and fail C5. That is not a contradiction after the scopes are separated; it is a false equivalence between “stratum token visible” and “clause evidence complete.”

## The fresh-20 finding

L15 is a genuine C5 failure at the seam:

- Pane 3 relocated full commands for 18/20.
- L15 was not relocatable despite the journal being present; the turn held 15 bash calls and no prefix matched because of compaction/rewrite drift.
- Its preview was truncated before the complete deletion evidence.
- The clause correctly withheld it because C5 could not establish all operands from an authoritative span.

“Verifiable sample” therefore meant identity and draw reproducibility, not that every command remained independently verifiable after journal drift. The sample-file claim and the C5 evidence claim must not be conflated.

## Full-68 scale

Q44 measured:

| stratum | n | preview-insufficient | unrelocatable |
|---|---:|---:|---:|
| ambiguous-authority | 50 | 36 | 2 |
| disallowed-destructive | 8 | 4 | 0 |
| reversible-safe | 10 | 0 | 2 |
| **total** | **68** | **40** | **4** |

The exact C5-specific count is **not present in the Q44 artifact**. Its `insufficient` field aggregates failure to show the stratum-assigning token; it does not record whether a deletion operand was hidden. It would be fabricated to call all 40 C5 failures.

The defensible quantitative statement is:

- **Observed C5 failures:** 1/20 (L15).
- **Full-68 evidence-risk upper bound:** 40/68 preview-insufficient cases, plus 4 separately unrelocatable cases; at most 44/68 cannot be closed from the preview/relocation artifacts alone.
- **Exact C5 failures across 68:** unknown; Q44 must be re-emitted with a C5-specific field to distinguish hidden scope operands from other missing stratum tokens.
- **Reversible-safe-only observation:** 0/10 preview-insufficient, but 2/10 unrelocatable; this does not make the overall clause evidence-complete because ambiguous cases can still enter the deletion clause.

Thus the manifest is a **precondition for non-nagware operation from committed artifacts**, not because all 40 necessarily fail C5, but because the existing artifacts cannot distinguish the C5 subset. A manifest with per-case evidence spans can turn the 40-case upper bound into an exact C5 result. The span must include the target and every operand needed for C1; a hash alone or a truncated preview does not suffice.

## Required artifact correction

Rename the semantic role of Q44 from “preview sufficiency” to **stratum-token visibility**. Preserve its counts, because they remain useful, but add per-case fields:

```json
{
  "preview_contains_stratum_token": true,
  "evidence_span_present": true,
  "evidence_span_complete_for_c5": false,
  "c5_failure_reason": "truncated_before_operand|unrelocatable|missing_span|null"
}
```

The Q52 clause remains the authority for outcomes. C5 passes only when `evidence_span_complete_for_c5` is true. If the field is absent, the outcome is withhold for an otherwise potentially reversible deletion; deterministic destructive or external operations still escalate.

## Ruling

The two-artifact contradiction is resolved without hiding the seam:

- Q44 yields on the claim that preview sufficiency proves clause sufficiency.
- Q52 yields on the implication that a preview can substitute for an evidence span.
- The manifest work is a dependency for closing C5 from committed artifacts, not a parallel convenience.

This closes the lane's reconciliation only. It does not claim a full-68 C5 count, agreement, or rung-4 validity.
