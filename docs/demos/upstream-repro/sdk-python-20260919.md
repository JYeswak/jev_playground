# `typesafe-sdk-python` — the last unrun clone, and the control arm for the JS crash

**Date:** 2026-09-19 · **Level:** `[live]` · **Bead:** `jev-hwa` · **Clone untouched.**
**This completes the sweep: 22 of 22 vendored clones run.**

## Their suite

```
uv sync --all-extras   -> rc=0
uv run pytest -q       -> 534 passed, 50 skipped in 2.63s
```

Zero errors. The 50 skips are honest and self-describing ("Public sync tooling is only available in
the dev repository"). **No green-while-throwing** — the shape that `typesafe-sdk-js` shows with
189/189 passing beside 8 unhandled rejections.

## The control arm that matters

`docs/demos/upstream-repro/sdk-python-timeout-control.py` runs the **same scenario** as the JS crash
repro: a server that flushes headers and never ends the body, one client call, a short timeout.

| | JS SDK | Python SDK |
|---|---|---|
| caller sees | `APITimeoutError` | `TypeSafeAPITimeoutError` |
| leaked async errors | **1 per timed-out request** | **0** |
| default process outcome | **dies, exit 1** | **survives** |

Both SDKs raise the right error to the caller. Only the JS one leaves a second, unobserved
rejection behind, which Node's default policy turns into a process kill.

**This upgrades the JS finding.** It is not "async is hard" or "Node is strict" — it is a defect
their own other SDK does not have, in the same vendor's hands, for the same scenario. `httpx` under
`asyncio` with a loop exception handler installed reports **zero** loop-level exceptions.

## A small API friction, reported not patched

`AsyncTypeSafeClient(max_retries=0)` raises `TypeError`; the parameter is `retry: RetryPolicy`. The
JS client uses `retry: { maxRetries: 0 }`. Both are defensible alone; a user moving between the two
SDKs will write the wrong one, as I did on the first attempt.

## NO-CLAIM

One Python (3.14.2), one platform (macOS arm64), one transport path. The control establishes that
the JS leak is **not inherent to the scenario**; it does NOT establish why the JS path leaks — that
remains the uninstrumented inference recorded in `sdk-js-timeout-crash-20260919.md`. No live API
calls were made: both suites and both repros are offline against local servers.
