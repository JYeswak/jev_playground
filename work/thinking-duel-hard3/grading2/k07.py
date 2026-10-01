import sys

sys.path.insert(0, SYS_PATH)
from semver import intersect

assert intersect("^1.2.3", ">=1.5.0") == ((1, 5, 0), (2, 0, 0))
assert intersect("^0.2.3", ">=0.2.9") == ((0, 2, 9), (0, 3, 0))
assert intersect("^0.0.3", "~0.0.3") == ((0, 0, 3), (0, 0, 4))
assert intersect("~1.2.3", "<1.2.0") is None
assert intersect("*", "1.2.3") == ((1, 2, 3), (1, 2, 3))
assert intersect(">=2.0.0", "<2.0.0") is None
assert intersect("^1.0.0", "^2.0.0") is None
print("k07 PASS")
