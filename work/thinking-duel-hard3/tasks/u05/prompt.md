# Task u05: exactly-once threaded memoizer

Work in $PWD. `memo.py` has `Memoizer(func)` with `get(key)`. It is wrong. Fix it, standard library only. Verify yourself with racy thread bursts on one key, exception-then-retry, and mixed-key bursts.

Rules: concurrent `get` calls for the same key must run `func` exactly once (single-flight) and every caller gets the same result; exceptions from `func` are never cached and every waiting caller sees the same exception; a later `get` after a failure retries `func`; distinct keys resolve independently; cached values never recompute. Keys are hashable.
