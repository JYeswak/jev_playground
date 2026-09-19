# OMP Jev failure observer — live proof

**Unit:** P2-36
**Package:** `work/omp-jev-failure`
**Profile:** disposable `jev-lab`

## Event surface

OMP source confirms the extension event at:

```text
/Users/josh/.local/lib/node_modules/@oh-my-pi/pi-coding-agent/src/extensibility/extensions/types.ts:821-826
```

`tool_execution_end` carries `toolCallId`, `toolName`, `result`, and `isError`. A nested `eval`
call did not expose the needed failure event, so the live proof used OMP's direct bash tool surface:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  omp --profile=jev-lab --no-extensions \
      --extension=$PWD/work/omp-jev-failure/src/index.ts \
      --tools=bash -p 'run exactly: false'
```

## Live evidence

Session:

```text
/Users/josh/.omp/profiles/jev-lab/agent/sessions/-Developer-jev/2026-09-19T23-39-34-451Z_01a0bc0a-1cb3-7599-babd-3a8b94a6d58d.jsonl
```

Decision row:

```text
kind=failure_scored
toolCallId=call_my9cfNZyjS0idy78GY3OyuLq|fc_0ebbb9811d696395016aaf1d399d2087d0a7faef194424f5a6
toolName=bash
scores={transient:0.36, argument:0.67, bug:0.27}
latencyMs=901
model=jev-1.13.0
```

The same session contains the `tool_execution_start` and errored result (`isError=true`, exit code
1). The extension emitted `failure_scored`; it never blocked or threw into OMP.

## Offline arms

```text
node --test work/omp-jev-failure/test/*.test.mjs
4 tests passed
```

Covered planted negatives:

- errored tool with scored Jev response → `failure_scored` with scores;
- errored tool with Jev HTTP failure → `failure_error` without scores;
- non-error execution → diagnostic only, no decision;
- append/classifier throws → fail-open, no host throw.

## NO-CLAIM

Scoring an errored tool is not the same as predicting failure. No accuracy, calibration, or live
traffic precision claim is made. The live result is one disposable-lab row produced by the
`openai-codex/gpt-5.6-luna` agent through direct bash. It does not establish production behavior.
