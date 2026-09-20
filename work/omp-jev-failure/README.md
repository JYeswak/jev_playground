# omp-jev-failure

Observe-only Jev scoring for errored OMP tool executions. Failed tool executions produce either
`failure_scored` with a complete `scores` object or `failure_error` with a named client failure;
there is no default score and the extension never blocks or throws into OMP.

## Install

From a repository checkout:

```bash
omp install ./work/omp-jev-failure
```

For a live proof with the configured Jev key:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- omp --profile=jev-lab -p 'run exactly: false'
```

## Three questions after holdout rescue

The failure questions were re-tested on fresh holdout cases at `c6b77b8`. The rescued `argument` wording scored 6/7 with spread 0.83; its single miss tied a stale-hash rejection to the invocation. The nine-case/11-case committed measurement rerun scored `argument` 8/11, with the same boundary instability. `transient` and `bug` remain unchanged. Overfit is not ruled out.

| question | committed rerun | holdout result | verdict |
|---|---|---|---|
| `transient` | 11/11 | existing stable result | retained |
| `bug` | 11/11 | existing stable result | retained |
| `argument` | 8/11; near-threshold misses | 6/7; one stale-hash boundary miss | discriminates, unstable boundary |

The extension emits scores only; it never acts on them. No accuracy or production failure-prediction claim is made.

## Measure

~~~bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/omp-jev-failure/measure.mjs
~~~

Reproduce:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types work/omp-jev-failure/measure.mjs
```

## It scores. It does not act.

Nothing here changes what the agent sees, retries, or reports. Eleven cases I wrote myself do not
license acting on a failure classification in real traffic.

## Tests

```bash
node --experimental-strip-types --test work/omp-jev-failure/test/failure.test.mjs   # 4/4
```

NO-CLAIM: eleven hand-built failures, authored by the same person who knew the answers. This
establishes that the three questions are not constants and that two of them are stable on
legible cases. It does not establish accuracy on real tool traffic, cannot rule out that the
phrasing made each class legible, and says nothing about mixed causes — a flaky dependency
exposed by a real bug — because no such case is in the set. Two adversarial arms are two, not a
distribution.
