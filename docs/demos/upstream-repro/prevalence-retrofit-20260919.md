# Prevalence retrofit: no verdict inverts, one confirms hard, two are UNKNOWN

Pane 3 (muse), 2026-09-19. Zero-API unit: every number below is quoted from the
row's own committed receipt. No live calls, no re-runs.

| Candidate | Sample base rate | Population base rate | Implied TP:FP at pop. | Verdict |
|---|---|---|---|---|
| fast-jev-compaction | needed 84-92/96 (~90%) | same sessions ~90% reuse | dropping 98% of a 90%-needed population: ~9:1 wrong:right on drops | NOT-DEPLOYABLE (confirms RULED_OUT) |
| thruwire/foreman | 10/20 constructed | 30/186,449 = 0.016% | ~24 vs ~55,791 ≈ 1:2300 at 80% recall | NOT-DEPLOYABLE (already narrowed) |
| AbdelStark/bicameral | dangerous 20/40; routine FP 3/20 = 15% | dangerous commands vanishingly rare in routine traffic (<0.1% est.) | 15% FP on ~100% of traffic: thousands of nags per catch | NOT-DEPLOYABLE (confirms HELD, was never promoted) |
| claude-code-templates/jev-model-router | balanced 25/25 by design | hard turns ~253/278 ≈ 91% in their corpus | high prevalence favors deployment, but AUC 0.56-0.63 < 0.70 bar and free length wins 2/3 | NOT-DEPLOYABLE (confirms REJECT; prevalence helps, signal doesn't) |
| NiazMorshed2007/jev-review | balanced 8/14 by construction | UNKNOWN (worse-pool rate 10-38% is predicate-dependent, not a population rate) | cannot be computed — inventing one is the defect | PREVALENCE-UNKNOWN |
| Dicklesworthstone/skillranker | positives 10/12 (83%) | UNKNOWN (synthetic diagnostic; repo forbids holdout claims) | precision 0.80 at 83% would fall further at lower prevalence; n=12 so one case = 8pts | NOT-DEPLOYABLE leaning (confirms gate miss; fragility noted) |
| 0xNatoshi/jev-codex-router | n=1199 priced turns (cost claim, not detection) | downgrade-safety rate unmeasured (receipt line 62) | cannot be computed | PREVALENCE-UNKNOWN (verdict stands on cost inversion) |
| logan-markewich/jeff | 22,560 rows, 8 datasets (benchmark, no operating threshold) | benchmark class mix; no deployment decision exists | N/A — nothing is thresholded | STANDS (comparison, not a detector) |

## Inversions: none

No RULED_OUT row sits at a prevalence where its AUC would be fine, and no
CLEARED/HELD row sits where prevalence makes it useless-but-promoted — because
nothing in the HELD/CLEARED set is promoted, and every RULED_OUT fails on
grounds independent of prevalence (cost, signal<bar, gate miss). The ledger's
verdicts survive the retrofit; the retrofit's value is the two UNKNOWNs (review,
router-savings), which now carry explicit denominators-missing flags instead of
implied ones.

## NO-CLAIM

Population rates are estimated from our own corpora (sessions, histories,
synthetic sets) and do not transfer to other users' workloads. The <0.1%
dangerous-command figure is an order-of-magnitude estimate, stated as such.
No manifest row changes: nothing inverted.
