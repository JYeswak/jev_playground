import sys

sys.path.insert(0, SYS_PATH)
from resolver import resolve

idx = {"a": ["1.0.0", "1.5.0", "2.0.0"], "b": ["0.9.0"]}
assert resolve(idx, {"a": ("1.0.0", "2.0.0")}) == {"a": "1.5.0"}
assert resolve(idx, {"a": ("3.0.0", None)}) is None
assert resolve(idx, {"zzz": ("1.0.0", None)}) is None
assert resolve(idx, {"a": ("1.0.0", None), "b": ("0.1.0", "1.0.0")}) == {
    "a": "2.0.0",
    "b": "0.9.0",
}
assert resolve({"a": ["1.0.0"]}, {"a": ("2.0.0", None)}) is None
print("k12 PASS")
