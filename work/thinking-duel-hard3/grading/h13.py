import sys, copy

sys.path.insert(0, SYS_PATH)
from mpatch import merge_patch

assert merge_patch({"a": 1}, {"a": 2}) == {"a": 2}
assert merge_patch({"a": 1, "b": 2}, {"a": None}) == {"b": 2}
assert merge_patch({"a": [1]}, {"a": [2, 3]}) == {"a": [2, 3]}
assert merge_patch({"a": {"x": 1, "y": 2}}, {"a": {"y": None, "z": 3}}) == {
    "a": {"x": 1, "z": 3}
}
assert merge_patch([1], {"a": 1}) == {"a": 1}
assert merge_patch({"a": 1}, 5) == 5
t = {"a": {"x": 1}}
p = {"a": {"y": 2}}
t0, p0 = copy.deepcopy(t), copy.deepcopy(p)
merge_patch(t, p)
assert (t, p) == (t0, p0), "inputs mutated"
assert merge_patch({}, {"a": None}) == {}
print("h13 PASS")
