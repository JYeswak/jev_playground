# Quoted-number census — Q11

Status: measured source audit, not a design.

## Result

Fourteen headline entries were audited because surviving candidates or the lane calibration/guardrail claims still lean on them. Eight local source/control paths were opened; four survey entries remain external/unopened; four other headline families were explicitly excluded because no live surviving candidate depends on them.

The key correction is already measured: phishing arithmetic survives, but its own no-AI control explains 29.0 of the quoted 32.5 points, leaving 3.5 points of method gain. The compaction 3–1 summary headline fails stability: reruns are 1–1 and 1–3. Survey ceilings are not local controls.

## Census table

| ID | Headline | Control opened | Outcome | Dependency |
|---|---|---:|---|---|
| USAGE-1a | injection probability 0.99 while page remained readable | yes | UNVERIFIED | Demo-2 admission screen |
| USAGE-2a | contradicted claim caught at confidence 1.0 against a city ordinance | yes | UNVERIFIED | Demo-6/Demo-3 claim surface |
| USAGE-7a | 6,257 traces; Who 73.4, When 76.4, All 31.3; $1.28 | yes | EXCLUDED | None currently; excluded |
| USAGE-9a | TF-IDF needs 100–10,000 labels to match; shifted mail loses 20+ points | yes | REPRICED_BUT_SUPPORTED | Demo-7 signals starter |
| USAGE-9b | verdict 62.6 vs 81.3; five signals + fitted head 95.1; AUROC .988; ECE .027; fixed 89.5 | yes | SURVIVES_NUMERICALLY_REPRICED | Demo-7 signals starter |
| USAGE-12a | 662 injection messages and 200 vulnerable-code pairs | yes | SURVIVES_SCOPE | Demo-2 guardrail framing |
| USAGE-14a | 45% reduction, zero text loss; summary won 3–1 at one-third bytes | yes | UNSTABLE_HEADLINE | Demo-5 fact ledger |
| USAGE-13a | ECE .061, Brier .020, Noul 58/60, Choice 19/20 | yes | SURVIVES_LOCAL_FIXTURE_ONLY | All probability-bearing candidates |
| SURVEY-1 | TypeSafe four-workflow average 67.8% agreement | no | UNVERIFIED_EXTERNAL | Calibration/decision-layer claims |
| SURVEY-2 | Mike Taylor 12 passages: Jev 6/7, Fable 5.1 7/7; ~25x faster, ~580x cheaper | no | UNVERIFIED_EXTERNAL | External early-warning ceiling |
| SURVEY-3 | 193.6x faster and 444.6x cheaper against a named LLM baseline | no | CONFLICTED_EXTERNAL | Any cost/latency superiority claim |
| SURVEY-4 | HN 1,863-point discussion warns typed output can still be a wrong valid value | no | NON_BENCHMARK | Typed judgment claims |

## Source-side findings

### Demo-7 phishing benchmark
`jev-phishing-bench@1d56e8c` was opened at pinned SHA `1d56e8c64d029a9554a0874e2ef2901ed196e230`. `results/report.md` contains the quoted 62.6%, 81.3%, 95.1%, 0.988, 0.027, and 89.5 values. It also contains five controls: a no-AI free-hosting rule at 91.6%, an A/B split, alternate LLM questions, alternate verdict wordings, and a dataset-knowledge disclosure. The headline survives as source arithmetic; its original method interpretation does not.

### Demo-5 compaction
`compaction/runs/replay-big-20260917.json` gives 2047→1136 chars (44.43%), 13→8 messages, and 11 calls. The A/B has three exact recall questions. The original 1/3 versus 3/3 “B wins” was not stable: rerun ties at 1/3 versus 1/3, and same-fixture sample3 returns 1/3 versus 3/3. The control result is generator variance; no stable winner should be quoted.

### Guardrail benchmark
`jev-sec-bench@fdb16b9` was opened at pinned SHA `fdb16b94d37535db9bad77f8ef0faa971bd7d69a`. Its README confirms 662 labelled injection messages (263 positives) and 200 matched vulnerable-code pairs. Context and label-audit controls are present; corpus sizes survive, but accuracy carries those caveats.

### Spam/label curve
`jev-spam-eval@76ef183` explicitly draws each learning-curve size five times. The table shows parity points near 10,000 for email logistic, 200 for Ling-Spam naive Bayes, and 100 for the three-category test. The Usage Map range 100–10,000 is directionally true but hides dataset-specific results and OOD caveats.

### Calibration fixture
`foundation/runs/20260917T224444Z.json` records ECE 0.0613, Brier 0.0199, n=60, threshold coverage, and Choice accuracy 0.95 over the hashed local fixture. This is an opened control receipt, not external transfer evidence.

## External survey numbers
The survey summary is in `PLAN.md` §3q, but the raw 11-sweep/716-item artifact is absent from this checkout. Public sources found Mike Taylor’s 12-passage report and TypeSafe/DataCamp discussion, but this census did not treat them as local re-derivations. The 67.8% figure is agreement with reference answers reportedly produced by other models, not human ground truth. The 193.6x/444.6x headline has conflicting public baseline descriptions; it must not be used generically.

## Excluded headline families
Rerank nDCG/cost, router -60%/237 turns, browser 7.1s, and failure-attribution 6257/73.4/76.4/31.3/$1.28 were not opened in this pass because no current surviving candidate depends on those surfaces. The exclusion is explicit, not a validation claim.

## NO-CLAIM
This census validates source-side presence and control/ablation status, not broad truth, adoption, or transfer. “Control opened” means the pinned local source or receipt was read; it does not mean the control was independently rerun. No live model call or external package install was made.
