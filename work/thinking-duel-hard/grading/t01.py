import random, sys

sys.path.insert(0, SYS_PATH)
from search import bisect_leftmost


def ref(a, x):
    try:
        return a.index(x)
    except ValueError:
        return -1


cases = [[], [1], [1, 2, 2, 3], [2, 2, 2], [1, 3, 5], list(range(0, 100, 3))]
random.seed(11)
for _ in range(300):
    n = random.randint(0, 12)
    a = sorted(random.randint(0, 5) for _ in range(n))
    for x in [random.randint(0, 6) for _ in range(4)]:
        assert bisect_leftmost(a, x) == ref(a, x), (a, x)
for a in cases:
    for x in [-1, 0, 1, 2, 3, 5, 99, 100]:
        assert bisect_leftmost(a, x) == ref(a, x), (a, x)
print("t01 PASS")
