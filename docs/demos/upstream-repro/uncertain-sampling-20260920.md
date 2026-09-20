# Uncertainty-ranked decision-row audit

Date: 2026-09-20

`work/jev-client/uncertain.mjs` reads persisted extension rows through `readRow`, ranks only rows within the explicit uncertainty window (`min(abs(score - 0.5)) <= 0.1`), and emits a score-independent deterministic random audit sample. Stable IDs are `session-file:line:toolCallId-or-row-index`. `--logs` accepts a directory, one JSONL session, or a comma-separated set of JSONL sessions.

## Offline proof

```text
node --test work/jev-client/test/uncertain.test.mjs
1..4
# tests 4
# pass 4
# fail 0
```

The planted negative uses scores 0.1 and 0.9; it returns zero uncertain rows rather than selecting the closest available rows.

## Live route proof

Command:

```text
node work/jev-client/uncertain.mjs --logs /Users/josh/.omp/profiles/jev-lab/agent/sessions/--private-tmp--/2026-09-20T00-00-47-549Z_01a0bc1d-89bd-7151-9f26-3bdeb55815e0.jsonl --type com.zeststream.omp-jev-route.decision.v1 --uncertain 3 --random 2 --seed 42
```

Actual summary and audit output:

```json
{"kind":"summary","type":"com.zeststream.omp-jev-route.decision.v1","totalRows":24,"nearThresholdRows":0,"scoreBuckets":{"0.0-0.2":24,"0.2-0.4":0,"0.4-0.6":0,"0.6-0.8":0,"0.8-1.0":24},"uncertainCount":0,"randomCount":2,"seed":42}
{"kind":"random_audit","id":"2026-09-20T00-00-47-549Z_01a0bc1d-89bd-7151-9f26-3bdeb55815e0.jsonl:66:3","uncertainty":0.4,"scores":[{"key":"needs_heavyweight","value":0.9},{"key":"mechanical","value":0.1}]}
{"kind":"random_audit","id":"2026-09-20T00-00-47-549Z_01a0bc1d-89bd-7151-9f26-3bdeb55815e0.jsonl:1819:15","uncertainty":0.41000000000000003,"scores":[{"key":"needs_heavyweight","value":0.91},{"key":"mechanical","value":0.09}]}
```

The route run has 24 scored rows. There are 48 bucketed numeric probabilities because each row carries two class probabilities. No row is within the uncertainty window, so no NO-CLAIM label candidate is emitted.

## Live harm proof

The named harm run uses the two persisted session JSONL files that contain 11 + 21 = 32 scored decision rows:

```text
node work/jev-client/uncertain.mjs --logs /Users/josh/.omp/profiles/jev-lab/agent/sessions/--private-tmp--/2026-09-19T23-41-42-810Z_01a0bc0c-121a-7170-8236-2c544a01a556.jsonl,/Users/josh/.omp/profiles/jev-lab/agent/sessions/--private-tmp--/2026-09-19T23-49-38-291Z_01a0bc13-5373-7549-9aeb-ca0144441031.jsonl --type com.zeststream.omp-harm-rule.decision.v1 --uncertain 3 --random 2 --seed 42
```

Actual summary and audit output:

```json
{"kind":"summary","type":"com.zeststream.omp-harm-rule.decision.v1","totalRows":32,"nearThresholdRows":0,"scoreBuckets":{"0.0-0.2":32,"0.2-0.4":0,"0.4-0.6":0,"0.6-0.8":0,"0.8-1.0":0},"uncertainCount":0,"randomCount":2,"seed":42}
{"kind":"random_audit","id":"2026-09-19T23-41-42-810Z_01a0bc0c-121a-7170-8236-2c544a01a556.jsonl:177:js-bash-0df6c106-d347-45dc-a417-142ed2aaa9b6","uncertainty":0.49,"scores":[{"key":"score","value":0.01}]}
{"kind":"random_audit","id":"2026-09-19T23-49-38-291Z_01a0bc13-5373-7549-9aeb-ca0144441031.jsonl:1121:js-bash-a902e2f5-492f-4c47-a995-67ef12bfaaf7","uncertainty":0.49,"scores":[{"key":"score","value":0.01}]}
```

No NO-CLAIM label candidates are emitted by either live run. The random rows remain audit candidates only; this tool does not assign labels or make routing/harm claims.
