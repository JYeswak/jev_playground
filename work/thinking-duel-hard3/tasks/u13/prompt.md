# Task u13: sliding-window rate limiter

Work in $PWD. `limiter.py` has `RateLimiter(limit, window)` with
`allow(now=None)`: at most `limit` allowed calls in any half-open window
`(now-window, now]`; `now` defaults to `time.monotonic()`. It is wrong.
Fix it, standard library only. Verify yourself with burst-limit checks,
exact window-edge expiry (`allow(0.0)` then `allow(window)` must succeed
for limit 1), and a faked-clock check that `allow()` follows
`time.monotonic`, not wall time.
