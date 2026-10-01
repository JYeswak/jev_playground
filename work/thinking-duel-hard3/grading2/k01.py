import sys

sys.path.insert(0, SYS_PATH)
from kmerge import merge

assert merge([[], [], []]) == []
r = merge([[(1, "a"), (2, "b")], [(1, "c"), (3, "d")]], key=lambda t: t[0])
assert r == [(1, "a"), (1, "c"), (2, "b"), (3, "d")], r


def gen(xs):
    yield from xs


r = merge([gen([1, 3]), gen([]), gen([2])])
assert r == [1, 2, 3], r
r = merge([[("y", 1), ("x", 2)]], key=lambda t: t[1])
assert r == [("y", 1), ("x", 2)], r
print("k01 PASS")
