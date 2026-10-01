import sys, time, threading

sys.path.insert(0, SYS_PATH)
from pmap import pmap

assert pmap(lambda x: x * 2, [1, 2, 3], 2) == [2, 4, 6]
active = 0
peak = [0]
lock = threading.Lock()


def work(x):
    global active
    with lock:
        active += 1
        peak[0] = max(peak[0], active)
    try:
        time.sleep(0.05)
        return x
    finally:
        with lock:
            active -= 1


assert pmap(work, list(range(10)), 3) == list(range(10))
assert peak[0] <= 3, peak
assert peak[0] >= 2, peak


def boom(x):
    if x == 2:
        raise ValueError("bad 2")
    time.sleep(0.3)
    return x


t = time.time()
try:
    pmap(boom, range(6), 3)
    raise SystemExit("h15 FAIL: no raise")
except ValueError:
    pass
assert time.time() - t < 3.0, "no prompt cancellation"
print("h15 PASS")
