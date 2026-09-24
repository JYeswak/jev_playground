# The shipped `jev_rerank` tool on BEIR SciFact (bead `jev-k9z.7`)

AmberFinch (task agent RubricSciFact), 2026-09-24. Lane: LIVE, TypeSafe only. Model `jev-1.13.0`
on every response. N = 300 queries x 20 passages x 3 runs.

**Question.** The omp tool `jev_rerank` asks one 4-level Score question per passage, with all 20
passages in the state. On BEIR SciFact, the set where the one-passage Noul question passed
(`jev-nssg`, `rerank-beir-scifact-20260924.md`), does the tool's question beat BM25 order, and
does it lose to the Noul question?

**Bar.** `rerank-tool-scifact-prereg-20260924.md`, committed and pushed as `dfc5fe9` at
2026-09-24T22:10:50Z. The first live call came after that, at 22:11:12Z. The bead's decision rule
is restated verbatim there. Nothing in the prereg changed after data. One later commit touched the
driver: `0b06c0f` (22:15:37Z) changed the selftest's fake key string to `test-key`, because CI's
`30-no-secrets` gate read it as a key. It changes no live code path.

**Code under test.** `rerank` (`work/nev-rerank/src/rank.ts`, blob `fce9a35`) with `liveAsker`
(`work/nev-rerank/src/live.ts`, blob `74232da`), unchanged, called by
`work/rerank-tool-scifact/run.mjs`. That is the same pair `.omp/tools/jev-rerank.ts` calls.
Passages went in BM25 order as `title\ntext`. 4 queries were in flight; within a query the 20
calls ran one after another, one attempt each, with a 20 s timeout.

## Runs

| run | window (UTC) | queries ordered | Jev calls | non-200 | resume pass | input tokens | rows commit |
|---|---|---:|---:|---:|---:|---:|---|
| tool | 22:11:12 to 22:14:56 (223 s) | 300/300 | 6,000 | 0 | 0 queries | 50,609,780 | `efcbe5d` |
| tool-run2 | 22:15:13 to 22:19:08 (236 s) | 300/300 | 6,000 | 0 | 0 queries | 50,609,780 | `5409edb` |
| tool-run3 | 22:24:47 to 22:30:17 (330 s) | 300/300 | 6,000 | 0 | 0 queries | 50,609,780 | `cb1025d` |

- **Failed queries per run: 0, 0, 0.** No query came back `ordered=false`, so no resume pass ran
  and no run is near the NOT-SCORED line of 3.
- **Run 3 was interrupted once.** The harness's 300 s shell timeout killed the first invocation
  after 281 queries had been written (last row 22:29:46.657Z). The same command, rerun at
  22:29:58Z, scored the 19 queries with no row, as the prereg's resume rule says. Those 19 were
  first attempts, not retries. The calls the killed process had in flight made no row and are not
  counted. There were at most 4 queries in flight, so at most 76 calls [INFERENCE: from the
  concurrency, not measured]. The 330 s window includes the roughly 11 s gap.
- **Wall time:** 223 + 236 + 330 = 789 s across the three runs. The median query took
  2.8 s, 2.9 s and 4.0 s.
- **Spend, measured from the wire.** The tool's return value carries no usage. A wrapper on
  `globalThis.fetch` read the server's `usage.input_tokens` from each response. It recorded
  50,609,780 input tokens per run, an average of 8,435 tokens per call. That is 151,829,340 across
  the three runs, at $0.042 per million input tokens (output is free,
  `docs-mirror/typesafe/models.md:13`): **$2.13 per run and $6.38 in total**, plus the unrecorded
  in-flight calls from the run-3 kill. The Noul arms took 4,738,937 tokens per run for the same
  6,000 calls, about 10.7 times fewer. Each tool call carries all 20 passages; each Noul call
  carries one.
