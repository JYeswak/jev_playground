# Jev vs BM25 rerank preregistration — jev-iu1e

**Amendment to `8fe1624d`; frozen before the NFCorpus live call.**

- **Dataset:** public BEIR NFCorpus test split, qrels and corpus. This experiment does not use the previously scored SciFact items. The committed candidate file will contain every NFCorpus test query whose deterministic BM25 top-20 contains at least one positive qrel.
- **BM25:** stdlib implementation, document text `title + " " + text`, lower-case word tokens, Robertson/Sparck Jones IDF, `k1=0.9`, `b=0.4`, stable corpus-order tie break. The builder records the public zip SHA and candidate-file SHA.
- **Items:** all eligible NFCorpus test queries, expected N=239 from the pinned BM25 construction; the run MUST refuse if the built candidate manifest does not contain exactly 239 rows or the reach receipt does not match its SHA. No query is selected after seeing Jev answers.
- **Baseline:** BM25 candidate order, top-20 per query.
- **Treatment:** Jev Choice rerank over the same 20 candidates, model pinned to `jev-1.13.0`; Jev only, no OpenRouter or other comparator.
- **Primary metric:** mean nDCG@10, paired per-query against BM25 order.
- **Secondary metric:** top-1 hit rate (rank-1 candidate is relevant), paired per-query against BM25.
- **Bar:** pass only if mean nDCG@10 improves by at least 0.05 **and** top-1 hit rate improves by at least 0.10 absolute. The bar and N are fixed before calls; the +0.10 bar intentionally exceeds the prior SciFact +0.091 observed effect.
- **Paired tests:** exact two-sided McNemar on top-1 correctness and Wilcoxon signed-rank on per-query nDCG@10 differences. Report discordant counts, statistic, p-value, effect, and N.
- **Reachability:** `scripts/bar-reachable.py --mode mcnemar` MUST report REACHABLE for the planned N and the baseline exact count, with 24 additional Jev-only top-1 wins and zero losses (the preregistered +0.10 bar, rounded up from 23.9, reaches p<0.05). No rate-mode receipt is valid for this paired bar.
- **Feasibility:** run `scripts/jev-state-size.py` against the exact generated states and refuse live calls for any over-limit item; excluded items are recorded before calls and never scored as model errors.
- **Execution:** `kit/experiment/run.py` detached with checkpointing; each completed row records model id, latency, usage, and status. Stop on 401/402/403; no unbounded retries.
- **Spend:** Jev spend only; receipt records calls, input/output tokens, and billed cost. No paid comparator is permitted.
- **Non-claims:** this tests only NFCorpus test queries eligible under this BM25 top-20 construction and this Jev question; it does not establish general retrieval quality or compare Jev with an LLM.
