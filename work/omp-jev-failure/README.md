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

## Tests

```bash
node --test work/omp-jev-failure/test/
```

NO-CLAIM: scoring an errored tool is not the same as predicting failure, and this package makes no
accuracy claim for the questions or live traffic.