- **No comparator model was called.** Every call went to `api.typesafe.ai`. The process ran with
  `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `OPENROUTER_API_KEY` and `OPENAI_API_KEY` removed
  (`env -u`). The BM25 order and the committed Noul rows are the only comparators.

Rows (sha256), ids and scores only, with no query or passage text:
- `rows-tool.jsonl` `82056f0266df4562e990cc9cd5baed37817115108b25a75595ef597f15a3bc6a`
- `rows-tool-run2.jsonl` `f90b9c77cb3114996181aec1664cfdf243505bdf69a1c596766bbe0c45905d7b`
- `rows-tool-run3.jsonl` `a297ffc1af9529b45fc4762c2474e845d11f1acd46e0f6d63ec718b0155e95fd`

## Result

| run | nDCG@10 | Recall@10 | (a) vs BM25 nDCG@10: diff [95% interval] | label |
|---|---:|---:|---|---|
| BM25 order | 0.6762 | 0.8013 | | |
| tool | 0.7645 | 0.8454 | +0.0883 [+0.0632, +0.1167] | WIN |
| tool-run2 | 0.7646 | 0.8454 | +0.0884 [+0.0629, +0.1167] | WIN |
| tool-run3 | 0.7692 | 0.8454 | +0.0930 [+0.0677, +0.1209] | WIN |
| Noul jev / run2 / run3 (jev-nssg) | 0.7623 / 0.7641 / 0.7637 | 0.8421 | | |

Recall@10 vs BM25 is +0.0441 [+0.0238, +0.0673], a WIN in all three runs. It is reported only;
the rule reads nDCG@10.

**(b) tool vs Noul, nDCG@10, the 9 pairings: TIE in all 9.** The point differences run from
+0.0004 to +0.0068. Every interval contains 0: the lowest lower bound is -0.0097 and the highest
upper bound is +0.0187. **LOSE in 0 of 9.** On Recall@10 all 9 are TIE (+0.0033, one query better,
none worse).

**Outcome by the fixed rule: KEEP.** (a) is WIN in all 3 runs, and (b) is LOSE in none. The tool
keeps its question. No follow-up is filed to switch it.

## Keyless re-score

`python3 work/rerank-tool-scifact/score.py` prints the block below byte-for-byte. It needs no
key and no network; it reads the committed rows, `candidates.jsonl` and the `jev-nssg` Noul rows,
and imports `work/rerank-scifact/score.py` for the metrics and the bootstrap.
`python3 work/rerank-tool-scifact/score.py --check-receipt docs/demos/upstream-repro/rerank-tool-scifact-20260924.md`
checks the match and prints `RECEIPT MATCH`.

<!-- rescore:begin -->
```text
queries=300 candidates_sha256=2cf3a9a96a12253a76095f5505dc475dcae5eb64b5dd29b2ed36de9290fe83e8

arm            nDCG@10  Recall@10
BM25 order     0.6762   0.8013
noul jev       0.7623   0.8421
noul jev-run2  0.7641   0.8421
noul jev-run3  0.7637   0.8421
tool           0.7645   0.8454
tool-run2      0.7646   0.8454
tool-run3      0.7692   0.8454

run        window(UTC)        span_s  http_calls  non200  input_tokens  q_ms p50/p95  first_pass_unordered  resumed  unordered_after_resume  models  reasons
tool       22:11:12-22:14:56   223.4        6000       0      50609780  2818/3950                     0        0  0 []  jev-1.13.0  -
tool-run2  22:15:13-22:19:08   235.8        6000       0      50609780  2916/4486                     0        0  0 []  jev-1.13.0  -
tool-run3  22:24:47-22:30:17   330.2        6000       0      50609780  3993/6849                     0        0  0 []  jev-1.13.0  -

