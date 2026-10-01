# Task u02: jittered backoff with a time budget

Work in $PWD. `backoff.py` has `compute_delay(attempt, base=0.1, cap=10.0, rng=None)` and `run_with_backoff(call, *, max_attempts=5, base=0.1, cap=10.0, max_elapsed=60.0, clock=None, sleeper=None, rng=None)`. It is wrong. Fix it, standard library only. Verify yourself with stub rng/clock/sleeper doubles (no real sleeping).

Rules: `compute_delay(n, ...)` returns a full-jitter delay in [0, min(cap, base*2**n)], drawn as `rng.uniform(0, upper)`. `call(i)` is tried with 0-based index i; the first attempt runs immediately with no sleep. On `TransientError`, sleep the jittered delay for retry i-1 before attempt i. Any other exception propagates at once with no further sleep. Exhausting `max_attempts` re-raises the last `TransientError`. If `clock() - start + next_delay > max_elapsed`, raise `TimeoutError` without sleeping past the budget. `clock` defaults to `time.monotonic`, `sleeper` to `time.sleep`, `rng` to a fresh `random.Random()`.
