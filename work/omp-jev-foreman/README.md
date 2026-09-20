# omp-jev-foreman

Observe-only progress supervision for long OMP runs. It keeps a rolling window of the last 20
`tool_execution_end` events and calls Jev only after a local trigger: three identical command/tool
pairs or eight calls without a write/edit tool. It never blocks and never throws into OMP.

Each triggered row is either:

- `foreman_scored` with complete Jev scores; or
- `foreman_error` with a failure reason and no scores.

The upstream Foreman adoption claim is intentionally not repeated here. Real-observation AUC was
0.750 against a 0.90 bar (`docs/demos/upstream-repro/foreman-supervision-adoption-20260919.md`).
This package claims only an observe-only trigger surface, not supervision accuracy.

## Install

```bash
omp install ./work/omp-jev-foreman
```

For a live disposable-profile run:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  omp --profile=jev-lab --tools=bash -p 'run exactly: npm test'
```

## Tests

```bash
node --test work/omp-jev-foreman/test/*.test.mjs
```
