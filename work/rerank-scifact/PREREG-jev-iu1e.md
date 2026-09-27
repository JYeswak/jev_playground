# Jev vs BM25 rerank preregistration — jev-iu1e

**Amendment to `8fe1624d`; amendments `27148544`, `95206ed9`, `b4085d73`; frozen before the valid NFCorpus rerun.**

reach-mode: mcnemar

- **Dataset:** public BEIR NFCorpus test split, qrels and corpus. This experiment does not use the previously scored SciFact items. The committed candidate file contains every NFCorpus test query whose deterministic BM25 top-20 contains at least one positive qrel.
- **BM25:** stdlib implementation, document text `title + " " + text`, lower-case `[a-z0-9]+` tokens, Robertson/Sparck Jones IDF, `k1=0.9`, `b=0.4`, stable corpus-order tie break. The public archive SHA and candidate-file SHA are recorded in the receipt.
- **Items:** all eligible NFCorpus test queries under that exact construction, N=234. The run MUST refuse if the candidate file does not contain exactly 234 rows or the reach receipt does not match its SHA. No query is selected after seeing Jev answers.
- **Baseline:** BM25 candidate order, top-20 per query.
- **Treatment:** one Jev Choice call per query, with the state containing the query and all 20 candidate passages and the criteria keyed by the 20 candidate IDs; model pinned to `jev-1.13.0`; Jev only, no OpenRouter or other comparator. Expected valid live calls: N=234.
- **Primary metric:** mean nDCG@10, paired per-query against BM25 order.
- **Secondary metric:** top-1 hit rate (rank-1 candidate is relevant), paired per-query against BM25.
- **Bar:** pass only if mean nDCG@10 improves by at least 0.05 **and** top-1 hit rate improves by at least 0.10 absolute. The bar and N are fixed before calls; the +0.10 bar intentionally exceeds the prior SciFact +0.091 observed effect.
- **Paired tests:** exact two-sided McNemar on top-1 correctness and Wilcoxon signed-rank on per-query nDCG@10 differences. Report discordant counts, statistic, p-value, effect, and N.
- **Reachability:** `scripts/bar-reachable.py --mode mcnemar` MUST report REACHABLE for tasks=234, comparator_exact=136, and 24 additional Jev-only top-1 wins with zero losses (the +0.10 bar, rounded up from 23.4, has p<0.05). No rate-mode receipt is valid for this paired bar.
- **Feasibility:** run `scripts/jev-state-size.py` against the exact generated states and refuse live calls for any over-limit item; excluded items are recorded before calls and never scored as model errors.
- **Execution:** `kit/experiment/run.py` detached with checkpointing; each completed row records model id, latency, usage, and status. Stop on 401/402/403; no unbounded retries.
- **Spend:** Jev spend only; receipt records calls, input/output tokens, and billed cost. The earlier 4,680-call invalid one-passage implementation is retained as an invalid transport incident, not scored.
- **Non-claims:** this tests only NFCorpus test queries eligible under this BM25 top-20 construction and this Jev question; it does not establish general retrieval quality or compare Jev with an LLM.