(a) tool vs BM25 order: diff [95% interval] label queries better/worse/equal
  ndcg10
    tool                   +0.0883 [+0.0632, +0.1167] WIN  79/17/204
    tool-run2              +0.0884 [+0.0629, +0.1167] WIN  80/19/201
    tool-run3              +0.0930 [+0.0677, +0.1209] WIN  79/17/204
  recall10  (reported, not in the rule)
    tool                   +0.0441 [+0.0238, +0.0673] WIN  18/0/282
    tool-run2              +0.0441 [+0.0238, +0.0673] WIN  18/0/282
    tool-run3              +0.0441 [+0.0238, +0.0673] WIN  18/0/282

(b) tool vs Noul: diff [95% interval] label queries better/worse/equal
  ndcg10
    tool vs jev            +0.0021 [-0.0076, +0.0136] TIE  15/15/270
    tool vs jev-run2       +0.0004 [-0.0094, +0.0118] TIE  11/16/273
    tool vs jev-run3       +0.0008 [-0.0090, +0.0121] TIE  14/18/268
    tool-run2 vs jev       +0.0022 [-0.0082, +0.0141] TIE  17/17/266
    tool-run2 vs jev-run2  +0.0005 [-0.0097, +0.0121] TIE  13/17/270
    tool-run2 vs jev-run3  +0.0009 [-0.0096, +0.0126] TIE  16/20/264
    tool-run3 vs jev       +0.0068 [-0.0027, +0.0187] TIE  18/13/269
    tool-run3 vs jev-run2  +0.0051 [-0.0048, +0.0168] TIE  18/14/268
    tool-run3 vs jev-run3  +0.0055 [-0.0048, +0.0174] TIE  19/17/264
  recall10  (reported, not in the rule)
    tool vs jev            +0.0033 [+0.0000, +0.0100] TIE  1/0/299
    tool vs jev-run2       +0.0033 [+0.0000, +0.0100] TIE  1/0/299
    tool vs jev-run3       +0.0033 [+0.0000, +0.0100] TIE  1/0/299
    tool-run2 vs jev       +0.0033 [+0.0000, +0.0100] TIE  1/0/299
    tool-run2 vs jev-run2  +0.0033 [+0.0000, +0.0100] TIE  1/0/299
    tool-run2 vs jev-run3  +0.0033 [+0.0000, +0.0100] TIE  1/0/299
    tool-run3 vs jev       +0.0033 [+0.0000, +0.0100] TIE  1/0/299
    tool-run3 vs jev-run2  +0.0033 [+0.0000, +0.0100] TIE  1/0/299
    tool-run3 vs jev-run3  +0.0033 [+0.0000, +0.0100] TIE  1/0/299

(a) nDCG@10 labels: WIN WIN WIN  WIN on all 3: yes
(b) nDCG@10 labels: TIE TIE TIE TIE TIE TIE TIE TIE TIE  LOSE 0/9
OUTCOME: KEEP
```
<!-- rescore:end -->

## NO-CLAIM

- This does not say the tool's question beats the Noul question. All 9 pairings are TIE. The two
  questions give the same ranking quality on this set within the interval.
- It does not say the tool is the cheaper choice. Per run it spent about 10.7 times the Noul
  arm's input tokens for the same 6,000 calls, because each call carries all 20 passages.
- One public benchmark: BEIR SciFact, 300 queries, a BM25 top-20 shortlist. One model pin
  (`jev-1.13.0`). Three runs in one 20-minute window. One passage format (`title\ntext`).
- This is reranking of the top 20 on this corpus, not retrieval, and not other domains. On our
  grep corpus the same question failed its bar (`jev-k9z.1`, 0.2828 < 0.3242), and this result
  does not overturn that.
- This measures `rerank()` with `liveAsker`, the functions the tool calls. It did not go through
  the omp tool host's `execute()` wrapper, which adds text formatting and a try/catch around the
  same call.
- The 3-in-a-row nDCG@10 WIN is a live measurement (N=300 x 3), not an offline claim. The rule
  was fixed by the bead before any call. pane 1's non-author check is pending; the bead stays
  in_progress.
