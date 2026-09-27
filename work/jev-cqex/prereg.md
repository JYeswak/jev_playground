# Climate-FEVER H3: claim/evidence-label conflict analysis

Status: PREREGISTERED BEFORE COMPUTATION
Bead: jev-cqex
Date: 2026-09-27

This is a keyless reanalysis. No Jev, comparator, or other model call is permitted or required.

## Question and frozen scope

H1 and H2 tested Jev verification on the same Climate-FEVER dev slice. H3 tests whether Jev accuracy is conditional on a disagreement between the dataset claim label and the majority of its own per-sentence evidence labels.

The analysis uses only committed Jev answers, hash-keyed IDs, and local public-dataset metadata. It does not inspect or publish claim/evidence text. It does not alter, rescore, or reinterpret any Jev answer.

## Frozen inputs

- Dataset: `tdiggelm/climate-fever`, release/tag `1.0.1`.
- Dataset source SHA-256: `8a4b9032d861be482ffb49dddfd283ffa6089e654f1e968040011882c5eb6e0b`.
- Local source: `var/agent-tmp/jev-oioo/climate-fever.jsonl`; source bytes remain local.
- Eligible rows: all 907 rows whose dataset claim label is `SUPPORTS` or `REFUTES`; `NOT_ENOUGH_INFO` and `DISPUTED` claims are excluded exactly as in the committed H1/H2 corpus.
- Jev answers: `work/jev-oioo/live-results.jsonl`, model `jev-1.13.0`, 907 rows, corrected decision threshold `noul > 0.5` (strict; exact `0.5` is `REFUTES`), receipt `work/jev-oioo/final-receipt.json`.
- The source row is joined to the committed answer by the existing hash-keyed claim ID. No row is sampled, reordered, or dropped after the eligibility filter.

## Frozen stratum construction

For each eligible row, read the five source `evidence_label` values exactly as recorded. Count every recorded label, including `NOT_ENOUGH_INFO`, `SUPPORTS`, `REFUTES`, and `DISPUTED`; no evidence label is discarded or mapped.

- `agree`: one unique label has the strictly largest count and equals the claim label.
- `disagree`: one unique label has the strictly largest count and differs from the claim label.
- `ambiguous`: the maximum count is tied across two or more labels. Ambiguous rows are reported separately and excluded from the primary agree/disagree comparison.

The stratum assignment, five-label count vector, claim label, and hash-keyed ID are written to `work/jev-cqex/strata.jsonl` after this preregistration is committed. No text is written there.

## Frozen metrics and decision rule

For each stratum, compute Jev's binary prediction as `noul > 0.5` and exact accuracy against the dataset claim label. Report `n`, correct, accuracy, and two-sided Wilson 95% interval. Report the full confusion counts and the number of Jev refusal/error rows; any refusal/error is invalid and excluded from that stratum's accuracy denominator, never coerced.

Primary H3 diagnostic: the `disagree` stratum's Jev accuracy is **near chance** iff its point estimate is within 10 percentage points of binary chance: `0.40 <= accuracy <= 0.60` on valid rows. This is a diagnostic condition, not a deployment bar.

Secondary: report the `agree` stratum accuracy and Wilson interval, the `ambiguous` stratum separately, and the accuracy difference `agree - disagree`. No post-hoc threshold, stratum rule, or exclusion is permitted.

Interpretation is frozen:

- If `disagree` is near chance, H3 supports the explanation that claim/evidence-label conflict is a meaningful contributor to the committed Jev error pattern; this does not establish a general Climate-FEVER capability or license a fix.
- If `disagree` is outside `[0.40, 0.60]`, H3 does not support that near-chance explanation; the next loss-depth decision remains outside this reanalysis.
- In either case, this result is keyless and observational; it is not a new Jev live claim, comparator result, promotion, or ruling.

## Provenance and boundary

Before any computation, this preregistration is committed and its SHA is sent to pane 1. The result note must include the prereg SHA, source SHA, answer-file SHA, strata-file SHA, exact commands, and no-call statement. Only hash-keyed IDs and aggregate counts may be committed; no raw claim or evidence sentence may be committed.
