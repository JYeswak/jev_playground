import sys

sys.path.insert(0, SYS_PATH)
from ivl import union, gaps

assert union([(5, 6), (1, 3), (2, 4)]) == [(1, 4), (5, 6)]
assert union([(1, 2), (2, 3)]) == [(1, 2), (2, 3)]
assert union([(1, 2), (2, 3)], merge_adjacent=True) == [(1, 3)]
assert union([]) == []
assert gaps([(1, 4), (5, 6)], (0, 8)) == [(0, 1), (4, 5), (6, 8)]
assert gaps([], (2, 5)) == [(2, 5)]
assert gaps([(0, 8)], (0, 8)) == []
print("k14 PASS")
