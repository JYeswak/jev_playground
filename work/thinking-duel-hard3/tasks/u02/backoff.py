import random
import time


class TransientError(Exception):
    pass


def compute_delay(attempt, base=0.1, cap=10.0, rng=None):
    return base * (2 ** attempt)


def run_with_backoff(call, *, max_attempts=5, base=0.1, cap=10.0,
                      max_elapsed=60.0, clock=None, sleeper=None, rng=None):
    now = clock or time.monotonic
    slp = sleeper or time.sleep
    start = now()
    last = None
    for attempt in range(max_attempts):
        slp(compute_delay(attempt, base, cap, rng))
        try:
            return call(attempt)
        except TransientError as e:
            last = e
            continue
    raise last
