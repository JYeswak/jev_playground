import sys

sys.path.insert(0, SYS_PATH)
from money import split

s = split(100, [1, 1, 1])
assert sum(s) == 100 and s == [34, 33, 33], s
assert split(1, [1, 1]) == [1, 0]
assert split(1000001, [3, 1]) == [750001, 250000]
assert split(10, [7, 2, 1]) == [7, 2, 1]
s = split(10**12 + 7, [1] * 7)
assert sum(s) == 10**12 + 7 and max(s) - min(s) <= 1, s
for bad in ([], [0, 0], [1, -1]):
    try:
        split(10, bad)
        raise SystemExit("k04 FAIL accepted")
    except ValueError:
        pass
print("k04 PASS")
