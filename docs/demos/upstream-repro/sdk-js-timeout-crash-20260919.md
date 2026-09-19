# UPSTREAM REPORT — `typesafe-sdk-js`: a request timeout kills a default Node consumer

**Date:** 2026-09-19 · **Level:** `[live]` · **Bead:** `jev-kqf` · **Clone untouched; no patch proposed.**

## Summary

Every request that times out leaks **one unhandled promise rejection**. The SDK correctly throws
`APITimeoutError` to the caller *and* separately rejects an `AbortError` that nothing handles.
Under Node's default `--unhandled-rejections=throw` (the default since Node 15), that **terminates
the process**. Reproduced on Node v22.22.0 with no test framework and no fetch doubles.

## Reproduction

`docs/demos/upstream-repro/sdk-js-timeout-crash-repro.mjs` — a real `node:http` server that flushes
headers and never ends the body, the real global `fetch`, one client call with `timeout: 200`:

```
$ npx tsx sdk-js-timeout-crash-repro.mjs
consumer caught: APITimeoutError        <- correct behaviour
node:internal/process/promises:394
DOMException [AbortError]: This operation was aborted
    at Timeout._onTimeout (src/client.ts:421:18)
exit=1                                   <- "SURVIVED" never prints
```

With an `unhandledRejection` handler installed, the same script prints
`unhandled rejections after ONE timed-out request: 1` and survives — so the count is exactly one
per timed-out request, and the crash is Node's default policy acting on it.

## Isolation

Their own suite reports **189/189 passing with 8 unhandled errors**, and Vitest warns this "might
cause false positive tests". Run file by file, all 8 come from **one** file:

| test file | unhandled |
|---|---|
| `native-transport.test.ts` | **8** |
| the other 8 files | 0 each |

That file makes 8 aborted requests (3 calls x 2 statuses, plus 1 x 2). **8 aborted requests, 8
rejections — one each**, matching the standalone repro exactly.

## Mechanism, and the wrong version I published first

`client.ts:419-422` sets a timeout that calls `controller.abort()`. My first reading concluded the
timer leaked; **that was wrong** — `finally { clearTimeout(timer) }` is present at line 444-446 and
the `catch` maps the abort to `APITimeoutError` correctly. I said so in `4c0d768`'s NO-CLAIM.

What actually escapes is a *second* rejection: the abort tears down a response whose body is still
being consumed, and that rejection has no handler attached. The caller-facing path is clean; the
process-level one is not. **This is shipped-code behaviour, not a test artifact** — the repro uses
neither vitest nor a fake fetch.

## Suggested direction (not a patch)

Attach a handler to whatever promise the abort rejects, so the abort is observed exactly once.

## NO-CLAIM

Reproduced on **one** Node version (v22.22.0) and one platform (macOS arm64). I did not identify
the precise awaited promise that escapes, so "the body teardown" is inference from the stack, not
from instrumentation. Not reported to upstream's tracker yet — this file is the report text.
