import sys, inspect

sys.path.insert(0, SYS_PATH)
from rsv import sample
import rsv as shmod

assert "random" not in inspect.getsource(shmod), "no random module"


def ref(stream, k, seed):
    res = []
    s = seed % 2**31
    for idx, x in enumerate(stream, 1):
        s = (1103515245 * s + 12345) % 2**31
        j = s % idx
        if len(res) < k:
            res.append(x)
        elif j < k:
            res[j] = x
    return res


assert sample(iter(range(10)), 3, 42) == ref(iter(range(10)), 3, 42)
assert sample((x for x in range(100)), 5, 7) == ref((x for x in range(100)), 5, 7)
assert len(sample(iter(range(5)), 5, 1)) == 5
from collections import Counter

c = Counter()
for s in range(200):
    c.update(sample(range(20), 2, s))
assert min(c.values()) > 0, "coverage"
print("k16 PASS")
