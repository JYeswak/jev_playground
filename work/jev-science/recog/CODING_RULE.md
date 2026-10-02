# CODING RULE v1: RECOGNITION vs FORECASTING (jev-2zbl Part A retest)

Committed BEFORE any row is coded (2026-10-02, OrangeFrog). Codes are assigned from
the experiment's task/hypothesis text alone; verdicts live in a separate file joined
by script, never hand-transcribed. Analyst is NOT blind to published outcomes (stated
limitation); the procedure is blind (rule fixed first, applied mechanically).

## Rule
- **FORECASTING (F)** iff the task asks about an event realized AFTER judgment time
  (will-X, would-X-if-run, gets-reopened, duration-will-exceed) OR the gold label was
  produced by running/observing something after the judged text existed (retry exits,
  suite results, background durations, reopen events, next-action outcomes).
- **RECOGNITION (R)** otherwise: the label is asserted determinable from the provided
  text (injection present, skill fits prompt, memory relevant to prompt, hazard pattern
  in command, duplicate-of relation between given texts, claim-evidence relation
  within the given pair). Post-hoc autopsies ("needed state outside the text") MUST
  NOT be used to code F; code from the task as posed.

## Edge conventions (fixed here, not per-row)
- Triage/routing to a handling action whose correctness is judged by later handling:
  F only if the task names the later outcome; plain "triage these messages" with
  labels from readers of the same text: R. (R140/R145 keep their table flag; agreement
  with the table's `future_counterfactual` column is REPORTED, not enforced.)
- Game/benchmark play (win the game, reach a line): the label (score/outcome) is
  realized in play after the judged move: F.
- External-comparator benchmark rows (Jev vs Haiku on Banking77/SciFact/FEVER):
  code by the same rule (all R: label in the text), included in primary; own-vein-only
  (exclude the 3 comparator wins) reported as pre-committed sensitivity.

## Pre-committed analyses
- PRIMARY: WIN vs NON-WIN (loss+tie) by R/F. Fisher exact two-sided p, odds ratio
  (Haldane-Anscombe corrected, 95% CI), risk difference with 95% CI.
- SECONDARY (reported, not decisive): LOSS vs NON-LOSS; WIN-or-TIE vs LOSS.
- A non-significant primary is a result ABOUT THE FEATURE (single-feature
  insufficient), not a license to try codings until green.
