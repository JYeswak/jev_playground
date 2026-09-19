# OMP observer toolCallId join — fresh lab proof

**Unit:** P2-28
**Profile:** `~/.omp/profiles/jev-lab` only
**Installed extension:** `~/.omp/profiles/jev-lab/agent/extensions/omp-jev-observer.ts`
**Worktree source:** `work/omp-jev-observer/src/observer.mjs`

## Fresh session

Command:

```text
omp --profile=jev-lab --config=/Users/josh/.omp/profiles/jev-lab/agent/config.yml -p 'run exactly: echo p228-toolcall-id-smoke'
```

Session JSONL:

```text
/Users/josh/.omp/profiles/jev-lab/agent/sessions/-Developer-jev/2026-09-19T21-11-25-279Z_01a0bb82-795f-7790-ad32-ca7f5ffd75b6.jsonl
```

The verifier used `work/oracle-kit` `requireKey` and `inspectKey` while reading the custom rows.
It counted:

```text
decisionRows=1
toolCallIdNonempty=1
bridgeRows=1
joinsByToolCallId=1
```

The matched ID was the same `js-bash-*` string in the observer decision and
`com.zeststream.omp-dcg-bridge.decision.v1` row. The decision schema now carries `toolCallId` and
no longer carries the fictional `context.dcgVerdict` field.

## NO-CLAIM

This proves one fresh disposable-lab session has a decision-to-bridge join by `toolCallId`. It does
not establish working-profile traffic, production precision, model quality, or any denominator
beyond this one session. The Jev endpoint was unset; the join is independent of classification
success.
