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

## All three questions survived measurement — but they are not equal

These scores were logged for a day before anyone checked one against a known answer. `measure.mjs`
now checks them against eleven tool failures whose cause is known by construction: three
transient, four argument, four bug. Nine spell their class in the error text. Two are
**adversarial** — the misleading keyword leads and the disambiguating evidence follows, both
readable from `state` alone (an `ECONNREFUSED` that is really our own code computing an undefined
port; a `TypeError` that is really a missing required CLI option, every frame in `node_modules`).

The sibling `omp-jev-rerank` measurement deleted 2 of its 3 questions for being constants. None
of these three is a constant, so **nothing was cut.** Three runs:

| question | correct (3 runs) | its own always-no constant | score spread | verdict |
|---|---|---|---|---|
| `transient` | 9/9, 11/11, 11/11 | 8/11 | 0.77 | discriminates, stable |
| `bug` | 9/9, 11/11, 11/11 | 7/11 | 0.74 | discriminates, stable |
| `argument` | 9/9, 8/11, 9/11 | 7/11 | 0.90 | discriminates, **but barely beats its constant and is run-unstable** |

Totals were 27/27, 30/33, 31/33 against a coin-flip baseline of 16.5.

**The pooled total is the least interesting number here.** Classes are mutually exclusive, so
each question is false on most cases and a question that always said "no" would already score
7-8 of 11. The bar is not the coin flip; it is each question's own constant. `transient` and
`bug` clear it by 3-4 items and were perfect on every run, including the adversarial arms —
`bug` scored 0.74 on the `ECONNREFUSED` trap that reads as pure network flake.

`argument` clears its constant by **one to two items out of eleven**, and its verdicts are not
reproducible: `permission-denied-system-path` scored 0.50 / 0.48 / 0.47 on three consecutive runs
of the identical input, flipping HIT → MISS → MISS at the 0.5 threshold. All three of its misses
sit within 0.10 of the threshold. It is kept because it is not a constant and it does separate
the clear cases hard (0.97 / 0.89 / 0.95 on real argument errors vs 0.07 / 0.10 / 0.19 on
transient ones). But an `argument` score near 0.5 carries no information, and nothing downstream
should ever treat it as a verdict. `measure.mjs` prints the near-threshold verdicts on every run
for exactly this reason.

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
