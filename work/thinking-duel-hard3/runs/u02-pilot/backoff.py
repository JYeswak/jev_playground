import random
import time


class TransientError(Exception):
    pass


def compute_delay(attempt, base=0.1, cap=10.0, rng=None):
    if rng is None:
        rng = random.Random()
    upper = min(cap, base * (2**attempt))
    return rng.uniform(0, upper)


def run_with_backoff(
    call,
    *,
    max_attempts=5,
    base=0.1,
    cap=10.0,
    max_elapsed=60.0,
    clock=None,
    sleeper=None,
    rng=None,
):
    now = clock if clock is not None else time.monotonic
    slp = sleeper if sleeper is not None else time.sleep
    if rng is None:
        rng = random.Random()
    start = now()
    last = None
    for attempt in range(max_attempts):
        if attempt > 0:
            next_delay = compute_delay(attempt - 1, base, cap, rng)
            if now() - start + next_delay > max_elapsed:
                raise TimeoutError(
                    f"backoff budget exceeded: elapsed={now() - start!r} "
                    f"+ delay={next_delay!r} > max_elapsed={max_elapsed!r}"
                )
            slp(next_delay)
        try:
            return call(attempt)
        except TransientError as e:
            last = e
            continue
    raise last
