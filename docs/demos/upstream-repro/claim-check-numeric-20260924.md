# Does an exact-value question catch a changed number? The R83 retry (bead `jev-2mp`)

ClaimCheckTool (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**Why.** `NEGATIVE_EVIDENCE.md` R83: asked "does the evidence support the claim?" over whole close
reasons, `jev_claim_check` caught 0 of 31 changed numbers and approved 4, including `75/219 ->
35/219` at p 0.91 against evidence that says `75/219` three times. R83's retry condition names two
changes, and this unit makes both: one number per check, and a question that asks for the exact value.

**Instrument.** `work/jev-claim-check/numeric.mjs` (rules in its header). For every number in a
claim, one Noul over state `{clause, value, evidence}`: instructions *"Does the evidence state the
exact value `value` for what `clause` says it measures?"*, criteria `true`: *"The evidence states this
same value for this quantity. A shorter rounding of the evidence's value, or the same value written
as a fraction, percent or decimal, also counts"*, `false`: *"The evidence gives a different value for
this quantity, or does not state it"*. The clause is the claim unit holding the number (split at
sentence ends, `; `, `, `, ` (`, `)`), widened backwards to at least 4 words. Per-check verdict uses
the tool's cuts (supported >= 0.8, unsupported <= 0.2). A whole claim is supported when every check
is, unsupported when any check is.

**Sets**, taken verbatim from files already committed:
- **readme**: the 19 true README claims of `jev-sp5` (`cases.jsonl`) with their frozen evidence. One
  (`official-sdk`) has no number, so 18 have checks.
- **close**: the 34 real close reasons of `jev-10t` that carry evidence (`close-cases.jsonl`). Two
  have no number.

**Fresh plants.** Drawn by `numeric.mjs --build` with seed 20260925 (mulberry32), one per claim that
has an eligible number (any token except a bare 0 or 1). The draw is uniform over eligible numbers
that occur in the evidence, else over all eligible numbers. The drawn number's first non-zero digit
run has its last digit changed (1->5 ... 9->4, 0->4). These plants are nearer the original than
jev-10t's: `75/219 -> 79/219`, `0.0614 -> 0.0618`, `189 -> 184`. The build refuses a plant equal to
any jev-10t plant or diagnostic clause. readme: 18 plants, all 18 with the original number in the
evidence. close: 31 plants, 25 with it in the evidence. `numeric-cases.jsonl` sha256
`dbaafe7f4a0564c1e634ba468ca5824ba7ce04486a1d0e67f1e88f811c4ca379`, 314 distinct checks to ask.

**Bar** (`work/jev-claim-check/score-numeric.py`), in EACH set over its n plants:

| # | Metric | readme (n=18) | close (n=31) |
|---|---|---|---|
| a | the planted number's check called `supported` | <= 1 | <= 3 |
| b | the planted number's check called `unsupported` | >= 11 | >= 19 |
| c | the original number's check (same position, real claim) called `supported` | >= 11 | >= 19 |

(10% floor, 60% ceil, 60% ceil.) **PASS** = all three in both sets. Always-`supported` fails (a) and
(b); always-`unsupported` fails (c). Whole-claim verdicts are reported descriptively, and every real
claim called unsupported as a whole is read against its evidence and classed: the claim is wrong, the
number is absent from the resolved evidence (resolver or registry gap), the check misread it, or the
value is not a measured quantity (a sample size, a seed, a count of calls).

**If PASS**, `jev_claim_check` gains a numeric mode with L0 tests. **If FAIL**, R83 is updated with
this result. The question, cuts and clause rule are not retuned after an answer.

**Stated before running:** 314 Jev calls, sequential.

**NO-CLAIM.** One wording, one Jev version, one run, plants from a one-digit rule. The close set's
labels assume the reasons are right; a real check called unsupported is read, not scored as an
error. The numberTokens rule reads `3.0e-09` as `3`, and such checks stay in as built.
