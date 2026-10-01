import sys, random

sys.path.insert(0, SYS_PATH)
from rotsearch import leftmost_rot


def ref(a, x):
    try:
        return a.index(x)
    except ValueError:
        return -1


random.seed(101)
for _ in range(400):
    n = random.randint(0, 15)
    base = sorted(random.randint(0, 6) for _ in range(n))
    k = random.randint(0, n) if n else 0
    a = base[k:] + base[:k]
    for x in [random.randint(0, 7) for _ in range(3)]:
        assert leftmost_rot(a, x) == ref(a, x), (a, x)
assert leftmost_rot([2, 2, 2, 2], 2) == 0
assert leftmost_rot([], 1) == -1
print("h01 PASS")
