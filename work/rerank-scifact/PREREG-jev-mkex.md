# Jev top-1 rerank confirmation — jev-mkex

**Amendment to `3bea1ec6`; frozen before any live call.**

reach-mode: mcnemar

- **Dataset:** public BEIR FiQA-2018 test split, qrels and corpus; this is a second BEIR set for the NFCorpus result and is not authored by this experiment.
- **Archive:** FiQA zip SHA `32c7df99ed21252fdfb2cf3f5673502a8d245ee0c44c4a133570d92ce2b3ad02`.
- **BM25:** stdlib implementation, document text `title + " " + text`, lower-case `[a-z0-9]+` tokens, Robertson/Sparck Jones IDF, `k1=0.9`, `b=0.4`, stable corpus-order tie break.
- **Items:** all FiQA test queries whose deterministic BM25 top-20 contains at least one positive qrel and whose full 20-passage state is in the FITS band of `scripts/jev-state-size.py`: N=329. Twenty near-limit queries were excluded before calls by the preregistered feasibility rule; no query is selected after seeing Jev answers. Candidate file SHA `9c1ae1500379413ab14b54275743a3727e95c91523d8ee17433919960d2972cf`; baseline top-1 exact count is 129/329. The original 349-row candidate manifest SHA is `e1411e654f7f02e2751ce8079d109bbe4b84cb31feb44120d9c4a41c38dccec6`.
- **Treatment:** one Jev Choice call per query, with the query and all 20 candidate passages in state and criteria keyed by candidate IDs; model pinned to `jev-1.13.0`; Jev only, no comparator.
- **Primary confirmatory metric:** top-1 hit rate, paired against BM25 order.
- **Confirmatory bar:** Jev top-1 gain >= +0.05 absolute (at least 17 Jev-only wins over BM25 at N=329) **and** exact two-sided McNemar p<0.05. Both conditions are required.
- **Secondary descriptive metric:** report nDCG@10 for BM25 and Jev, but do not use it for the confirmatory pass/fail bar.
- **Reachability:** `scripts/bar-reachable.py --mode mcnemar` MUST report REACHABLE for tasks=329, comparator_exact=129, and 17 additional Jev-only wins with zero losses. This is bar headroom, not the true BM25-missed headroom: the true eligible-set headroom is 200 queries (329 - 129). No rate-mode receipt is valid.
- **Execution:** use the shared detached `kit/experiment/run.py` gate with checkpointing; each row records model, latency, and usage; stop on 401/402/403; no unbounded retries.
- **Feasibility:** the 20 excluded near-limit states are recorded before calls and never scored as model errors; the executed eligible states must pass the FITS gate.
- **Spend:** Jev spend only; receipt records calls, input/output tokens, latency, and input cost. No paid comparator or OpenRouter call.
- **Non-claims:** this confirms only the top-1 comparison on this FiQA eligible subset and this BM25/Choice design; nDCG is descriptive and no general retrieval claim follows from one confirmation set.
