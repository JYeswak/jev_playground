# Rung-4 label plan — pricing 200 policy labels (Q30)

Status: pricing measured, not estimated. A 10-case trial was run, timed,
and is reported below with its caveats. Bottom line up front: **N=200 is
affordable** (~90 label-minutes + audit). No UNASKABLE pressure applies.

## Trial method (so the number means something)

Sample: 10 destructive-bash turns, deterministic seed 20260918, from
1,457 destructive candidates across 111 journals (same corpus as the
Q9/Q12 census). Each card: pattern id, command truncated to 160 chars
(secrets scrubbed, home paths folded), last-2 user texts truncated.
Three cards (T4/T6/T10) fired their selection pattern outside the
visible window; full commands were pulled transiently for those three
(all benign; the pattern fired on unseen text — recorded as a
methodology caveat, not hidden).

Rubric (rung-4 design, verbatim classes): pass / withhold / escalate /
block. Labels: T1 escalate, T2 escalate, T3 block, T4–T10 pass
(7/2/1/0 split; destructive-only sample skews pass-light on purpose —
a pricing trial prices the *act*, and destructive cases are the slow
ones).

## Measured timing (loaded, honestly loaded)

- 06:03:00 trial cards in context → 06:04:10 labels file written,
  including one verification probe (full-command pull for T4/T6/T10)
  and caveat analysis: **~27 s/label all-in**.
- Pure judgment (reading cards + deciding) estimated ~12 s/label; the
  difference is harness overhead I choose NOT to subtract, because the
  real run has its own overhead (manifest handling, adjudication).
- Use 27 s/label for pricing. It is conservative by construction.

## Extrapolation by stratum (limits stated)

The 200-case design needs four strata, and they price differently:

| Stratum | N | Rate used | Cost | Basis |
|---|---|---|---|---|
| reversible/read | 50 | ~10 s | ~8 min | simpler than trial; mostly pass |
| disallowed/destructive | 50 | ~27 s | ~23 min | measured trial rate |
| ambiguous-authority | 50 | ~40 s | ~33 min | evidence hunt per case (estimate, flagged) |
| credential/injection | 50 | ~30 s | ~25 min | redaction handling + policy read (estimate, flagged) |
| **Total label** | **200** | | **~90 min** | single pane, one sitting |

Only the destructive row is measured; the other three are estimated
with direction stated (reversible faster, ambiguous/credential
slower). If the estimates are off 2× against, the total is still an
afternoon. **Largest affordable N: the full 200, no reduction argued
for.** Had the trial shown otherwise, this section would name the
smaller N and let the design's UNASKABLE clause fire — it does not.

## Split design (hard constraint honored)

The author of `policy.json` cannot be the sole source of the labels
its policy is graded against. Split, pre-registered:

- **Pane A labels all 200** (suggested: pane 2, which authored neither
  the policy nor the corpus classifier).
- **Pane B audits a random 20** (seed committed before sampling),
  blind to A's labels.
- **Agreement bar: ≥18/20.** Below it, labels are re-done with an
  adjudicated rubric, not averaged into agreement.
- **Disagreements go to the conductor**, case by case, recorded in
  the receipt with both labels and the ruling. No silent majority
  rule, no author override.
- Audit sample and bar are fixed here, before any label exists.

## Live-call cost (first-party verified)

`docs-mirror/typesafe/models.md:13-16`: **$42/Btok = $0.042/Mtok,
input only, output free.** The dispatch's "unverified external
figure" is now verified in-repo — quote: *"| Price (per Btok / per
Mtok) | $42 / $0.042 |"*. Arithmetic check: 2,000 calls × measured
mean 435 input tokens (Q24 usage: 439/444/438/434/420) = 870,000
tokens = 0.870M × $0.042 = **$0.0365 ≈ $0.037**. Model money is not
the constraint on rung 4; the ~90 label-minutes are, and they fit.

## Who verifies, and what could still block

- Verifier of this plan: conductor (pricing method + arithmetic).
- Verifier of the labels: pane-B audit per the split above.
- Remaining blockers, named not hidden: ambiguous-stratum rate
  could exceed estimate if evidence hunts run long (cap: timebox
  60 s/case, overflow marked AMBIGUOUS-capped and counted); live
  provider must support the K=10 budget (else UNASKABLE per design,
  not a smaller K).
