# Harm-rule claim reproduction

**Unit:** P2-26 Unit 1
**Verifier:** `work/omp-harm-rule/verify-claim.mjs`
**Source under test:** `work/omp-harm-rule/harm-rule.ts`

## Published result

```text
node work/omp-harm-rule/verify-claim.mjs

shipped rule recall: 12/12
shipped rule false positives: 0/38
corpus provenance: 12 positives and 38 committed benign cases
VERDICT: REPRODUCIBLE COMMITTED CORPUS
```

The verifier imports the shipped rule's default extension entrypoint and drives its registered
`tool_call` handler. It does not copy or reimplement the regexes. It uses `work/oracle-kit`'s
`requireKey` and `inspectKey` for corpus field access.

## Corpus provenance

The committed corpus assembled by the verifier is:

- `work/toolcall-judge-v3/corpus-v3.json`: 12 eligible positive cases and 8 benign cases;
- `work/bicameral-gate/commands.json`: 20 benign cases;
- `work/bicameral-gate/heldout.json`: 10 benign cases.

The exact two historical benign cases behind the original `0/40` figure were not recovered from
committed files or git history. They are not silently reconstructed. The published deterministic
rule claim is corrected to `0/38`, the denominator that the verifier actually reproduces.

The Jev `11/12` and dumb-baseline `5/12` rows remain historical measurements. They are not rerun
by this offline verifier and retain their historical `0/40` notation only as historical receipt
figures, not as current reproducibility claims.

## Mutation negative

A temporary copy of `harm-rule.ts` with the `777` privilege regex mutated to `778` was run through
the same verifier:

```text
shipped rule recall: 10/12
```

The verifier detects a broken shipped-rule copy. The temporary copy stayed outside the repository.

## NO-CLAIM

This proves only the shipped rule's `12/12` recall and `0/38` false-positive result on the
committed corpus. It does not recover the two missing historical cases, rerun live Jev, establish
live-traffic precision, or support any denominator beyond 38 benign cases.
