import sys

sys.path.insert(0, SYS_PATH)
from topo import order

ok, res = order({"b": [], "a": []})
assert ok and res == ["a", "b"], res
ok, res = order({"c": ["a"], "b": ["a"], "a": []})
assert ok and res == ["a", "b", "c"], res
ok, res = order({"z": ["a"], "a": []})
assert ok and res == ["a", "z"], res
ok, res = order({"m": ["n"]})
assert ok and res == ["n", "m"], res
ok, res = order({"a": ["b"], "b": ["a"]})
assert not ok and res[0] == res[-1] and set(res[:-1]) == {"a", "b"}, res
ok, res = order({"x": ["y", "z"], "y": ["w"], "z": ["w"], "w": []})
assert ok and res == ["w", "y", "z", "x"], res
print("h11 PASS")
