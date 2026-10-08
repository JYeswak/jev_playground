# Native SDK cutover — 2026-09-21

A fresh agent can implement from this file. GPT Pro review rounds were not run.
Joshua asked for the map and the beads now. A four-round review that blocks the
cutover is the process the tick just forbade.

## Why

RULE 14: the native repo is the incumbent. We vendored four TypeSafe trees and
built for days on a hand-rolled POST. `work/jev-client/src/index.ts` is that
POST. `@typesafe-ai/sdk` at `upstream/typesafe-ai/typesafe-sdk-js` @ `66880cc`
already ships the typed surface. It is also installed at
`work/sdk/node_modules/@typesafe-ai/sdk/`. We installed it, then wrote our own.

Lane status at `9e10788`: 41 candidates, 0 promoted, 15 ruled out, 9 cleared,
17 held. Every comparator was a floor (regex, constant, BM25). The incumbent
comparison — an LLM on the same questions — has not been run. That unit is
already in flight on pane 2.

## Native surface, measured at 66880cc

From `src/types.ts` and `src/questions.ts`. Not from memory.

| Builder | Wire type | Fields we did not use |
|---|---|---|
| `noul(instructions, criteria?)` | `noul` | `criteria.true` / `criteria.false` descriptions |
| `choice(instructions, criteria)` | `choice` | description may be null; instructions may be JSON, not only a string |
| `score(instructions, criteria)` | `score` | list of at least two descriptions; `validateQuestions` refuses a map or a shorter list |

`EntryType` is `string | object | array | null`. Our client sends strings only.

`systemOne` returns `answers`, `usage`, and the resolved `model`. Our
`askJev` does not return usage on the happy path. `models.list` and
`RetryPolicy` exist. We reimplemented retry as a loop.

Keyless suite: `npx vitest run` exit 0, 189 passed, 10 files. First `npm test`
exit 1 on unhandled `AbortError` in `test/native-transport.test.ts`. Finding
about their suite. Not edited. `examples/demo.ts` calls the API. Not run.

## Our surfaces

| Surface | What it does | SDK mapping | Disposition |
|---|---|---|---|
| `work/jev-client/src/index.ts` `postSystemOne` | hand-rolled POST | `TypeSafeClient.systemOne` | COLLAPSE. This is the one canonical call. |
| Callers of `askJev` / `askJevChoice` / `askJevBundle` | injection, review, routing, triage, measures | keep calling a thin wrapper that uses the SDK | MIGRATE after the wrapper exists. Do not edit each caller to import the SDK. |
| `work/jevcache-probe/repro-1-*.sh` | echoes a server rejection string | SDK would not reproduce it | EXEMPT. Reason in the gate file. |
| `question-shape-measure.mjs`, `omp-jev-failure/measure.mjs` | URL inside a fixture curl failure | not a POST | EXEMPT. |
| `work/p2-localjev` | local `/v1/systemone` server | not a client of `api.typesafe.ai` | DO NOT COLLAPSE on a `fetch()` match. |
| `work/nev-routing/tool-select-labelled.jsonl` | session text | not code | DO NOT DELETE. Privacy. |
| `foundation/gates.d/40-native-surface.sh` | the gate | ast-grep for a direct POST, not a comment | P3 builds it. RED arm required. |

`ripwire work --exemplar="call the jev api"` exited 0 and named a truncate
helper. It cannot see the wire call. `fh` ledger was 332 hours stale. Those
tools do not replace the table above.

## Cutover

1. One wrapper in `work/jev-client` whose only network call is
   `TypeSafeClient.systemOne`. Inject the transport. Missing key throws.
   Malformed answers throw. Fail-safe stays in our code, not in the SDK.
2. `askJev` / `askJevChoice` / `askJevBundle` become that wrapper. Call sites
   do not change their imports.
3. Offline tests stay on an injected fetch. No live call in the unit tests.
4. The native-surface gate goes RED on a planted direct POST with no exemption
   line, and names the file. Exemptions name path and reason.
5. Pane 2's differential is the incumbent comparison. It is not blocked by
   the wrapper. Do not sample it to save money. The spend gate is lifted.
   Preregister before the first new call. Do not re-measure a number we have.

## What this plan does not do

- It does not certify a seat. R75 stands: no label, no entrance.
- It does not adopt the pilot rung. That needs a non-author ruling.
- It does not delete probes.
- It does not edit `upstream/typesafe-ai/*`.
- It does not push a vendored clone.
- It does not remove `~/.omp/profiles/jev-scratch-p4`. Joshua has not said so.

## Beads

Created from this file. A fresh agent runs `br ready` and does not need this
plan open if the bead body is complete. The plan remains the map.
