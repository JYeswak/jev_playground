# omp-jev-rerank

Observe-only relevance scoring for search output. Watches `tool_result` for `grep`/`glob`, and
when a result carries 8+ hits, asks Jev three questions about the list.

```bash
omp plugin install omp-jev-rerank
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- omp   # see ../../.env.example
```

Mined from `jev-rerank-bench` (RUN; headline reproduces from its committed cache).

## Three questions after holdout rescue

The original `definitional` and `noise` questions were degenerate on the tuning cases. Pane3 re-tested the rescued wording on fresh holdout cases at `c6b77b8`: `noise` 8/8, spread 0.67; `definitional` 6/8, spread 0.92. The definitional misses are boundary cases where the definition sits at index 3, outside the first three. Overfit is not ruled out.

Our committed four-case rerun after the rescue scored 12/12, but that is a same-case smoke result, not a generalization claim:

| question | committed-case result | holdout result | verdict |
|---|---|---|---|
| `definitional` | 4/4 | 6/8; boundary misses | discriminates, holdout-sensitive |
| `noise` | 4/4 | 8/8 | discriminates; overfit not ruled out |
| `ordered` | 4/4 | existing shipped question | retained |

The extension scores but never reorders agent output. No adoption or traffic accuracy claim is made.

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
