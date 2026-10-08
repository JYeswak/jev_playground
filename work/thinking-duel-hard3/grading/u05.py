import sys
import threading
import time

sys.path.insert(0, SYS_PATH)
from memo import Memoizer

# 1. racy burst on one key: func runs exactly once, all callers agree
calls = []
gate = threading.Barrier(32)


def slow(key):
    time.sleep(0.2)
    calls.append(key)
    return key.upper()


mz = Memoizer(slow)
out = [None] * 32
errs = [None] * 32


def worker(i):
    gate.wait(timeout=10)
    try:
        out[i] = mz.get("k")
    except Exception as e:  # noqa: BLE001
        errs[i] = e


ts = [threading.Thread(target=worker, args=(i,)) for i in range(32)]
[t.start() for t in ts]
[t.join(timeout=30) for t in ts]
assert all(e is None for e in errs), errs
assert all(v == "K" for v in out), out
assert calls == ["k"], calls

# 2. exceptions are shared by waiters, never cached, retry heals
n = {"c": 0}
clock = threading.Lock()
gate2 = threading.Barrier(8)


def flaky(key):
    time.sleep(0.2)  # keep the call in flight so all waiters overlap it
    with clock:
        n["c"] += 1
        first = (n["c"] == 1)
    if first:
        raise RuntimeError("boom")
    return "ok"


mz2 = Memoizer(flaky)
res = [None] * 8
exc = [None] * 8


def w2(i):
    gate2.wait(timeout=10)
    try:
        res[i] = mz2.get("a")
    except RuntimeError as e:
        exc[i] = e


ts = [threading.Thread(target=w2, args=(i,)) for i in range(8)]
[t.start() for t in ts]
[t.join(timeout=30) for t in ts]
assert n["c"] == 1, n
assert all(isinstance(e, RuntimeError) for e in exc), (res, exc)
assert mz2.get("a") == "ok"
assert n["c"] == 2, n

# 3. mixed keys resolve independently, cached values never recompute
counts = {}
clock3 = threading.Lock()
gate3 = threading.Barrier(24)


def cnt(key):
    with clock3:
        counts[key] = counts.get(key, 0) + 1
    time.sleep(0.05)
    return key * 2


mz3 = Memoizer(cnt)


def w3(key):
    gate3.wait(timeout=10)
    for _ in range(5):
        assert mz3.get(key) == key * 2


threads = [threading.Thread(target=w3, args=(k,)) for k in ("x", "y", "z") for _ in range(8)]
[t.start() for t in threads]
[t.join(timeout=30) for t in threads]
assert counts == {"x": 1, "y": 1, "z": 1}, counts
print("u05 PASS")
