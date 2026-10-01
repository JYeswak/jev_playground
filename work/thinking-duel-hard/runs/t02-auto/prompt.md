# Task t02: retry policy

Work in $PWD. `retrypy.py` has `fetch_with_retry(call, retries=5)` where
`call(attempt)` returns `(status, headers, body)` or raises
`TransientError`. It must: retry only transient statuses {429,502,503,504}
and TransientError; honor `Retry-After` seconds when present (else
exponential backoff base 0.1s with jitter, capped so total sleep <= 2.0s);
raise `PermanentError` immediately on other 4xx; return body on 200.
It is wrong. Fix it (no real sleeping: use the injected `sleeper(secs)`
callable, default `time.sleep`). Verify yourself.
