# jev-k9z.1 live rerank advisory (2026-09-24, pane 4 MistyTurtle)

Bead `jev-k9z.1` (blocked 09-21 on spend; spend gate lifted). Advisory order
only; not a blocking filter.

## BAR (preregistered — predates the first live call)

- Corpus: `work/nev-rerank/pairs.jsonl`, 219 rows mined from agent
  transcripts (unauthored). Full 219 (affordable; matches prior run).
- Metric (same as `rank.test.mjs` + prior run): top-1 hit rate
  (`top_file === label`), exact binomial 95% CI.
- Floors, same rows, keyless, run now: lexical `lexicalOrder` top-1
  71/219 = 0.3242 (`/tmp/k9z1-constant.mjs`); random-order expectation
  54.3/219 = 0.2480. File provenance `label_rank===1` (raw grep order, not
  lexical): 58/219 — reported for context, NOT the bar.
- Pass rule: Jev top-1 lower-CI > 0.3242. Pinned `jev-1.13.0`.
- Incumbent arm: zero-API lexical ranker (no TF-IDF ranker exists in
  `rank.ts`; lexical IS the identical-rows incumbent).
- Per call: latency (p50/p95/max), tokens, cost per call (1 call/query
  regardless of candidate count; candidates p50 5, max 20; MAX_PASSAGES 30
  is the per-call cap, not the corpus shape).

## Constant first (keyless, before any call)

n=219 lexical-top1=71 (0.3242) random-expect=54.3. A Jev number below 71
ties a word-count.


## Results (2026-09-24, model jev-1.13.0, 219 rows, 2 full runs)

Runner `/tmp/k9z1-run.mjs` (score-pairs logic, OUT /tmp, concurrency 6).
Run 1 untimed + run 2 with row latencies; tallies from run 2
(`/tmp/k9z1-scores.jsonl`, recomputed by pane 4).

| measure | value |
|---|---|
| rows ordered | 219/219, zero failures/throws |
| Jev top-1 | 75/219 = 0.3425, Wilson 95% CI lower 0.2828 |
| bar (lower-CI > 0.3242) | **FAIL** (0.2828 < 0.3242; +4 rows over lexical, noise) |
| paired McNemar vs lexical | jev-only 38 / lex-only 34, n.s. — confirms the CI verdict |
| latency per row | p50 1073ms / p95 5189ms / max 7278ms / min 223ms |
| calls | 1660 passage-Score calls per run × 2 runs = 3320 |
| tokens / dollars | NOT surfaced (`JevScoreResult`, index.ts:348-358, carries no usage field) — calls + latency stated instead |

## L3 in real omp sessions

Keyless direction: `ordered=false reason=unconfigured NOT_RUN`, input order
returned (observed live in a fresh `--print` session; tool header comment
states the contract).

Keyed positive (`infisical run ... -- omp -p ... --print`, real session):

```
ordered=true calledModel=true
1. [p01 0.917] This runtime frees memory by explicit ownership with no collector.
2. [p02 0.457] This runtime uses a garbage collector to reclaim memory automatically.
```

Keyed negative (single passage; empty array behaves the same): schema
validation refuses without throwing (exit 0, error frame, no exception):
`passages must be at least length 2`. The tool-level `nothing-to-rank`
path is unit-covered (`rank.test.mjs`, one passage never calls the model)
but unreachable through the tool schema — refusal happens one layer out.

## Verdict: bar FAILED, seat not claimed

Jev 75/219 does not clear lexical 71/219 at 95% confidence; paired test
agrees (38/34). The advisory stays advisory, which is what it already is.
The bar is not moved.

## Boundary

One corpus (agent transcripts, unauthored but narrow), one model version,
two full runs Tallied from run 2 only. No TF-IDF ranker exists — incumbent
is lexical by construction. Dollars unpriced (no usage object). No Rust.

Non-author re-score (TopazRaven, pane 3): Jev top-1 75/219 (two methods,
0 mismatches), lexical 71/219 re-ran. Expectations met; bar FAILED stands.

## Rows committed — 2026-09-24

`/tmp/k9z1-scores.jsonl` copied byte-identical (`cmp`) to `work/tmp-rescue/k9z1-scores.jsonl`, sha256 `c1bc3f6ba680172eb4da91e89ea2b0cc941a8f60796a67eb8703d02c1b166413`. The `/tmp` copy was not deleted.
