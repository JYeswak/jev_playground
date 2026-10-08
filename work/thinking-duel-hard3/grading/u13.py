import sys
import time

sys.path.insert(0, SYS_PATH)
from limiter import RateLimiter

r = RateLimiter(3, 10.0)
assert [r.allow(t) for t in (0.0, 1.0, 2.0)] == [True] * 3
assert r.allow(3.0) is False

r = RateLimiter(1, 10.0)
assert r.allow(0.0) is True
assert r.allow(10.0) is True

r = RateLimiter(2, 10.0)
assert r.allow(0.0) is True and r.allow(1.0) is True
assert r.allow(5.0) is False
assert r.allow(10.0) is True
assert r.allow(10.0) is False

r = RateLimiter(2, 10.0)
assert r.allow(0.0) is True and r.allow(1.0) is True
assert r.allow(2.0) is False
assert r.allow(10.0) is True
assert r.allow(11.0) is True

r = RateLimiter(1, 10.0)
real_m, real_t = time.monotonic, time.time
try:
    time.monotonic = lambda: 100.0
    time.time = lambda: 0.0
    assert r.allow() is True
    time.monotonic = lambda: 101.0
    assert r.allow() is False
    time.monotonic = lambda: 200.0
    assert r.allow() is True
finally:
    time.monotonic, time.time = real_m, real_t
print("u13 PASS")
