# omp-jev-rerank

Observe-only relevance scoring for search output. Watches `tool_result` for `grep`/`glob`, and
when a result carries 8+ hits, asks Jev three questions about the list.

```bash
omp plugin install omp-jev-rerank
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- omp   # see ../../.env.example
```

Mined from `jev-rerank-bench` (RUN; headline reproduces from its committed cache).

## It scores. It does not reorder.

Nothing here changes what the agent sees, and that is not temporary caution — **the first live
run disagreed with ground truth on two of three questions**:

| question | live score | ground truth |
|---|---|---|
| `definitional` — is the definition in the first three hits? | **0.05** | yes, it was hit #1 |
| `ordered` — is the list already best-first? | 0.92 | correct |
| `noise` — is >half irrelevant? | **0.94** | no, all 22 hits were relevant |

One run proves nothing about accuracy in either direction, but it is the opposite of a reason to
act on these scores. This lane has twice watched a model headline invert on real data (R28, the
router savings backtest). Scoring first, acting later, and only if a measurement earns it.

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
