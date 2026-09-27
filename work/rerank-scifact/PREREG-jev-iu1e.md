# Jev vs BM25 rerank preregistration — jev-iu1e

**Frozen before any live call.**

- **Dataset:** public BEIR SciFact test split, qrels and corpus; the committed `candidates.jsonl` is the observed BM25 top-20 candidate list, not authored labels. Dataset artifact SHA and source are recorded by the runner.
- **Items:** every row in `candidates.jsonl` with a query id and qrels-derived relevance list; no post-hoc filtering. Expected N is 219 rows; the run MUST refuse if the reachable receipt does not cover the exact items file.
- **Baseline:** BM25 candidate order, as captured in `candidates.jsonl`.
- **Treatment:** Jev `Choice` rerank over the same 20 candidates, model pinned to `jev-1.13.0`; no comparator model or paid external API.
- **Primary metric:** mean nDCG@10, paired per-query against BM25 order.
- **Secondary metric:** top-1 hit rate (candidate at rank 1 is relevant), paired per-query against BM25.
- **Bar:** treatment passes only if mean nDCG@10 improves by at least 0.05 **and** top-1 hit rate improves by at least 0.10 absolute; otherwise report fail/no-ship. The bar and N are fixed before calls.
- **Paired test:** Wilcoxon signed-rank on per-query nDCG@10 differences when available; exact paired McNemar on top-1 outcomes. Report effect, test statistic, p-value, and N.
- **Feasibility:** run `scripts/bar-reachable.py` against this exact items file and refuse live calls without a REACHABLE receipt. Run `scripts/jev-state-size.py` before calls; any over-limit item is excluded only before the receipt and recorded, never scored as a model error.
- **Execution:** `kit/experiment/run.py` detached with checkpointing; each completed row records model id, latency, usage, and status. Stop on 401/402/403; no unbounded retries.
- **Spend:** Jev spend only; record call count and API usage/cost from the receipt. No paid comparator is permitted.
- **Non-claims:** this test does not establish general retrieval quality beyond SciFact test, BM25 top-20, this question design, and the observed eligible N; it does not compare Jev to an LLM.
