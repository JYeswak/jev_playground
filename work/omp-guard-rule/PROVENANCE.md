# Golden provenance — omp-guard-rule

Generator: `node --experimental-strip-types work/omp-guard-rule/golden.mjs`
Fixture: `fixtures/session-pinned.jsonl` (sha recorded below), 6 tool_call
events: 2 shapes from jev-lab session `2026-09-20T17-49-12` (the live-fire
proof; benign commands) + 4 authored class representatives, each flagged
`"real": true|false` in the fixture itself.

Regenerate: `UPDATE_GOLDENS=1` + `git diff` review gate. CI never
auto-updates. Comparison is in-memory (no `*.actual` files produced);
`*.actual` stays ignored so a future file-comparing runner cannot
accidentally commit its output.

Volatile scrubbed at replay: `timestamp` → `[TIMESTAMP]`,
`toolCallId` → `[ID]`. Live counts get structural treatment only —
an exact golden over a live-monotonic corpus is guaranteed test rot.
