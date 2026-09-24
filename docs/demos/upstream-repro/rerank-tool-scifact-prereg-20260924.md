# Preregistration: the shipped `jev_rerank` tool on BEIR SciFact (bead `jev-k9z.7`)

AmberFinch (task agent RubricSciFact), 2026-09-24. Committed and pushed before the first live
call of this unit. Nothing below changes after data. The receipt is
`docs/demos/upstream-repro/rerank-tool-scifact-20260924.md`.

**Question.** The omp tool `jev_rerank` (`.omp/tools/jev-rerank.ts`) asks one 4-level Score
question per passage, with every passage in the state. `jev-nssg` (`cf70e28`,
`rerank-beir-scifact-20260924.md`) passed on BEIR SciFact with a different question: one Noul per
passage, state holding that passage only. Does the question the tool ships hold on the same 300
queries, the same BM25 top-20 and the same qrels?

## Decision rule, verbatim from `br show jev-k9z.7`

> DECISION RULE (fixed here, before any call; the preregistration may add detail but not change
> it): scorer = work/rerank-scifact/score.py machinery (binary-gain nDCG@10, paired bootstrap 2,000
> resamples, seed 20260924, WIN/LOSE/TIE by the 95% interval). (a) tool vs BM25 order on each of 3
> runs; (b) tool vs each committed Noul run (rows-jev, rows-jev-run2, rows-jev-run3), 9 pairings. KEEP
> the tool's question if (a) is WIN on all 3 and (b) is LOSE on none. SWITCH (file a follow-up to move
> jev_rerank to the Noul question) if (a) is not WIN on all 3, or (b) is LOSE on all 9. Anything else
> is MIXED and is reported as numbers, with no switch. A query the tool cannot order after one resume
> pass is scored as the tool returns it (BM25 order, ordered=false) and counted; more than 3 such
> queries in any run = that run NOT-SCORED.

## Operational detail (adds, does not change)

**Code under test, pinned.** `rerank` from `work/nev-rerank/src/rank.ts` (blob `fce9a35`) with
`liveAsker` from `work/nev-rerank/src/live.ts` (blob `74232da`), passed to `rerank` exactly as the
tool passes it. `liveAsker` calls `askJevScore` in `work/jev-client/src/index.ts` (blob `2a6b620`)
once per passage, sequentially, `model jev-1.13.0`, timeout 20 s, SDK retry off (`maxRetries 0`).
Tool file `.omp/tools/jev-rerank.ts` blob `45b7982`. Last commit touching these: `5d63394`.
`@typesafe-ai/sdk` 0.6.0 from `work/sdk`. The driver restates no rubric, question text or
expected-level reduction; none of those files is edited by this unit.

**Inputs.** `work/rerank-scifact/candidates.jsonl` sha256
`2cf3a9a96a12253a76095f5505dc475dcae5eb64b5dd29b2ed36de9290fe83e8` (qid, BM25 top-20 with scores,
qrels ids). Text from BEIR `scifact.zip` sha256
`536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165`, read at run time; the driver
refuses on a mismatch. No query or passage text is committed (license decision in the jev-nssg
receipt).

**Passage string.** `title + "\n" + text`, one string per candidate, in BM25 order. Every one of
the 5,183 abstracts has a non-empty title and text. The query string is the BEIR query text. So the
tool's state is `{query, passages: {p01..p20}}`, p01 the BM25 rank-1 doc.

**Runs.** `tool`, `tool-run2`, `tool-run3`, run in that order, each in the foreground of this
session, attended, never in a background loop:

```
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  env -u ANTHROPIC_API_KEY -u XAI_API_KEY -u OPENROUTER_API_KEY -u OPENAI_API_KEY \
  node work/rerank-tool-scifact/run.mjs <run>
```

No comparator model is called. The comparator keys Infisical injects are removed from the process.

**Concurrency.** 4 queries in flight. Inside a query the 20 calls are sequential, as `liveAsker`
makes them. 4 keeps the rate under the documented 1,200 requests per minute
(`docs-mirror/typesafe/models.md:14`), because the shipped path does not retry a 429.

**Rows.** `work/rerank-tool-scifact/rows-<run>.jsonl`, one JSON line per query and attempt:
`qid, run, attempt, ordered, reason, calledModel, truncated, ranking` (the returned order as
`{doc, score}`, score `null` when the tool returned none), `wallMs` (around `rerank()`), `ts`
(completion time), `calls`, `status` (HTTP status counts), `inputTokens`, `models`. The last four
come from a wrapper on `globalThis.fetch` that counts each request and reads the server's
`usage.input_tokens` and `model` from a clone of the response. The wrapper changes no request and no
response. The tool's own return value carries none of these numbers.

**Resume.** A run first scores every query that has no attempt-1 row. Then, once, every query
whose attempt-1 row is `ordered=false` and which has no attempt-2 row gets attempt 2. The scorer
uses attempt 2 where it exists. There is no third attempt. Rerunning the same command after a
crash continues where the file stops and never repeats a finished attempt.

**Stop.** A row whose reason is `unconfigured`, `sdk-missing` or `billing-hold`, or which saw an
HTTP 402, stops dispatch. The run exits 4 and makes no further calls. No loop waits for credits.

**Scoring.** `python3 work/rerank-tool-scifact/score.py` imports `work/rerank-scifact/score.py`
(sha256 `c3d8b869...a0`) for `ndcg10`, `recall10`, `per_query`, `arm_nouls` and `compare`. The
tool's metrics come from the returned order. BM25 and the Noul arms come from that module on the
committed rows (`rows-jev.jsonl` `40289951...b93b`, `rows-jev-run2.jsonl` `afd9eb3c...88de`,
`rows-jev-run3.jsonl` `52c1a252...31f7`). The labels in (a) and (b) are on nDCG@10, the bead's
metric. Recall@10 is printed and is not part of the rule.

**Reading of the rule where a run is NOT-SCORED.** A NOT-SCORED run has no label. It is therefore
not a WIN in (a), and its three (b) pairings carry no LOSE. That is the literal text. It is written
down here so the reading cannot be chosen after the data.

**Outcome actions.** KEEP: no change to the tool. SWITCH: file a follow-up bead to move
`jev_rerank` to the Noul question; this unit does not edit the tool. MIXED: numbers only.

**Spend.** No call budget (AGENTS.md, lifted 2026-09-21). The receipt states the calls, the
measured input tokens and the price from `docs-mirror/typesafe/models.md` ($0.042 per million input
tokens; output free).

## Keyless checks before the first call

- `node work/rerank-tool-scifact/run.mjs --selftest` with no key: PASS. A fake asker on 2
  queries maps ids back to docs and writes no text. A failed query gets exactly one resume. The
  shipped `liveAsker` with no key gives `ordered=false reason=unconfigured`, 0 HTTP calls, no
  throw, and stops dispatch. A fake transport counts 20 calls and the usage per query.
- `python3 work/rerank-tool-scifact/score.py --selftest`: PASS. The oracle order gives KEEP.
  Constant scores reproduce BM25 order exactly and give SWITCH. 3 unordered queries are scored; 4
  make the run NOT-SCORED. The rule table passes 7/7 cases. A doc outside the shortlist is refused.
