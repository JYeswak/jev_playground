import sys

sys.path.insert(0, SYS_PATH)
from touches import touched_ranks

assert touched_ranks("a/b.md", ["b.md"]) == [1]
assert touched_ranks("src/x_test.py", ["*_test.py"]) == [1]
assert touched_ranks("a/b/c.md", ["*.md", "b/*.md"]) == [1, 2]
assert touched_ranks("nomatch.py", ["*.md"]) == []
assert touched_ranks("", ["*"]) == []
assert touched_ranks("x", []) == []
assert touched_ranks("a/b.md", ["b.md", "A/B.MD"]) == [1]
print("h06 PASS")
