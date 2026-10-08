import sys
import time
from email.utils import parsedate_to_datetime, formatdate


sys.path.insert(0, SYS_PATH)
from retry import do_request, RetryExhausted

T0 = 1_700_000_000.0
clock = [T0]
sleeps = []
calls = []


def reset():
    clock[0] = T0
    sleeps.clear()
    calls.clear()


def now():
    return clock[0]


def slp(s):
    sleeps.append(s)


# 1. HTTP-date Retry-After honored (20s out stays under the 30s cap)
reset()
date20 = formatdate(T0 + 20, usegmt=True)
seq = [(503, {"Retry-After": date20}, None), (200, {}, "ok")]
assert do_request(lambda a: seq[a] if a == 0 else (200, {}, "ok"), now=now, sleeper=slp) == "ok"
assert len(sleeps) == 1 and abs(sleeps[0] - 20.0) < 2.0, sleeps

# 2. case-insensitive header, surrounding whitespace, per-wait cap
reset()
seq = [(429, {"rEtRy-AfTeR": "  2 "}, None), (503, {"Retry-After": "3600"}, None), (200, {}, "done")]
out = do_request(lambda a: seq[a], now=now, sleeper=slp)
assert out == "done", out
assert sleeps == [2.0, 30.0], sleeps

# 3. 501 is permanent: one call, no sleep
reset()


def c501(a):
    calls.append(a)
    return (501, {}, None)


try:
    do_request(c501, now=now, sleeper=slp)
    raise AssertionError("501 should raise")
except RetryExhausted as e:
    assert e.args[0] == 501, e.args
assert calls == [0] and sleeps == [], (calls, sleeps)

# 4. ValueError propagates unwrapped; TimeoutError retries with backoff
reset()


def cval(a):
    calls.append(a)
    raise ValueError("bad input")


try:
    do_request(cval, now=now, sleeper=slp)
    raise AssertionError("ValueError should propagate")
except ValueError as e:
    assert str(e) == "bad input", e
assert calls == [0] and sleeps == [], (calls, sleeps)

reset()
seq2 = [TimeoutError("t"), (200, {}, "hi")]


def cto(a):
    v = seq2[a]
    if isinstance(v, Exception):
        raise v
    return v


assert do_request(cto, now=now, sleeper=slp) == "hi"
assert sleeps == [0.2], sleeps

# 5. exact attempt budget: 3 calls / 2 backoff sleeps, then exhausted; max_attempts=1 never sleeps
reset()
n = [0]


def c503(a):
    n[0] += 1
    return (503, {"Retry-After": "soon"}, None)


try:
    do_request(c503, max_attempts=3, now=now, sleeper=slp)
    raise AssertionError("should exhaust")
except RetryExhausted as e:
    assert e.args[0] == "exhausted", e.args
assert n[0] == 3 and sleeps == [0.2, 0.4], (n[0], sleeps)

reset()
n[0] = 0
try:
    do_request(c503, max_attempts=1, now=now, sleeper=slp)
    raise AssertionError("should exhaust")
except RetryExhausted:
    pass
assert n[0] == 1 and sleeps == [], (n[0], sleeps)

# 6. past HTTP-date means wait 0.0 (still exactly one sleep, then success)
reset()
past = formatdate(T0 - 60, usegmt=True)
seq3 = [(503, {"Retry-After": past}, None), (200, {}, "back")]
assert do_request(lambda a: seq3[a], now=now, sleeper=slp) == "back"
assert sleeps == [0.0], sleeps

print("u09 PASS")
