# Task h02: retry with date-valued Retry-After

Work in $PWD. `retrypy.py` has `fetch_with_retry(call, retries=5, now=None,
sleeper=None)` where `call(attempt)` returns `(status, headers, body)` or
raises `TransientError`; `now()` gives epoch seconds (default `time.time`).
Rules: retry only {429,502,503,504} + TransientError; `Retry-After` may be
delta-seconds OR an HTTP date (parse with `email.utils.parsedate_to_datetime`,
wait = max(0, date - now)); else backoff 0.1*2**attempt with total sleep
capped at 2.0s; 501 and other 4xx/5xx raise `PermanentError` at once; 200
returns body. shipped code is wrong. Fix it. Verify yourself.
