# typesafe-sdk-python — W7.0 SDK profile (T1–T3 + T9 + T10)

- **Repo:** first-party `typesafe-ai/typesafe-sdk-python` @
  `0ffd094c72ed9445223060b24ffd7a56aa781fb4` (2026-09-21 15:57:06 +0000,
  Release v0.7.1). MIT (`pyproject.toml:6`, `LICENSE:1`; `LICENSE:3`
  copyright is an unfilled `[year] [fullname]` template placeholder).
- **`git status`:** clean before and after (empty porcelain, verified both).
- **Runtimes:** uv 0.9.28 (repo-pinned, `uv.lock` present); venv python
  3.14.2 (system python 3.9.6 is below `requires-python >=3.10`); SDK 0.7.1.
- **Lane:** keyless, 2026-09-23. No live calls.

| id | result | evidence |
|---|---|---|
| T1 | PASS | SHA + date + license + clean statuses + runtimes above |
| T2 | PASS | `env -u TYPESAFE_API_KEY uv run pytest` → **671 passed, 52 skipped**
  (3.17s, re-run by parent — matches subagent). Skips: 17
  PUBLIC_SYNC_DEV_ONLY (`test_public_sync.py`), 35 keyless
  (`test_docs.py` ×29, `test_integration.py` ×6). RED plant (in /tmp copy
  only: `if not key:` → `if False:` in `config.py`): 6 failed
  (`test_missing_key`, DID NOT RAISE) — suite guards the invariant |
| T3 | PASS | 7 claims, all PASS: base URL `constants.py:15`; default model
  `constants.py:18`; 10.0 s default timeout `constants.py:21-22`;
  missing-key raises pre-I/O `config.py:26-30`; 429 →
  TypeSafeRateLimitError `errors.py:194`; RetryPolicy defaults
  `retry.py:52,64,82`; sync+async clients share kw surface
  `__init__.py:5-8` |
| T9 | PASS | 4/4 vs `127.0.0.1:18923` stub (re-run by parent): hang+timeout=1.0 →
  TypeSafeAPITimeoutError; 429 → TypeSafeRateLimitError (+request_id);
  `not-json{{{` → TypeSafeAPIResponseValidationError; unset key →
  TypeSafeError pre-I/O. Stub answered after all four (host survives) |
| T10 | SELF | first-party SDK; no FLOOR/INCUMBENT run. T4–T8 NOT-APPLICABLE
  (out of SDK profile). NO-CLAIM: nothing about live API behaviour,
  latency, model quality, real-outage retry, or CI — no live calls made |

## Boundary

No live Jev calls. No key used. Clone untouched (no writes; plant lived in
`/tmp/sdk-red`). Async paths covered only by the suite's own async runs,
not by extra probes.
