# omp-jev-foreman live proof

**Unit:** P2-37
**Package:** `work/omp-jev-foreman`

## Offline arms

```text
node --test work/omp-jev-foreman/test/*.test.mjs
4 tests passed
```

Covered planted negatives:

- healthy varied window does not trigger Jev;
- repeated-command window triggers one `foreman_scored` decision;
- throwing classifier emits `foreman_error` without scores;
- throwing host remains fail-open.

## Live row

Command:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  omp --profile=jev-lab --no-extensions \
      --extension=$PWD/work/omp-jev-foreman/src/index.ts \
      --tools=bash -p 'run exactly three separate bash calls, each: npm test'
```

Session:

```text
/Users/josh/.omp/profiles/jev-lab/agent/sessions/-Developer-jev/2026-09-20T00-02-05-252Z_01a0bc1e-b944-7164-980e-efed3d404780.jsonl
```

Live decision row:

~~~text
kind=foreman_scored
trigger=repeated_command
latencyMs=375
model=jev-1.13.0
scores={progress:0.12,repeating:0.98,stuck:0.88}
window_len=3
first_command={"command":"npm test","cwd":"/Users/josh/Developer/jev"}
~~~

The rolling window contains three errored `npm test` executions and preserves command text by joining
`tool_execution_start` args to `tool_execution_end`. The live run was produced by
`openai-codex/gpt-5.6-luna` through direct bash.

## NO-CLAIM

The rejected Foreman adoption claim remains rejected: real-observation AUC was 0.750 against a
0.90 bar. This package claims only local-triggered observe-only progress supervision and one live
row. It makes no supervision accuracy, prediction accuracy, calibration, or production traffic
claim.
