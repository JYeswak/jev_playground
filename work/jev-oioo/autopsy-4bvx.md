# Jev Climate-FEVER autopsy — jev-4bvx

Keyless failure analysis of the committed Jev arm, not a new model run and not a ruling.

## Evidence boundary

- Dataset: `tdiggelm/climate-fever@1.0.1`; source SHA `8a4b9032d861be482ffb49dddfd283ffa6089e654f1e968040011882c5eb6e0b`.
- Frozen eligible corpus: 907 claim/evidence states, 654 `SUPPORTS` and 253 `REFUTES`; item-manifest SHA `bbda30671b46678a11717d0fa89994b5226e9887ff321ec70a860e45f579032c`.
- Jev rows: `work/jev-oioo/live-results.jsonl`, model `jev-1.13.0`, 907/907 scored, 0 refusal/error rows. Receipt `work/jev-oioo/final-receipt.json`; Jev accuracy 597/907 = 65.8%, Brier 0.2328, input spend $0.021322602.
- Comparator rows are quarantined after OpenRouter daily quota; no comparator claim is made here.
- All examples below are hash-keyed IDs only. Raw claim/evidence text stays under `var/agent-tmp/jev-oioo/`.

## Confusion and confidence shape

| Gold | Correct | Incorrect | Accuracy | Error rate |
|---|---:|---:|---:|---:|
| SUPPORTS | 353 | 301 | 53.98% | 46.02% |
| REFUTES | 244 | 9 | 96.44% | 3.56% |
| **Total** | **597** | **310** | **65.82%** | **34.18%** |

Noul histogram by gold (bins are rounded to tenths; counts are rows):

| Noul bin | SUPPORTS | REFUTES |
|---|---:|---:|
| 0.0 | 16 | 115 |
| 0.1 | 82 | 92 |
| 0.2 | 74 | 21 |
| 0.3 | 59 | 5 |
| 0.4 | 43 | 9 |
| 0.5 | 52 | 6 |
| 0.6 | 49 | 1 |
| 0.7 | 43 | 2 |
| 0.8 | 88 | 2 |
| 0.9 | 116 | 0 |
| 1.0 | 32 | 0 |

The gap is asymmetric: 301 SUPPORTS errors versus 9 REFUTES errors. This is not explained by a generic inability to read the state.

## Failure modes

Counts are disjoint by the first applicable category below.

1. **State evidence is heterogeneous or incomplete — 288/310 errors.** 815/907 states (583 SUPPORTS, 232 REFUTES) contain at least one per-sentence `NOT_ENOUGH_INFO` label or a sentence label that does not equal the claim label. Jev errors: 279 SUPPORTS and 9 REFUTES. The five-sentence list mixes relevant, irrelevant, and contradictory/undecidable evidence, while the frozen Noul asks one aggregate support question.
   - Hash examples: `7417443dd462bb5eaa127b1374aeff2bc4fecb20204790fd2b8b0202aab6fc3a`, `cfb6595b74224e4d169d9e508895ff836c500977b63a49e463788cdb9b277625`, `6c7cfecc52e4bfef771a59ecf1925a2a74a0c954d9f4965d6895562caeaed140`.

2. **Claim-label/evidence-label disagreement — 200/495 errors.** The majority per-sentence evidence label differs from the dataset claim label on 495 states. Jev errors: 191 SUPPORTS and 9 REFUTES. This is a label/state construction conflict, not evidence that the API returned malformed data.
   - Hash examples: `cfb6595b74224e4d169d9e508895ff836c500977b63a49e463788cdb9b277625`, `a20d93471e8637fb238035a7c1299f24ab1818a8bb3b2804c2b3c5667b85e48f`, `0c154a242366b10eb448f3a73519193aae227ff98de54bd6c1b742df90a37db7`.

3. **Question/state semantic mismatch — 22/92 clean-state errors.** Only 92 states have all five per-sentence evidence labels equal to the claim label. Jev still misses 22 SUPPORTS and 0 REFUTES in that subset. The wording `Does the abstract support the claim?` is a binary aggregate question applied to a five-sentence evidence list; it does not identify which sentence supports or fails to support the claim.
   - Hash examples: `ede1ba0bb3c8552b61ca2bd21b73e64497dc893f643962d8759718c47deeac5`, `6b40d2a2af8f36683d2bc0cab14a0d7652405c098919a9d7149`, `4e7366a482a8eb3b193deea67d11611abaf0e4ec145beb8de8adda6397fee1bb`.

4. **Residual asymmetric model limit — 22 clean SUPPORTS misses.** After removing heterogeneous and claim/evidence-conflict states, the remaining errors are all SUPPORTS false negatives. This is the residual model-limit hypothesis, not yet proven: the clean subset is only 92 rows and was not held out from prompt/state design.
   - Hash examples: `ede1ba0bb3c8552b61ca2bd21b73e644887dc893f643962d8759718c47deeac5`, `6b40d2a2af8f36683d2bc0cab14a0d7652405c098919a9d7149`, `4e7366a482a8eb3b193deea67d11611abaf0e4ec145beb8de8adda6397fee1bb`.

5. **Harness/validator failure — 0 observed.** All 907 rows are scored, all carry a valid numeric Noul and model `jev-1.13.0`, and the receipt records no refusal/error rows. The harness is not a supported explanation for this gap.

## Ranked hypotheses and discriminating tests

1. **Heterogeneous evidence dominates the loss.** Rebuild states with only evidence sentences whose per-sentence label agrees with the claim, keeping the original claim and row IDs. Prediction: the SUPPORTS error rate falls materially below 46.0%; if not, reject this as the dominant cause.
2. **The aggregate Noul wording is the wrong decision shape.** Ask a Choice or fan-out Nouls that first scores each sentence, then aggregates with an explicit support rule. Prediction: clean and mixed-state SUPPORTS recall improves without increasing REFUTES false positives; otherwise the question-shape hypothesis weakens.
3. **Dataset claim labels conflict with evidence labels.** Score a preregistered subset stratified by majority-evidence agreement versus disagreement. Prediction: the disagreement stratum remains near chance or reverses while agreement improves; if both strata match, label noise is not causal.
4. **Residual Jev model limit on clean SUPPORTS.** Hold out a fresh clean-state set and repeat the frozen question. Prediction: the same SUPPORTS-only miss pattern recurs; otherwise the 22/92 result was sampling noise.
5. **Harness bug.** Re-run only schema/validator and row-accounting checks; any malformed/missing row would reopen this hypothesis. Current evidence is 0 such rows.

## Boundary

This autopsy reanalyzes committed Jev rows and local public-data metadata only. No new Jev or comparator calls were made. It does not establish a general Climate-FEVER capability, does not compare against the quarantined free comparator, and does not claim a fix or a promotion decision.
