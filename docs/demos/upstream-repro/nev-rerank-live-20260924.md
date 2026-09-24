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

## Results

TBD — live run below.
