import sys

sys.path.insert(0, SYS_PATH)
from wrap import wrap

assert wrap("hello world", 5) == ["hello", "world"]
assert wrap("ab cd", 4) == ["ab", "cd"]
assert wrap("\u4e2d\u6587\u6d4b\u8bd5", 4) == ["\u4e2d\u6587", "\u6d4b\u8bd5"]
assert wrap("a\u4e2d b", 3) == ["a\u4e2d", "b"]
assert wrap("e\u0301e", 2) == ["e\u0301e"]
assert wrap("supercalifragilistic", 5) == ["supercalifragilistic"]
assert wrap("", 5) == []
print("k06 PASS")
