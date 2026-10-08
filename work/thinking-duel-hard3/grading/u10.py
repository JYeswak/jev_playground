import sys
import itertools
import operator
import random


sys.path.insert(0, SYS_PATH)
from kmerge import merge_sorted

# 1. stability across sources with unorderable items sharing keys
s0 = [{"k": 1, "v": "a"}, {"k": 3, "v": "c"}]
s1 = [{"k": 1, "v": "b"}, {"k": 2, "v": "d"}, {"k": 3, "v": "e"}]
got = [(d["k"], d["v"]) for d in merge_sorted([s0, s1], key=operator.itemgetter("k"))]
assert got == [(1, "a"), (1, "b"), (2, "d"), (3, "c"), (3, "e")], got

# 2. laziness: pull counts stay bounded after taking only 3 outputs
pulls = [0, 0]
data = [[1, 4, 5, 9], [2, 3, 6]]


def counting(i):
    for x in data[i]:
        pulls[i] += 1
        yield x


out = list(itertools.islice(merge_sorted([counting(0), counting(1)]), 3))
assert out == [1, 2, 3], out
assert pulls == [2, 2], pulls

# 3. key function + one-shot / empty inputs
assert list(merge_sorted([["b", "D"], ["a", "C"]], key=str.lower)) == ["a", "b", "C", "D"]
assert list(merge_sorted([])) == []
assert list(merge_sorted([[], iter([]), [1]])) == [1]
assert list(merge_sorted(iter([iter([2]), iter([1])]))) == [1, 2]

# 4. three-way ties keep source order; randomized cross-check vs stable sort
t = merge_sorted([[(5, "a")], [(5, "b")], [(5, "c")]], key=lambda t: t[0])
assert [v for _, v in t] == ["a", "b", "c"]

random.seed(7)
srcs = [sorted(random.randint(0, 9) for _ in range(random.randint(0, 8))) for _ in range(5)]
tagged = [(x, i) for i, s in enumerate(srcs) for x in s]
want = [x for x, _ in sorted(tagged, key=lambda p: (p[0], p[1]))]
assert list(merge_sorted(srcs)) == want

print("u10 PASS")
