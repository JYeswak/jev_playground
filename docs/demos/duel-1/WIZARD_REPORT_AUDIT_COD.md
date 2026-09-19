<!-- A/B verdict migration (2026-09-18): any literal n=1 relative verdict below is historical/retracted. Current harness withholds verdicts until each arm has >=10 zero-spread samples; see compaction/ab/verdict.ts. -->

# DUELING_WIZARDS_REPORT.md audit — completed

Bead: `jev-demo-loop-a1q`
Report under audit: `docs/demos/duel-1/DUELING_WIZARDS_REPORT.md` at `a765840`.
Comparison sources: `docs/demos/duel-1/WIZARD_CONVERGENCE_AUDIT_COD.md` at `9b0965b`, the four score files, `compaction/runs/ab-20260917.json`, `compaction/runs/ab-rerun-20260918.json`, and `compaction/runs/ab-sample3-20260918.json`.

## 1. Convergence fidelity

**Faithful:** §1 reports the actual ruling: only 2 of 4 top-five pairings are SAME DEMO; screen and claim-check are ADJACENT BUT DISTINCT; the two alleged singletons have counterparts outside the other shortlist. Its table and the 2/4 / full-inventory concept-coverage conclusion match `WIZARD_CONVERGENCE_AUDIT_COD.md`.

**Residual overclaim:** §4 says “all three lineages independently converged on the same remedy.” The local-redaction/injection-only remedy is the result of pane 2 steelmanning MU-2 and pane 3 conceding the finding, not three independent pre-reveal proposals. The report should call this a post-reveal merged remedy, not independent convergence.

**Scope warning:** §5 says “no grader below 800” for the merged admission-screen form. CC-5 itself has 880/855, but MU-2 has 470/620 and the merged CC-5-form + MU-2-install-rigor design was not independently rescored. The sentence is true only when explicitly scoped to the CC-5 form.

## 2. Arithmetic re-derivation

| Quantity | Re-derived | Report | Verdict |
|---|---:|---:|---|
| MU on CC grader-pass mean | 820.0 | 820.0 | EXACT |
| COD on CC grader-pass mean | 814.0 | 814.0 | EXACT |
| CC on MU grader-pass mean | 762.0 | 762.0 | EXACT |
| COD on MU grader-pass mean | 705.0 | 705.0 | EXACT |
| Whole-file CC mean | 817.0 | 817.0 | EXACT |
| Whole-file MU mean | 733.5 | 733.5 | EXACT |
| Whole-file gap | 83.5 | 83.5 | EXACT |
| Drop-weakest CC mean | 832.5 | 832.5 | EXACT |
| Drop-weakest MU mean | 780.625 → 780.6 | 780.6 | EXACT (rounded) |
| Drop-weakest gap | 51.875 → 51.9 | 51.9 | EXACT (rounded) |

Per-demo means are also correct: CC-5 867.5; merged routing 853.75 → 853.8; CC-2 claim-check 835.0; foreman 812.5; fact ledger 792.5; MU-4 claim-check 767.5; merged signals 712.5; MU-2 admission 545.0.

The 20-score denominator and 8-row post-ruling demo table are correct. The correction table’s “33 points” entry is still semantically ambiguous: 95.1 − 62.6 = 32.5, but the cited benchmark also reports 81.3 as the comparison value. The report should name the metric pair instead of calling it simply “33 points worse.”

## 3. A/B nondeterminism

Faithful. §§6 and 8 do not treat “B wins” as stable evidence. They cite R11’s byte-identical arm-B sequence 3, 1, 3, reject a one-word verdict, and replace N≥50 alone with a pinned generator or a published distribution. The report correctly calls the routing recommendation defensible because it is read-only, not because B won.

## 4. Bias-audit ruling

The four grader-pass means and the author-versus-neutral comparisons are arithmetically correct. The self-exoneration is incomplete, however: an author scoring the opponent above the neutral grader does not prove absence of bias because scores are subjective and there is no calibrated external scoring oracle. The transparent disclosure is evidence in its favor, not a proof. The report should retain that limitation beside the arithmetic.

**Verdict:** the report faithfully corrects the headline and the stochastic A/B claim, but it needs the three qualifications above: post-reveal remedy is not independent convergence, “no grader below 800” must be scoped to CC-5’s form, and the bias comparison is suggestive rather than dispositive.

**NO-CLAIM:** This audit did not alter the synthesis report, rerun any idea harness, or add a consensus score. It re-derived the recorded arithmetic and checked the report against pane 2’s committed convergence ruling and R11 evidence.
---
