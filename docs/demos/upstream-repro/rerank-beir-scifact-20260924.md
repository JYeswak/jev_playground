# Rerank BEIR SciFact: Jev Noul vs BM25 vs grok-4.20 (bead `jev-nssg`)

QuietHarbor (pane 3, grok), 2026-09-24. Pattern: rerank after fast search.
Doc: `docs-mirror/typesafe/cookbooks/rerank_typesafe.md` (one Noul per candidate, no
candidate sees another) and `docs-mirror/typesafe/cookbooks/classifying_rag_passages.md`
(state is `{query, passage}`). Use-case map: Search and retrieval / Ranking
(`docs-mirror/typesafe/concepts/use-case-map.md`).

**Question this unit answers.** On the 300 BEIR SciFact test queries that have qrels,
does reranking the BM25 top-20 by one Noul ("does this passage contain evidence
relevant to the query") beat BM25 order on nDCG@10, and does it beat grok-4.20 asked
the same question? `jev-k9z.1` failed that question on an author-labelled corpus.

## Bar (frozen before any call of this unit)

**Corpus.** BEIR SciFact zip
`https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip`,
sha256 `536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165`,
5,183 abstracts, 300 test queries with qrels (339 relevant pairs). The zip has no
license file. AllenAI `LICENSE.md` (fetched 2026-09-24,
`https://github.com/allenai/scifact/blob/master/LICENSE.md`) licenses claims CC BY 4.0
and abstracts ODC-By 1.0. The HuggingFace card `allenai/scifact` also says CC BY-NC 2.0
and points at that LICENSE.md, which does not say NC. **Decision: do not commit query
or passage text.** Ids, BM25 scores, qrels ids, and model scores are committed. Text is
read from the pinned zip at run time.

**Fast search.** `bm25s==0.3.11`, Lucene BM25, k1 0.9, b 0.4, English stopwords,
English Snowball stemmer, document = title + space + text. Ties break by corpus-file
order. Candidate depth 20. Feasibility, fixed before the first build: full-corpus
nDCG@10 within 0.03 of Anserini BM25 (flat) 0.6789
(`castorini/anserini` `docs/fatjar-regressions/fatjar-regressions-v1.6.0.md`, SciFact
row, column BM25 (flat); fetched 2026-09-24, the table is the nDCG@10 table). Measured
before any model call: **0.6762** (delta 0.0027). Rebuild:
`uv run --script work/rerank-scifact/build.py --check` (byte-identical candidates,
sha256 `2cf3a9a96a12253a76095f5505dc475dcae5eb64b5dd29b2ed36de9290fe83e8`).

**Shortlist, measured before any model call** (`python3 work/rerank-scifact/score.py`):

| | nDCG@10 | Recall@10 |
|---|---:|---:|
| BM25 order of the top-20 (the floor) | 0.6762 | 0.8013 |
| oracle reorder of the same 20 (ceiling, descriptive) | 0.8492 | 0.8454 |

nDCG@10 of the top-20 prefix equals full-corpus nDCG@10, because nDCG@10 only reads the
top 10. 282/339 relevant docs are in the top-20. 42/300 queries have no relevant doc in
the top-20 (reranking cannot help them). 23 queries have more than one relevant doc.
Headroom from the floor to the oracle is 0.173 nDCG@10.

**The question, frozen** (`work/rerank-scifact/run.py` `QUESTION`). State =
`{"query", "passage": {"id", "title", "text"}}` for that pair only. One Noul:

- instructions: "Does this passage contain evidence relevant to the query?"
- true: "The passage is on the query's subject and states evidence a reader could use in assessing it, whether or not that evidence supports the query."
- false: "The passage is on a different subject, or states nothing about the query."

Relevance is not support. A contradicting abstract is still relevant. Rerank = the 20
sorted by noul, highest first; equal nouls keep BM25 order (stable sort).

**Arms.**

| Arm | Model | How | Rows |
|---|---|---|---|
| BM25 order | none | the shortlist order | `candidates.jsonl` |
| jev, jev-run2, jev-run3 | `jev-1.13.0` | `AsyncTypeSafeClient`, `RetryPolicy()` | `rows-jev.jsonl`, `rows-jev-run2.jsonl`, `rows-jev-run3.jsonl` |
| grok, grok-run2, grok-run3 | `grok-4.20-0309-non-reasoning` | `system-one-adapter` @ `adffc2e`, `AsyncOpenAIProvider(base_url="https://api.x.ai/v1")`, structured outputs, `llm_answer_mode="probabilities"`, `normalize_probabilities=True`, `RetryPolicy()` | `rows-grok.jsonl`, `rows-grok-run2.jsonl`, `rows-grok-run3.jsonl` |

SDK `typesafe_sdk` 0.7.0 @ `0ffd094`. `RetryPolicy()` defaults: max_retries 2, backoff
0.5 doubling to 5.0, jitter 0.25, timeout 30s. One request per pair. A pair still failed
after the runner's retries is scored on the wrong side of its qrels label: noul 0 if
relevant, noul 1 if not.

**Metrics.** nDCG@10 with binary gains, ideal DCG over every relevant doc in the qrels
(including docs outside the top-20). Recall@10 = relevant in the top 10 / relevant in
the qrels. Primary metric is nDCG@10. Recall@10 is reported.

**Paired test.** Over the 300 queries, bootstrap 95% percentile interval of the mean
difference, 2,000 resamples, `random.Random(20260924)`. WIN if the interval is above 0,
LOSE if below, else TIE.

**All-pairings rule.** A WIN or LOSE claim STANDS only if every pairing has that label.

- Jev vs BM25: 3 pairings (one per Jev run).
- grok vs BM25: 3 pairings (one per grok run). Reported either way. It is not a substitute
  for the Jev pass rule.
- Jev vs grok: 9 pairings (3 x 3).

**Pass rule.** PASS only if (1) Jev nDCG@10 is WIN vs BM25 on all 3 Jev runs, and (2) no
Jev-vs-grok pairing is LOSE on nDCG@10 or Recall@10. Otherwise FAIL, and a measured
failure to beat BM25 gets a `NEGATIVE_EVIDENCE.md` row. A missing Jev arm is
**BLOCKED-until-credits, not FAIL**, and does not get that row.

**402 stop.** If a Jev call returns HTTP 402 with the credits message, the runner writes
that one error row, cancels the rest of the queue, and exits 4. It does not retry the
queue. The known verbatim, from `~/.local/state/jev/gate-observe.jsonl` at
2026-09-24T04:19:44.084Z (session `01a0d19d-3d4b-7306-a1e0-d419dc707281`), and repeated
on later rows the same day:

```
http: systemOne HTTP 402: 402 Your organization has no available TypeSafe API credits. Please add more credits and/or set up auto-reload at https://console.typesafe.ai/settings/billing
```

This pane made no Jev call. When credits return, the three Jev arms run under this bar,
unchanged above `## Result`.

**Keyless checks, before any call.**

- `uv run --script work/rerank-scifact/build.py --check` — CHECK PASS, nDCG@10 0.6762.
- `python3 work/rerank-scifact/score.py --selftest` — PASS (oracle WIN, anti-oracle LOSE,
  constant noul reproduces BM25, all-failed scores as the anti-oracle, 8/9 retracts).
- `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/rerank-scifact/run.py --selftest`
  — PASS (question text, state keys, row has no passage text, 402 detector). No key, no network.

## Result

**Jev: BLOCKED-until-credits. Not FAIL. Not run.** The three Jev arms were not called.
The 402 above has stood since 04:19Z. No `NEGATIVE_EVIDENCE.md` row: there is no
measurement of Jev against BM25.

**grok: NOT_RUN at the bar commit.** The three grok arms start only after this file is
committed. Re-score, no key: `python3 work/rerank-scifact/score.py`.
