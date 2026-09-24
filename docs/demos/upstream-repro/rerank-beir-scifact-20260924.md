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

Bar commit `6203f00` (pushed) is an ancestor of this results commit. Nothing above
`## Result` changed. Jev was not called.

**Jev: BLOCKED-until-credits. Not FAIL. Not run.** No Jev rows. No
`NEGATIVE_EVIDENCE.md` row, because Jev was not measured against BM25. The verbatim
402 is in the bar. When credits return, `run.py jev`, `jev-run2`, and `jev-run3`
under this same bar.

**grok, live, 2026-09-24T07:26:40Z to 07:51:07Z.** Three runs, 6,000 pairs each,
model `xai/grok-4.20-0309-non-reasoning` on every success row. Input tokens are
5,294,469 on each run, so the prompts matched. One unscored smoke call before the
bulk (qid 1, doc 34386619, noul 0.0, 935 in / 7 out, 966 ms) is not in the rows;
the bulk asked that pair again.

| Arm | nDCG@10 | Recall@10 | answered | distinct nouls | p50/p95 pair ms | tokens in/out |
|---|---:|---:|---:|---:|---|---|
| BM25 order | 0.6762 | 0.8013 | | | | |
| grok | 0.7012 | 0.8091 | 6000/6000 | 12 | 557/805 | 5,294,469 / 52,127 |
| grok-run2 | 0.6997 | 0.8158 | 6000/6000 | 12 | 554/794 | 5,294,469 / 52,262 |
| grok-run3 | 0.6969 | 0.8214 | 6000/6000 | 12 | 541/766 | 5,294,469 / 52,183 |
| oracle top-20 | 0.8492 | 0.8454 | | | | ceiling, not an arm |

Run 1 wrote one `TypeSafePermissionDeniedError: 403 I can't help with that request`
(qid 115, doc 33872649) and the resume pass answered it. Run 2 wrote one
`TypeSafeInternalServerError: 502` (qid 1359, doc 13619127) and the resume pass
answered it. Run 3 was clean on the first pass. Those error lines remain in the
files; the scorer skips an error line when a success exists for the pair. Failed
pairs after resume: 0.

**grok vs BM25, the 3 pairings** (bootstrap as frozen; Jev pairings not scored):

| Metric | grok | grok-run2 | grok-run3 | all-pairings |
|---|---|---|---|---|
| nDCG@10 | +0.0250 [+0.0008, +0.0519] WIN (47/39/214) | +0.0235 [+0.0002, +0.0486] WIN (47/38/215) | +0.0207 [−0.0057, +0.0477] TIE (46/52/202) | WIN RETRACTED 2/3 |
| Recall@10 | +0.0078 [−0.0089, +0.0258] TIE (8/4/288) | +0.0144 [+0.0042, +0.0283] WIN (7/0/293) | +0.0201 [+0.0062, +0.0376] WIN (10/1/289) | WIN RETRACTED 2/3 |

No grok run is a LOSE to BM25 on either metric. The nDCG@10 win does not stand:
run 3's interval includes 0. Direction favours grok on nDCG@10 in all three runs
(point estimates +0.021 to +0.025, against an oracle headroom of 0.173). Twelve
distinct noul values across 6,000 pairs: the adapter's probability mode is coarse
here. That is descriptive, not a pass-rule claim.

**Unit verdict: BLOCKED**, not PASS and not FAIL. The pass rule needs the three
Jev runs.

**Spend.** 18,000 scored grok calls plus 2 retried failures plus 1 unscored smoke.
Recorded success-row tokens: 15,883,407 input / 156,572 output. xAI list price is
not applied here (same boundary as `grok-variance-20260924.md`). No Jev calls.

**Rows** (sha256): `rows-grok.jsonl`
`16fe9d822f90c07a9583ad21457d2fce158656e381ea89166554ce1470364b3f`,
`rows-grok-run2.jsonl`
`3184ed06e777ea76c9ac332eb3cb4ea6bcb225dcfcd54e4ea13893b6169f6025`,
`rows-grok-run3.jsonl`
`805a0e76c7710a4f8e4daefd05eed17371824afc2109ad43c2715cee332a7db1`.
No query or passage text in the rows.

Re-score, no key: `python3 work/rerank-scifact/score.py`.

**NO-CLAIM.** This does not say Jev beats or loses to BM25 or to grok. It does not
say grok beats BM25: that WIN is retracted at 2/3. Three grok runs, one wording,
one shortlist, one afternoon.

## Result, Jev arms (CopperHeron, pane at index 2)

