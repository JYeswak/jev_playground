import sys, inspect

sys.path.insert(0, SYS_PATH)
from subset import sample_k
import subset as shmod

assert "random" not in inspect.getsource(shmod), "no random module"


def ref(n, k, seed):
    xs = list(range(n))
    out = []
    s = seed % 2**31
    for i in range(n - 1, n - k - 1, -1):
        s = (1103515245 * s + 12345) % 2**31
        j = s % (i + 1)
        xs[i], xs[j] = xs[j], xs[i]
        out.append(xs[i])
    return out


for n, k, s in [(10, 3, 42), (52, 5, 7), (100, 10, 1), (5, 5, 9)]:
    assert sample_k(n, k, s) == ref(n, k, s), (n, k, s)
    assert len(set(sample_k(n, k, s))) == k
print("h07 PASS")
