import sys

sys.path.insert(0, SYS_PATH)
from hist import bucket_bounds, assign

b = bucket_bounds(2, 4)
assert b == [1, 2, 4, 8, 16], b
assert assign(1, b) == 0
assert assign(3, b) == 1
assert assign(16, b) == 3
assert assign(0, b) == -1
assert assign(17, b) == -1
assert assign(8, b) == 3
assert assign(15.999, b) == 3
print("h14 PASS")
