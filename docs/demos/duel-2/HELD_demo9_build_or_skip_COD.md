# Demo-9 build-or-skip decision

Status: **SKIP RUNG 3 NOW; HOLD, not RULED OUT.**
Candidate: Demo-9 continuous review signal.
Demand: reconciled 700 in the cross-score, but original non-author demand score 550 and the
candidate remains weak/held on the external-demand record.
Rung 2: CLEARED conditionally in `RUNG2_demo9_MU.md`; no implementation exists.

## Decision

Do not spend the next WIP slot building Demo-9 after COD-H2. The candidate is not rejected on taste
or on the existence of UBS. It is deferred because the cheapest honest rung-3 proof still needs a
labelled diff corpus, a six-dimension Jev runner, an install surface, and an arms-length comparison
against UBS, while the demand evidence remains contested and the measured superset is UNASKABLE.

This is a **HOLD/skip-now**, not a permanent kill. The retry condition is explicit below.

## What the thin proof would cost

A minimally honest Demo-9 build needs all of the following before it can answer “is this worth
running?”:

1. A clean-clone install command and an omp/CI-compatible advisory hook.
2. A pinned diff fixture with at least 20 labelled cases: safe changes, real regressions, pattern-
   detectable findings, design-coherence failures, intent mismatches, generated/unsupported files,
   and ambiguous cases.
3. Six Noul dimensions per attempted diff: correctness, complexity, changeability, modularity,
   tests, and security, with fixed reason codes and withhold paths.
4. A deterministic diff snapshot and receipt; no model-written prose review.
5. The existing four-file UBS baseline plus a positive-control defect and a reviewer-labelled
   actionability corpus.
6. A live or budgeted Jev run for approximately 20 × 6 = 120 dimension calls, plus retries/RED arms.

The first-run provider cost is not the constraint. At the measured Q23 input scale of roughly 435
input tokens per call and `$0.042/Mtok`, 120 calls are about `$2.19` before retries. The actual cost
will vary with diff context and batching. The expensive part is the labelled diff corpus, reviewer
agreement, hook wiring, and comparison analysis: conservatively **1–2 engineering days plus one
reviewer session**, not an afternoon-only proof.

The estimate is deliberately a price, not a claim that those calls or labels have happened.

## Existing baseline and what is still missing

The receipt cited by the lane reports a first-party UBS baseline over four TypeScript files:

```text
1 critical / 6 warnings / 27 info
```

with an `eval()` positive control proving UBS fires. That is useful baseline material, but it is not
a Demo-9 comparison because no Jev review-signal implementation exists and no human-labelled
actionability set exists.

The Demo-9 contract correctly narrows the possible wedge:

- pattern-overlapping findings must be reported separately from semantic dimensions;
- at least two non-pattern dimensions—design coherence and intent match—must be measured;
- advisory-only behavior is required until false-positive rate is published;
- no prose generation, no model-selected dimensions, and no diff-summary substitution.

A build that merely emits six probabilities beside the same UBS findings is an expensive echo, not a
proof of a strict superset.

## Why not build now

### Demand is not resolved

The candidate's original non-author demand score was 550 against a self-author score of 820. The
cross-score settled at 700, but explicitly held it pending an independent UBS blind-spot receipt and
a false-positive/actionability result. That receipt does not exist because the Jev implementation
does not exist.

The AI-code-review category is crowded, and CodeRabbit/Qodo/Greptile/Copilot Review are adjacent
commercial or platform baselines. Their existence does not structurally kill Demo-9, but it makes a
new local advisory hook pay for a differentiated result rather than for category familiarity.

### The WIP slot has a stronger measured path

COD-H2 has reached rung 3 and its implementation has a real request path, discriminating RED arms,
and a live provenance receipt, while Q29 has already designed the rung-4 measurement. Demo-9 has no
implementation and no live signal receipt. Spending the only WIP slot on Demo-9 now would reverse the
gauntlet's sequencing rule: pay for the higher-cost proof before the lower-cost demand/superset
question is answered.

## Retry condition

Re-open Demo-9 for a rung-3 build only when all conditions are true:

1. COD-H2's current WIP slot is closed or released.
2. A non-author demand review identifies a buyer and a diff class that existing review tools do not
   cover, without relying on vendor marketing alone.
3. A 20-case labelled diff corpus exists with at least 10 non-pattern semantic cases.
4. The UBS baseline is rerun on the same corpus with its positive control and a frozen receipt.
5. The proposed Jev dimensions have fixed reason codes, withhold semantics, and no generated prose.
6. A pre-registered gate requires a strict measurable win: at least **20 absolute percentage points
   of actionable semantic finding recall** over UBS on the non-pattern subset, false positives no
   worse than **5%**, and no material regression on UBS-covered security/test findings.
7. Review time or correct action selection improves by at least **20%** against the baseline, or the
   candidate remains held.

If the candidate cannot supply ten non-pattern semantic cases, return **UNASKABLE/HELD** rather than
lowering the gate. If Jev findings are a subset of UBS with probabilities attached, RULED_OUT is
allowed only after the shared-corpus measurement and with the retry condition recorded.

## Final ruling

**Skip Demo-9 for the current rung-3 slot. Hold it for the stated corpus-and-UBS-gap retry.**

This is not a rejection of semantic review. It is a costed sequencing decision: the candidate needs
an implementation plus labels to prove a wedge, while COD-H2 already has a runnable path and a
rung-4 instrument. The next Demo-9 action is corpus/UBS-gap preparation only after the WIP slot is
available; no build should start from this document alone.

## NO-CLAIM

No Demo-9 implementation, Jev call, labelled diff corpus, or UBS rerun was performed for this
decision. The `$2.19` estimate is arithmetic from 120 calls × 435 input tokens × `$0.042/Mtok`, not
spend. The 1–2 day engineering estimate is planning, not elapsed work. The ruling is a HOLD/skip-now
sequencing result, not a permanent product kill or a claim that UBS is complete.
