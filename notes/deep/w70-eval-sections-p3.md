
## typesafe-sdk-js — W7.0 SDK profile (TopazRaven, 2026-09-23, keyless)

`typesafe-sdk-js @ 66880cc` (v0.6.0). `M package-lock.json` pre-existing,
byte-identical before/after. `env -u TYPESAFE_API_KEY npx vitest run`:
189/189 pass, 0 skips, typecheck clean — exit 1 via 8 unhandled AbortError
rejections from native-transport timers. /tmp defect (validateQuestions
neutered) RED at `test/client.test.ts:383`. T9 4/4 vs local stub
(hang→APITimeoutError, 429→RateLimitError, malformed→TypeSafeError,
unset key→TypeSafeError). Class SELF. Receipt
`docs/demos/upstream-repro/typesafe-sdk-js-w70-20260923.md`.
Boundary: no live calls; T1 cleanliness FAILS on pre-existing dirt.

## typesafe-sdk-python — W7.0 SDK profile (TopazRaven, 2026-09-23, keyless)

`typesafe-sdk-python @ 0ffd094` (v0.7.1). Clean before/after.
`env -u TYPESAFE_API_KEY uv run pytest`: 671 passed, 52 skipped (17
dev-only, 35 keyless). /tmp defect (`if not key:`→`if False:`): 6
`test_missing_key` FAIL. T9 4/4 vs `127.0.0.1:18923` stub, host survives.
Class SELF. Receipt
`docs/demos/upstream-repro/typesafe-sdk-python-w70-20260923.md`.
Boundary: cassette-free run; async paths via suite only.

## system-one-adapter-python — W7.0 SDK profile (TopazRaven, 2026-09-23, keyless)

Upstream @ `adffc2e` (v0.2.0), clean. `uv run pytest`: 229 passed
(cassette replay, `--block-network`). /tmp defect (×2.0 rescale): 1 fail.
T9: missing-key refuses at construction; 429/malformed map to typed
errors; hang hits the 25 s deadline with no output. Class SELF.
**Root copy `system-one-adapter-python/` @ `0bb819b` is STALE** (upstream's
own v0.1.4 tag-commit; upstream 2 releases ahead, 28 files differ).
Receipt `docs/demos/upstream-repro/system-one-adapter-w70-20260923.md`.
Boundary: live-provider behaviour not evaluated.

## s1-rs client transport — W7.0 SDK profile (TopazRaven, 2026-09-23, keyless, RCH)

`s1-rs @ b916897`, clean. `cargo test -j 2 -p s1 --features
backend-typesafe-rs` on contabo-1, exit 0: ask 4/4, decode 8/8, golden
5/5, policy 10/10, loopback 1/1, ui 1/1 (inner 4/4), doctests 2+1 ignore.
Golden 5/5 re-run by parent. Scratch-copy defect (serde case): exit 101,
2/3 golden RED. T9 5/5 loopback, all `S1Error::Backend`. Class SELF.
Contabo-4 compile-fail anomaly resolved by worker repair (`/dev/null` +
`.rustc_info.json`; re-run exit 0). Receipt
`docs/demos/upstream-repro/s1-rs-client-w70-20260923.md`. Boundary: no
live calls; scratch tree left outside jev pending manual removal.

## work/jev-client — W7.0 SDK profile + fix (TopazRaven, 2026-09-23, keyless)

Own client over vendored `@typesafe-ai/sdk v0.6.0`. Suite 29/0 + 8/0
(measure/uncertain). T9 found a nondeterministic Node host kill via leaked
SDK-timer AbortError (`dist/index.mjs:636`), ~1/3 of timeouts; Bun 2/2
survived. Fixed in `src/index.ts` (`guardedFetch` owns the timeout):
regression test failed pre-fix, green post-fix; Node 30/30 + Bun 30/30
exit 0; suites 38/0. Class SELF (transport only). Receipt
`docs/demos/upstream-repro/jev-client-w70-20260923.md`. Boundary: no live
calls; defect originates vendored-upstream.
