import sys

sys.path.insert(0, SYS_PATH)
from topo import order

ok, res = order({"a": ["b"], "b": ["c"], "c": []})
assert ok and res == ["c", "b", "a"], res
ok, res = order({"a": ["b"], "b": ["a"]})
assert not ok and res[0] == res[-1] and set(res[:-1]) == {"a", "b"}, res
ok, res = order({"m": ["n", "o"], "n": ["o"], "o": []})
assert ok and res.index("o") < res.index("n") < res.index("m"), res
ok, res = order({"x": ["y"], "y": ["z"], "z": ["y"]})
assert not ok and res[0] == res[-1] and set(res[:-1]) == {"y", "z"}, res
ok, res = order({})
assert ok and res == []
ok, res = order({"s": ["s"]})
assert not ok and res == ["s", "s"], res
print("t11 PASS")
