# jev-d92: clone sweep for paired scorers — exhausted, negative result

Pane 3 (muse), 2026-09-19. Harvested-from:76e1557. All trees read-only, never
edited. Method: every `results/` dir, then a `probability` grep over all
`*.json/jsonl/csv` (minus node_modules/target), then a per-clone data-file survey
for the remainder. Offline replay only, zero live calls.

## Table: clone -> best candidate -> usable?

| Clone | Best candidate | Usable? Why |
|---|---|---|
| bitnovus/jev-spam-eval | `results/*_oof.jsonl`, `ood_tfidf_predictions.jsonl` (4-7k items, label+prob) | NO — same project as the existing three pairs; bead requires different clone |
| Gaurav-Gosain/jev-sec-bench | injection ctx/noctx (662 aligned pairs) | USED (jev-4uy) — the only paired item-level scores in the tree |
| anessbelbati/jev-rerank-bench | `candidates/*.jsonl` (bm25 per passage + relevance) | NO — one scorer (bm25); Jev per-passage scores are runtime-only (needs key) |
| anisselbd/jev-phishing-bench | `metrics.json` (2000 emails) | NO — aggregates only (tp/fp/fn + CIs); no per-item arrays |
| TokenTrim/jev-agent-failure-benchmark | `results/run/jev/text.jsonl` | NO — one judgment per question, no second scorer |
| iammrduncan/typesafe-ai-benchmark | `live.json` / `local-stub.json` | NO — latency aggregates |
| typesafe-ai/system-one-adapter-python | `tests/cassettes/` (4 backends × same questions) | NO — n≈2 distinct questions; conformance cassettes, not classification |
| 0xNatoshi/jev-codex-router | `tasks.json` + backtest results | NO — expects without scorer probabilities |
| gargpratyush/jev-router | tests | NO — policy unit tests, no scored items |
| devanshbatham/commit-miner | classified CSVs | NO — single classifier |
| Dicklesworthstone/skillranker | — | NO — CLI tool, no scored corpus |
| browser-use/jev-ultrafast | `docs/*measurement.json` | NO — single-flight timing logs |
| AbdelStark/s1-rs | `tests/golden/triage.json` | NO — golden fixture, single system |
| tamaratran/fast-jev-compaction | `hooks/hooks.json` | NO — hook config, not scores |
| thruwire / jkudish / Anil-matcha / NiazMorshed2007 | — | NO — no data files at all |

## Conclusion

R22's "3 of 22" is now 22 of 22 for the results-dir + data-grep + survey
definition of searched. The second-project pair does not exist in committed
form anywhere in this tree. Recipe 4 stays at: spam-eval pairs (1 project) +
sec-bench ctx-ablation (1 pair). The phi-0.5 question cannot be fed more committed
data without (a) running a keyed rerank bench to produce Jev per-passage scores,
(b) the absent themsquared clone, or (c) new live calls — all outside this bead.
