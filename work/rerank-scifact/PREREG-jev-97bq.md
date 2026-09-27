# OpenRouter incumbent vs Jev on NFCorpus rerank — jev-97bq

**Frozen before any OpenRouter call.** This is the incumbent arm required by AGENTS.md RULE 14; it does not alter or re-score the committed Jev arm.

reach-mode: mcnemar
n: 234
model: dots-studio/dots-3-note-preview:free

- **Dataset:** public BEIR NFCorpus test split. Use the exact committed candidate states from `candidates-nfcorpus.jsonl` (234 rows; SHA-256 `1ef3835708d8522ed39f2f2bd4018ea07390e403bcfd8e00119580e69860e3ec`) and the same public BEIR archive construction recorded by `receipt-nfcorpus-v2.json`.
- **State and question:** for each query, send the query plus its 20 candidate passages and ask one typed Choice question with the candidate IDs as criteria. The OpenRouter model is the only changed variable. Do not send one-passage states, do not select rows after seeing answers, and do not add a paid comparator.
- **Incumbent:** OpenRouter model `dots-studio/dots-3-note-preview:free`, through the existing `work/openrouter/provider.py` adapter pattern and the official `system-one-adapter-python` client. The `:free` suffix is mandatory and enforced before client creation.
- **Jev comparator:** committed `rows-nfcorpus-v2-jev.jsonl`, model `jev-1.13.0`, 234 answered rows. No new Jev calls in this unit.
- **Primary metrics:** top-1 correctness and mean nDCG@10, computed from the committed qrels and the same BM25 candidate order. Compare per-query OpenRouter and Jev outcomes; report exact two-sided McNemar on top-1 and Wilcoxon signed-rank on per-query nDCG differences, with N and discordant/effect counts.
- **Comparison bar:** report whether the free incumbent ties or beats Jev on both primary metrics under the paired tests; no claim is made if either metric is incomplete, has invalid rows, or the model returns a different candidate ID. The Jev-vs-BM25 bar remains the separate result in `receipt-nfcorpus-v2.json` and is not relabeled as this comparison.
- **Reachability:** use `scripts/bar-reachable.py --mode mcnemar` with this preregistration and the exact 234-row items file to produce a checkpoint gate. The receipt is a feasibility gate only; it is not an outcome or a claim that the incumbent wins.
- **Execution:** use `kit/experiment/run.py` with a bounded, detached, checkpointed runner. Every completed row records the model ID, query ID, selected candidate, latency, and provider usage. Stop on authentication, payment, quota, or repeated transport failure; never retry indefinitely.
- **Cost gate:** record OpenRouter key usage immediately before and immediately after the run through the provider's usage endpoint without printing the key. The run is `$0` only if both account-usage readings are unchanged and every row model ID ends in `:free`; otherwise report the observed usage delta and do not call it zero-cost.
- **Non-claims:** this is one free model on this 234-query NFCorpus slice. It does not establish general LLM quality, general OpenRouter availability, or Jev superiority outside this frozen state/question design.
