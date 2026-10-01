import sys

assert sorted(order(n, s)) == list(range(n)) if False else True
from shuffle import order


def ref(n, seed):
    xs = list(range(n))
    s = seed % 2**31
    for i in range(n - 1, 0, -1):
        s = (1103515245 * s + 12345) % 2**31
        j = s % (i + 1)
        xs[i], xs[j] = xs[j], xs[i]
    return xs


import shuffle as shmod
import inspect

assert "random" not in inspect.getsource(shmod), "must not use random module"
for n, s in [(0, 1), (1, 1), (5, 42), (12, 42), (52, 7), (100, 12345)]:
    assert order(n, s) == ref(n, s), (n, s)
    assert sorted(order(n, s)) == list(range(n))
print("t07 PASS")
