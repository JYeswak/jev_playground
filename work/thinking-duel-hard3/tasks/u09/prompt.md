# Task u09: retryable-request helper with Retry-After

Work in $PWD. `retry.py` has `do_request(call, max_attempts=4, now=None,
sleeper=None)` where `call(attempt)` returns `(status, headers, body)` or
raises. It is wrong. Fix it, standard library only. Verify yourself with a
fake sleeper and fixed clock, covering date-valued Retry-After, 501,
ValueError passthrough, and exact attempt counts.

Spec:
- `now` defaults to `time.time`, `sleeper` to `time.sleep`.
- Status 200-299 returns `body` at once (no sleep).
- Retryable: statuses {408, 425, 429, 500, 502, 503, 504} plus
  `TimeoutError`/`ConnectionError` from `call`. On a retryable failure at
  0-based attempt index `i` (when attempts remain): `wait` = parsed
  `Retry-After` response header if valid, else backoff `0.2 * 2**i`; cap
  every wait at 30.0; always call `sleeper(wait)` (even 0.0), then retry.
- `Retry-After`: look up case-insensitively, strip whitespace. A
  non-negative integer string means that many seconds. Else try an HTTP
  date via `email.utils.parsedate_to_datetime`: `wait = max(0.0,
  date.timestamp() - now())`. Missing, negative, or unparsable values fall
  back to backoff. Exceptions have no headers, so they use backoff.
- Any other status (including 501, 400, 404) raises `RetryExhausted`
  at once with no sleep. `call` raising `ValueError` (or anything besides
  `TimeoutError`/`ConnectionError`) propagates unwrapped with no sleep.
- At most `max_attempts` calls total; a retryable failure on the last
  attempt raises `RetryExhausted("exhausted")` with no further sleep.
  `max_attempts < 1` raises `ValueError`.
