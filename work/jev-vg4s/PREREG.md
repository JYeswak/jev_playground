# Verify confirmation: HealthVer cleaner claim/evidence pairs

Status: PREREGISTERED BEFORE LIVE CALLS
Bead: jev-vg4s
Date: 2026-09-27
Launch gate: Jev may run after approval; the free comparator runner refuses before `2026-09-30T00:00:00Z`; 2026-09-28 and 2026-09-29 free-tier allocations are reserved by existing beads.
reach-mode: mcnemar

## Question and corpus

Does the frozen `kit/src/verify.ts` Noul design retain its SciFact confirmation against a cleaner public claim/evidence set with exactly one source label per pair, when compared with the allowed free incumbent?

- Dataset: `jpd459/healthver_resplit`, revision `2d97d56c72aed720abb7bd7a981d44d645f136a5`, Apache-2.0.
- Source file: pinned public `test.jsonl`, source SHA-256 `eced674cf13b2f5171705518786a0e58ef8dd468a4972cc808aa0d78b82d99ce`, 378808 bytes.
- Exact corpus: `work/jev-vg4s/corpus.jsonl`, 840 source-order rows, corpus SHA-256 `24bdc0e651e1694652fc82bf4e2a167170e9b2aceeb2037efcaacd752d106d02`.
- Source labels: 322 `Supports`, 206 `Refutes`, 312 `Neutral`.
- Binary gold mapping, fixed before calls: `Supports` → `SUPPORTS`; `Refutes` and `Neutral` → `NOT_SUPPORTED`. This is the binary verify decision, not a claim that Neutral means contradiction.
- Each row has one source label. No per-sentence labels, mixed-label rows, or post-hoc filtering are used. Workspace search found no prior HealthVer rows or source mention before this preregistration.

## Frozen request and arms

State per row: `{ "claim": row.claim, "evidence": row.evidence }`. The source `question` field is not sent; this preserves the existing verify design's state contract.

Question: exactly `kit/src/verify.ts` / `docs-mirror/typesafe/cookbooks/citation_check.md`:

- Instructions: `Does the evidence support the claim?`
- Criteria true: `The evidence states the claim or directly implies that it is true`
- Criteria false: `The evidence contradicts the claim, or does not address what the claim asserts`
- Decision: strict `noul > 0.5` means `SUPPORTS`; exact `0.5` means `NOT_SUPPORTED`.

Arms, same state and question:

- Jev: pinned `jev-1.13.0`, official TypeSafe client path.
- Incumbent: OpenRouter `dots-studio/dots-3-note-preview:free` through the pinned system-one-adapter path. No paid comparator, Anthropic, or xAI arm.
- Each arm stores raw Noul, model, latency, usage, and validation status per hash-keyed row. Missing, malformed, or refused answers are invalid; no coercion or imputation.

## Preregistered metrics and bar

Primary metrics per arm: accuracy at `noul > 0.5`, AUC, Brier score, and 10-bin ECE. Report Wilson 95% accuracy/refusal intervals and paired exact McNemar on accuracy. Report paired bootstrap differences for AUC, Brier, and ECE with 2,000 resamples, seed `20260927`, percentile 95% intervals, Jev minus comparator.

Pass rule, fixed before calls:

1. Jev beats the always-`NOT_SUPPORTED` constant: Jev accuracy is strictly higher with exact McNemar `p < 0.05`, and Jev AUC's 95% interval is entirely above 0.5.
2. Jev beats the fitted base-rate constant on Brier: Jev-minus-constant Brier 95% interval is entirely below zero.
3. Jev does not lose to the free incumbent: no significant comparator win on accuracy, AUC, Brier, or ECE. A non-significant difference is `TIE`, not parity proven.
4. Each arm refusal rate is `<= 5%`.

`PASS` requires all four. Otherwise record the exact failed condition; do not retune wording, threshold, label mapping, or bar after answers.

## Size, reach, spend, and launch gate

- Planned N: 840 pairs, all rows in the pinned test split; no split or adaptive stopping.
- Planning reference: the prior SciFact paired run had Jev-only accuracy wins `b=19` and comparator-only wins `c=9` on 400 rows (discordance 28/400). This prereg uses the bead's prospective target of approximately 840 pairs for 0.80-power planning at that observed discordance; this is planning arithmetic, not an observed HealthVer result.
- Reach receipt: `work/jev-vg4s/reachability.json`, bound to this preregistration and corpus before calls. Exact state-size preflight must show all 840 requests `FITS`.
- Maximum calls: 840 Jev and 840 free-comparator requests, one per row and arm. If the free comparator exceeds its daily quota, the runner stops on HTTP 429 and records `NOT_RUN`; it never labels remaining rows as model failures or silently resumes within that day.
- The free-comparator runner must refuse before `2026-09-30T00:00:00Z` with no comparator API request. Jev may run after approval. After the comparator gate, stop on 401/402/403/429 and checkpoint every completed row.
- Jev spend: record input/output tokens and compute input spend at `$0.042/M` billed input tokens, output free. Comparator OpenRouter usage and spend are recorded; expected comparator charge is `$0` for the `:free` model.
## Dataset-card provenance boundary

The pinned `jpd459/healthver_resplit` dataset card at revision `2d97d56c72aed720abb7bd7a981d44d645f136a5` contains license metadata but no description of how its resplit differs from the original HealthVer authors' release. The prereg therefore records the observable change only: this run uses the maintainer's pinned `train.jsonl`/`dev.jsonl`/`test.jsonl` resplit, specifically all 840 rows of its `test.jsonl`; no stronger claim about the resampling or deduplication procedure is made. The receipt must repeat this limitation.

## Boundary

This preregistration is a future live confirmation on one public HealthVer test split. It does not claim performance before calls, does not establish general medical fact verification, and does not license deployment. `Neutral` is deliberately collapsed to `NOT_SUPPORTED` for the binary verify decision and remains a reported source-label stratum.
