# omp-jev-rerank

Observe-only relevance scoring for search output. Watches `tool_result` for `grep`/`glob`, and
when a result carries 8+ hits, asks Jev three questions about the list.

```bash
omp plugin install omp-jev-rerank
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- omp   # see ../../.env.example
```

Mined from `jev-rerank-bench` (RUN; headline reproduces from its committed cache).

## One question, because measurement killed the other two

The first draft asked three questions. `measure.mjs` ran them against four cases whose answers
we know by construction — definition first, definition buried, mostly noise, all noise:

| question | behaviour across 4 cases | verdict |
|---|---|---|
| `definitional` | said **no** every time, including when the definition was hit #1 | constant — cut |
| `noise` | said **yes** every time, including on a list with zero irrelevant hits | constant — cut |
| `ordered` | 4/4 correct, scores moved 0.90 / 0.11 / 0.96 / 0.23 with the actual ordering | kept |

Total agreement was 8/12 against a coin-flip baseline of 6 — which looks like weak signal until
you split it, and then two of the three questions turn out not to depend on their input at all.
**A question whose answer does not change with the input is not a cheap signal; it is noise with
a confidence attached.**

Reproduce:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types work/omp-jev-rerank/measure.mjs
```

## It scores. It does not reorder.

`ordered` discriminates on four hand-built cases. That is not evidence it helps on real search
traffic, so nothing here changes what the agent sees. This lane has twice watched a model
headline invert on real data (R28, the router savings backtest). Scoring first, acting later,
and only if a measurement on real traffic earns it.

## Decision rows

`rerank_scored` with `scores`, or `rerank_error` with `failure` ∈ `unconfigured | http |
non-json | no-answers | transport`. No third clean state; a missing score is never a clean list.

Never blocks, never throws into the host, returns `undefined` on every path.

## Test

```bash
node --experimental-strip-types --test test/rerank.test.mjs   # 7/7
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types live-probe.mjs
```
