import sys

sys.path.insert(0, SYS_PATH)
from patcher import apply_patch

orig = "a\nb\nc\nd\ne\n"
diff = (
    "--- f\n+++ f\n@@ -2,2 +2,3 @@\n b\n-c\n+C\n+c2\n d\n" "@@ -5,1 +6,1 @@\n-e\n+E\n"
)
got = apply_patch(orig, diff)
assert got == "a\nb\nC\nc2\nd\nE\n", repr(got)
try:
    apply_patch(orig, "--- f\n+++ f\n@@ -2,1 +2,1 @@\n-X\n")
    raise SystemExit("k09 FAIL no raise")
except ValueError:
    pass
assert apply_patch("x\n", "") == "x\n"
print("k09 PASS")
