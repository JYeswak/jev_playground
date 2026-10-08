import sys

sys.path.insert(0, SYS_PATH)
from backoff import compute_delay, run_with_backoff, TransientError


class MaxRng:
    def uniform(self, a, b):
        return b


class MinRng:
    def uniform(self, a, b):
        return a


class Rec:
    def __init__(self):
        self.calls = []

    def uniform(self, a, b):
        self.calls.append((a, b))
        return b


# 1. full-jitter formula, cap, and exact uniform bounds
assert compute_delay(0, base=0.1, cap=10.0, rng=MaxRng()) == 0.1
assert compute_delay(3, base=0.1, cap=10.0, rng=MaxRng()) == 0.8
assert compute_delay(20, base=0.1, cap=5.0, rng=MaxRng()) == 5.0
assert compute_delay(2, base=1.0, cap=10.0, rng=MinRng()) == 0.0
r = Rec()
compute_delay(2, base=0.5, cap=100.0, rng=r)
assert r.calls == [(0, 2.0)], r.calls

# 2. first attempt is immediate: no sleep on success
sleeps = []
calls = []


def ok(i):
    calls.append(i)
    return "win"


assert run_with_backoff(ok, clock=lambda: 0.0, sleeper=sleeps.append,
                         rng=MaxRng()) == "win"
assert sleeps == [] and calls == [0]

# 3. capped jittered sleeps between attempts only
sleeps.clear()
t = [0.0]


def clock():
    return t[0]


def slp(s):
    sleeps.append(s)
    t[0] += s


def flaky(i):
    if i < 3:
        raise TransientError("boom")
    return "late"


assert run_with_backoff(flaky, max_attempts=5, base=1.0, cap=2.0,
                        max_elapsed=100.0, clock=clock, sleeper=slp,
                        rng=MaxRng()) == "late"
assert sleeps == [1.0, 2.0, 2.0], sleeps

# 4. max_elapsed budget raises TimeoutError without oversleeping
sleeps.clear()
t[0] = 0.0


def always(i):
    raise TransientError("down")


try:
    run_with_backoff(always, max_attempts=100, base=1.0, cap=100.0,
                     max_elapsed=5.0, clock=clock, sleeper=slp, rng=MaxRng())
    raise SystemExit("u02 FAIL: budget ignored")
except TimeoutError:
    pass
assert sum(sleeps) <= 5.0, sleeps

# 5. non-transient errors propagate at once with no sleep
sleeps.clear()


def bad(i):
    raise ValueError("perm")


try:
    run_with_backoff(bad, clock=clock, sleeper=slp, rng=MaxRng())
    raise SystemExit("u02 FAIL: swallowed")
except ValueError:
    pass
assert sleeps == [], sleeps
print("u02 PASS")
