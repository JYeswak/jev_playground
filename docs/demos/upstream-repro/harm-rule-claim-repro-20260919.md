# Harm-rule headline claim reproduction

**Unit:** P2-25 Unit 1
**Verifier:** `work/omp-harm-rule/verify-claim.mjs`
**Source under test:** `work/omp-harm-rule/harm-rule.ts`

## Result

```text
node work/omp-harm-rule/verify-claim.mjs

shipped rule positive cases recoverable: 12/12
benign cases recoverable from committed corpora: 38/40
VERDICT: BLOCKED
```

The verifier imports the shipped rule's default extension entrypoint and drives its registered
`tool_call` handler. It does not copy or reimplement the regexes. It uses
`work/oracle-kit`'s `requireKey` and `inspectKey` for corpus field access.

Committed sources inspected:

- `work/toolcall-judge-v3/corpus-v3.json`: 12 eligible positive cases and 8 benign cases;
- `work/bicameral-gate/commands.json`: 20 benign cases;
- `work/bicameral-gate/heldout.json`: 10 benign cases.

The exact 40 benign cases behind the README's `0/40` headline are not recoverable from committed
files. The committed candidates total 38 after preserving corpus provenance. The head-to-head
receipt (`harm-rule-shipped-20260919.md`) reports the number but does not identify the 40 cases.

## Mutation negative

A temporary copy of `harm-rule.ts` with the `777` privilege regex mutated to `778` was run through
the same verifier:

```text
shipped rule positive cases recoverable: 10/12
```

The verifier detects a broken shipped-rule copy. The temporary copy was outside the repository.

## Verdict

**BLOCKED — exact corpus missing.** The README headline cannot be reproduced by a stranger from
committed artifacts. This is a corpus provenance defect, not a reason to invent two benign cases.

## NO-CLAIM

This unit does not establish the README's `0/40` false-positive result, the live Jev column, live
traffic precision, or any denominator beyond the 12 recoverable positives and 38 committed benign
candidates. The existing README table remains unverified until the missing exact benign corpus is
committed.
