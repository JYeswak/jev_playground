import sys

sys.path.insert(0, SYS_PATH)
from flaky import find_flaky

r = {
    "steady-pass": [True] * 20,
    "steady-fail": [False] * 20,
    "flaky": [True] * 14 + [False] * 6,
    "rare": [True] * 9 + [False],
    "few": [True, False],
    "empty": [],
    "edge-lo": [True] * 19 + [False],
    "edge-hi": [True] + [False] * 19,
}
got = find_flaky(r)
assert got == ["edge-hi", "edge-lo", "flaky", "rare"], got
assert find_flaky(r, min_runs=25) == []
assert find_flaky({"a": [True, False] * 5}, lo=0.4, hi=0.6) == ["a"]
print("k05 PASS")
