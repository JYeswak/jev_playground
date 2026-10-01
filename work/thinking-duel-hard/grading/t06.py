import sys

sys.path.insert(0, SYS_PATH)
from touches import touched_ranks

assert touched_ranks("a/b.md", ["b.md"]) == [1]
assert touched_ranks("b.md", ["b.md"]) == [1]
assert touched_ranks("xb.md", ["b.md"]) == [1]
assert touched_ranks("", ["b.md"]) == []
assert touched_ranks("x", []) == []
assert touched_ranks("a/b/c.md", ["c.md", "b/c.md", "a/b/c.md"]) == [1, 2, 3]
assert touched_ranks("/r/src/x.py", ["x.py", "src/x.py"]) == [1, 2]
assert touched_ranks("nomatch", ["other"]) == []
print("t06 PASS")
