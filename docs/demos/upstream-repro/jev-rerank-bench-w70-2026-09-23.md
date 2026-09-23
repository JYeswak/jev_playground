# jev-rerank-bench — W7.0 receipt (2026-09-23, worker W70Rerank)

Clone: `anessbelbati/jev-rerank-bench@cd9a35b22aeb4187334f7018a0ee1960a7470586`
(`cd9a35b Include Qwen controls in the public evidence export`).
What it is: hand-rolled-POST rerank benchmark — 30 BM25 candidates/query
(`common.py:26`), 1,617 scored headline questions, NevIR negation pairs,
Jev vs Cohere Pro/Fast vs zerank-2 vs DeepSeek vs self-hosted Qwen RLCD vs BM25.
Profile: seat/benchmark → T1–T8 + T10. No prior receipt is cited as evidence.

T4 bar (committed at `fec3f95`, `docs/demos/upstream-repro/w70-prereg-p5.md`,
pre-data, not moved): live spot N=30 sampled rows (seed recorded), one rubric
arm, PASS if live choices reproduce the committed cache on ≥24/30.
Cost ceiling for the T4 arm: 30 Jev calls — met exactly.

| id | result | evidence |
|---|---|---|
| T1 pin+env | PASS | SHA `cd9a35b22aeb4187334f7018a0ee1960a7470586`, 2026-09-23 UTC, MIT (`LICENSE`, `README.md:264-268`). `git status` before AND after identical, 6 pre-existing dirty files, all re-rendered outputs (fresh re-score in a `/tmp` copy reproduces 3/3 JSONs byte-identically): `M results/calibration_nq.png, nevir.json, runs.jsonl, significance.json, summary.json, summary.md`. Env: `OMP_PROFILE`/`PI_CODING_AGENT_DIR`/`PI_PROFILE` set, host `Joshs-Mac-Studio.local` Darwin 25.5.0 arm64, `uv 0.9.28`, project python 3.14.2, worker W70Rerank. Clone tree never edited; all runs in `/tmp/jev-rerank-fresh`, defects in `/tmp/jev-rerank-defect`. |
| T2 own suite fresh | PASS (suite can fail) | `uv run eval.py` exit 0 on committed cache; `uv run scripts/test_export_evidence.py`: 9 ran, 0 failed, 0 skipped (no skips to list by reason). Design exclusions (not skips): only queries with ≥1 relevant in BM25 top-30 are scored — headline 2,327→1,617 (scifact 300→264, fiqa 648→411, nq 500→320, nfcorpus 323→239, trec-covid 50→50, bright-bio 103→39, bright-eco 103→38, csn 300→256). Fresh headline reproduces README: rubric 0.6921, Cohere Pro 0.6912, BM25 0.4861. Planted defect (`export_evidence.py:522` `*1000`→`*100`, `/tmp` copy only) turns suite RED: exit 1, `FAILED (failures=1)`, `AssertionError: 100.0 != 1000` (`test_macro_query_weighting_and_cost_population`). |
| T3 claim inventory | PASS (7 claims, all demonstrated) | C1 tie, no winner: rubric−Cohere +0.001 [−0.009,+0.012] — fresh +0.0009 [−0.0093,+0.0124] (`README.md:41-42`, `significance.py:47-49,83-85`). C2 equal query weight flips it: Cohere 0.756 vs Jev 0.738 — fresh 0.7564 vs 0.7380, n=1617 (`README.md:42`, `scripts/export_evidence.py:521` micro average). C3 NevIR: Jev 71% vs Cohere 67%, +4.2 [+1.5,+6.9] — fresh 0.7115 vs 0.6696, +4.19 [+1.52,+6.87], p=0.0022, real (`README.md:45-46`, `nevir_eval.py:62,80-85`). C4 Choice top-1 +3.1pp [+0.7,+5.6] — fresh +0.0314 [+0.0075,+0.0560], p=0.006 (`README.md:43-44`). C5 Qwen one-passage 0.471, no gain over BM25 0.486 (−0.015 [−0.033,+0.004]) — fresh 0.4711 vs 0.4861, −0.0150 [−0.0343,+0.0034] (`README.md:49-50,80-82`). C6 order sensitivity: Qwen top changes 1,498/1,617 (92.6%) vs Jev Choice 400 (24.7%) — fresh exact (`README.md:85-86`, `eval.py:202-208`). C7 score gap 0.046 Qwen vs 0.430 Jev; slot means 0.195→0.384 — fresh 0.0456 vs 0.4298; 0.1947→0.3839 (`README.md:91-94`, `rlcd_check.py:15`). |
| T4 live Jev, own questions | PASS 28/30 | Arm `jev-score-batch` (4-level rubric, `rerankers/jev.py:136-158`) via the clone's own client; model sent `jev-1.13.0`, API echoes `model=jev-1.13.0`. Sample: seed 20260923, 15 scifact + 15 nfcorpus present-scored `ok` rows (frame sizes logged), workers=6. N=30, query prevalence 30/30 (frame requires ≥1 relevant), passage prevalence 58/900 (6.4%). 30 calls, 0 failed, cost $0.017876, p50 397.9 ms / p95 992.7 ms. Reproductions 28/30 ≥ 24. Misses: scifact q148, nfcorpus PLAIN-634. |
| T5 floors, same 30 | PASS (no tie) | Floor A majority-constant (BM25 order unchanged) and Floor B lexical BM25: top-1 10/30 (0.333), nDCG@10 mean 0.3811. Jev live: top-1 15/30 (0.500), nDCG 0.4958. Jev cache: 15/30, 0.5017. Floors trail by 5 top-1 and −0.115 nDCG — seat not refused. |
| T6 incumbent, same rows | PASS (inconclusive, as headline predicts) | Cohere Rerank 4 Pro via OpenRouter (`rerankers/cohere.py:8-28`), key held. Served `rerank-v4.0-pro` via Cohere. 30 calls, 0 failed, cost $0.075, p50 726.6 ms / p95 1648.4 ms. Cohere top-1 12/30 (0.400), nDCG 0.4816 vs Jev live 15/30 (0.500), 0.4958. McNemar on top-1 correctness: b=5 (Jev-only), c=2 (Cohere-only), two-sided p=0.4531 — no winner at N=30, consistent with the clone's own "neither a winner nor equivalence". |
| T7 calibration | PASS (bins with counts) | Live top-pick confidence vs agreement-with-cache: [0.0,0.4) n=2 agree 0.500; [0.4,0.6) n=10 agree 1.000; [0.6,0.8) n=10 agree 1.000; [0.8,1.0] n=8 agree 0.875. Spread across bins (not single-bin), but N=30: the top-bin dip is one miss in eight; no reliability claim beyond the table. |
| T8 stability | PASS | 5-row subset (first five of the spot sample): 3× identical asks → 0/10 repeat flips; 1 reworded-instructions ask, state identical → 0/5 framing flips. 15 extra calls, 0 failed, cost $0.00895, p50 374.5 ms / p95 694.3 ms. |
| T9 fault behaviour | NA (profile reason) | Seat/benchmark profile runs T1–T8+T10 per W7.0 §W7.0; no SDK/client surface to fault-probe. |
| T10 verdict | SELF | (a) Result class SELF: committed cache re-scores exactly, live rubric reproduces cache 28/30, floors beaten, incumbent statistically tied — the clone's numbers are its own and they replicate. (b) Tiers: C1–C7 DEMONSTRATED (independent fresh re-score matches to the printed digit); cost/latency tables REPORTED-NOT-VERIFIED (clone states no invoice reconciliation, `README.md:61,203`). (c) NO-CLAIM: no claim beyond the 30 sampled rows plus the committed-cache re-score; live N=30 cannot settle the Jev-vs-Cohere headline, and was never asked to. Nothing NOT-RUN. Total live spend: 45 Jev calls ($0.02683) + 30 Cohere calls ($0.075). |

## Boundary

In scope: pinned re-score of the committed cache (exact), one pinned-model live
rubric spot (28/30), floors, Cohere incumbent, bins, stability — all on
scifact+nfcorpus present rows, seed 20260923, `jev-1.13.0` echoed by the API.
Out of scope: the other six Jev variants live, NevIR/BRIGHT/MIRACL live,
Qwen/GPU reproduction, invoice verification of costs, the six dirty
`results/*` files beyond byte-comparison of three JSONs. The 20260918 receipt,
if it exists, was not consulted and counts for nothing here.
