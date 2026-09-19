# fast-jev-compaction install-and-run proof

**Upstream source:** `upstream/tamaratran/fast-jev-compaction` at `6e1da50d`
**Clean workdir:** `/Users/josh/Developer/jev/work/p2-compaction`
**Clone untouched:** yes. The clone already had an unrelated modified `package-lock.json`; no clone edits were made.

## Stranger path followed

README commands run in the clean workdir:

```sh
npm install
npm test
npm run typecheck
npm run build
```

Observed:

```text
npm install: rc=0, 50 packages added
npm test: rc=0, 2 test files, 29 tests passed
npm run typecheck: rc=0, library plus hooks
npm run build: rc=0
```

README defect discovered during live use: it documents the package-level `compactMessages` path,
but does not document an adapter for omp's on-disk `SessionEntry` JSONL shape. The README's
`Message` example is not a drop-in reader for real omp session files.

## Real omp run

Input session:

```text
/Users/josh/.omp/profiles/muse/agent/sessions/-Developer-restant/2026-09-09T22-14-47-878Z_01a0883c-e746-719e-8714-a251652cbfe5/MarketFitWave.jsonl
```

This is an omp-written real session with 10 tool results. The probe converted the whole-message
`role=toolResult` rows and assistant `content[].type=toolCall` parts, then called the installed
TypeSafe JavaScript SDK through the required `client.systemOne({state, questions})` shape and
`noul`/`score`/`choice` helpers.

```text
messages before: 5
messages after: 1
serialized bytes before: 48,062
serialized bytes after: 889
byte reduction: 47,173 (98.15%)
estimated tokens before: 15,541
estimated tokens after: 287
token reduction: 15,254 (98.15%)
Jev requests: 1
input tokens: 3,011
output tokens: 366
cost: $0.000126462 at $0.042/M input tokens, output free
wall time: 351 ms inside compactor stats; 1.31 s process wall time
calls evaluated: 10; calls dropped: 10
```

The richest requested session was also attempted:

```text
...2026-08-30T14-11-00-917Z_01a05302-64b5-7510-ae6a-bc314b8ba393.jsonl
```

It contains 11,824 tool results. The upstream compactor refused before making a request:

```text
history too large for Jev (~370635 tokens after truncation, limit 25000)
```

That is a real boundary, not a fabricated reduction.

## Planted negative

A deliberately invalid key was used against a two-message candidate with one unpinned tool call:

```text
TYPESAFE_API_KEY=deliberately-broken NEGATIVE=1 node live-probe.mjs /dev/null
```

Observed:

```text
Error: Jev request failed (401): Cannot authenticate with the server.
exit=1
```

No valid key was written to the workdir, probe, receipt, or log.

## No-claim

- This proves byte/token reduction, not that the agent can still complete its job afterward.
- The 98.15% result is one real session and one live Jev request, not a quality or latency distribution.
- The richest session did not compact; it exceeded the upstream state ceiling before a request.
- No production hook installation or successful production compaction is claimed.