This supersedes the BLOCKED verdict above. TypeSafe credits returned (`jev-1gdi` closed on pane
1's HTTP 200 probe). The bar and everything above `## Result` are unchanged from `6203f00`. The bar
file was clean at `ef1aadc` when each arm ran, so the `jev-8ec2` gate (`call_after_bar`) passed.

**Runs, live, 2026-09-24.** Each arm was run in the foreground with
`upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/rerank-scifact/run.py <arm>`
under `infisical run`, with `typesafe_sdk` 0.7.0, `AsyncTypeSafeClient(model="jev-1.13.0",
retry=RetryPolicy())` and `RERANK_CONCURRENCY` at its default of 16. `ANTHROPIC_API_KEY` and
`OPENAI_API_KEY` were unset for the process.

| Arm | Window (UTC) | Pairs answered | Failed | Model on every row |
|---|---|---:|---:|---|
| jev | 15:13:53 to 15:15:10 | 6000/6000 | 0 | `jev-1.13.0` |
| jev-run2 | 15:16:08 to 15:17:24 | 6000/6000 | 0 | `jev-1.13.0` |
| jev-run3 | 15:17:24 to 15:18:35 | 6000/6000 | 0 | `jev-1.13.0` |

There was no smoke call, no 402 and no resume pass. Pane 1's readout 4 live pass used the same key
at the same time.

**Scores** (`python3 work/rerank-scifact/score.py`, keyless, rc 0):

| Arm | nDCG@10 | Recall@10 | distinct nouls | p50/p95 pair ms | tokens in/out |
|---|---:|---:|---:|---|---|
| BM25 order | 0.6762 | 0.8013 | | | |
| **jev** | **0.7623** | **0.8421** | 99 | 162/416 | 4,738,937 / 132,000 |
| **jev-run2** | **0.7641** | **0.8421** | 99 | 179/375 | 4,738,937 / 132,000 |
| **jev-run3** | **0.7637** | **0.8421** | 99 | 163/334 | 4,738,937 / 132,000 |
| grok | 0.7012 | 0.8091 | 12 | 557/805 | 5,294,469 / 52,127 |
| grok-run2 | 0.6997 | 0.8158 | 12 | 554/794 | 5,294,469 / 52,262 |
| grok-run3 | 0.6969 | 0.8214 | 12 | 541/766 | 5,294,469 / 52,183 |
| oracle top-20 | 0.8492 | 0.8454 | | | ceiling, not an arm |

**Jev vs BM25**, the 3 pairings (frozen bootstrap, 2,000 resamples, `random.Random(20260924)`):

| Metric | jev | jev-run2 | jev-run3 | all-pairings |
|---|---|---|---|---|
| nDCG@10 | +0.0862 [+0.0616, +0.1117] WIN (77/18/205) | +0.0879 [+0.0636, +0.1140] WIN (77/18/205) | +0.0875 [+0.0640, +0.1141] WIN (77/16/207) | **WIN STANDS 3/3** |
| Recall@10 | +0.0408 [+0.0215, +0.0628] WIN (17/0/283) | +0.0408 [+0.0215, +0.0628] WIN (17/0/283) | +0.0408 [+0.0215, +0.0628] WIN (17/0/283) | **WIN STANDS 3/3** |

**Jev vs grok**, the 9 pairings:
- nDCG@10: WIN in all 9. The differences run from +0.0612 to +0.0672, and the lowest interval
  bound is +0.0385. **WIN STANDS 9/9.**
- Recall@10: WIN in all 9. The differences run from +0.0207 to +0.0330, the lowest bound is
  +0.0073, and in no pairing is a query worse for Jev. **WIN STANDS 9/9.**
- No Jev-vs-grok pairing is a LOSE on either metric.

**Unit verdict under the frozen pass rule: PASS.** (1) Jev's nDCG@10 is WIN vs BM25 in all 3 runs.
(2) No Jev-vs-grok pairing is LOSE on nDCG@10 or Recall@10. Jev closes about half the headroom
between BM25 and the oracle reorder (+0.086 of 0.173). No `NEGATIVE_EVIDENCE.md` row, because Jev
beat BM25.

**Spend, from the SDK usage fields.** Every success row carries `resp.usage.input_tokens` and
`output_tokens`. Jev bills input tokens only, at $0.042 per million, and output is free
(`docs-mirror/typesafe/models.md`).
- Each arm: 4,738,937 input tokens, **$0.199**.
- Three arms: 14,216,811 input tokens across 18,000 calls, **$0.597**.
- There were no failed calls and no retried rows. The runner records no retries the SDK made
  internally.
- The grok arms' cost is not applied here, as in the grok section above.

**Rows** (sha256), no query or passage text; fields `qid, doc, arm, model, noul, latencyMs, usage`:
- `rows-jev.jsonl` `40289951dcafcabbb1a7e4b2f03d989542aa99c4302165aa5b9a41d83f5af93b`
- `rows-jev-run2.jsonl` `afd9eb3c5b7c0702f16f497cf13367821e6229ea4291a82a30e058199f0288de`
- `rows-jev-run3.jsonl` `52c1a252da9ade744c4472a7b87fb39cd43c30dbf97c40c18345a58cf27431f7`

**NO-CLAIM.**
- One public benchmark: BEIR SciFact, 300 queries, a BM25 top-20 shortlist.
- One question wording, one model pin (`jev-1.13.0`), three runs in one five-minute window.
- The claim is reranking the top 20 on this corpus, not retrieval, and not other domains.
- The incumbent is grok-4.20 in the adapter's probability mode: 12 distinct nouls, against 99 for
  Jev. A stronger reranker, or grok in another mode, may do better.
- Recall@10 is identical across the three Jev runs; nDCG@10 moves by at most 0.0018.
