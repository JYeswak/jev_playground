# omp-jev-failure

Observe-only Jev classification for errored OMP tool executions. Failed tool executions produce
either `failure_classified` — exactly one of three mutually-exclusive classes, with its full
probability distribution — or `failure_error` with a named client failure; there is no default
class and the extension never blocks or throws into OMP.

## Install

From a repository checkout:

```bash
omp install ./work/omp-jev-failure
```

For a live proof with the configured Jev key:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- omp --profile=jev-lab -p 'run exactly: false'
```

## One multiclass question, not three binary ones

This unit shipped three independent binary questions (`transient`, `argument`, `bug`) and the
`argument` one was never stable. A rephrasing rescue at `c6b77b8` did not fix it. What fixed it was
deleting the shape: the three classes are mutually exclusive by construction, and three
independent yes/no questions cannot say so. Measured in one session, three runs per arm, same
eleven committed cases, same `state`, only the question shape differing
(`measure-multiclass.mjs`, receipt: `docs/demos/upstream-repro/multiclass-failure-20260919.md`):

| arm | case-level score, 3 runs | drift | structurally impossible answers |
|---|---|---|---|
| three binary questions (shipped before) | 9/11, 9/11, 9/11 | none in this block | **2 per run** — `argument` and `bug` both true |
| one choice question, question-shaped class text | 11/11, 11/11, 11/11 | none | 0 |
| one choice question, declarative class text (**shipped**) | 11/11, 11/11, 11/11 | none | 0 |

A case counts as correct only when every verdict it produced is right, which is the only
comparison between one label and three. Both adversarial arms pass in all six multiclass runs.
Across all seven binary runs tonight the score was 9-10/11 and never 11, and the *identity* of the
missed cases moved between measurement blocks.

The extension emits a class and its distribution only; it never acts on them. No accuracy or
production failure-prediction claim is made.

## Measure

Binary baseline and both multiclass wordings, three runs each, in one command:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types work/omp-jev-failure/measure-multiclass.mjs
```

The older per-question binary measurement, which is what `measure-multiclass.mjs`'s `binary` arm
re-runs in-session, is still here:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types work/omp-jev-failure/measure.mjs
```

## It scores. It does not act.

Nothing here changes what the agent sees, retries, or reports. Eleven cases I wrote myself do not
license acting on a failure classification in real traffic.

## Tests

```bash
node --experimental-strip-types --test work/omp-jev-failure/test/failure.test.mjs   # 5/5
```

NO-CLAIM: eleven hand-built failures, authored by the same person who knew the answers, and the
same eleven the class descriptions were shaped against. This establishes that one multiclass
question is stable and coherent on those eleven where three binary questions were neither. It does
not establish accuracy on real tool traffic, cannot rule out that the phrasing made each class
legible, and says nothing about mixed causes — a flaky dependency exposed by a real bug — because
no such case is in the set. Two adversarial arms are two, not a distribution. **There is no
hold-out here.** The rescue this unit tried before scored 6/7 on fresh cases while answering no to
all seven, so a good-looking number on cases a question was shaped against is exactly the failure
mode to distrust. Running this multiclass question on failures nobody wrote for it is the next
unit, and it has not been done.
