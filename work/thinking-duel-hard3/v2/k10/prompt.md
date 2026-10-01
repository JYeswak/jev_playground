# Task k10: thread-safe token bucket

Work in $PWD. `bucket.py` has `Bucket(rate, burst, now=time.monotonic)`
with `take(n=1)` returning True (and deducting) iff at least n tokens are
available, else False without deducting. Tokens refill continuously at
`rate` per second up to `burst`; all methods thread-safe via a lock; time
comes only from `now()`. shipped code races and over-refills. Fix it,
stdlib only. Verify with a fake clock and threads.
