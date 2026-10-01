import sys, os

sys.path.insert(0, SYS_PATH)
from sjoin import safe_join

assert safe_join("/tmp/x", "a", "b") == "/tmp/x/a/b"
assert safe_join("/tmp/x", "/a") == "/tmp/x/a"
assert safe_join("/tmp/x", "a/./b//c") == "/tmp/x/a/b/c"
for bad in ["..", "../e", "a/../../e", "../x-evil/f"]:
    try:
        safe_join("/tmp/x", bad)
    except ValueError:
        continue
    raise SystemExit("k03 FAIL accepted")
try:
    safe_join("/tmp/x", "..")
    raise SystemExit("k03 FAIL dotdot")
except ValueError:
    pass
print("k03 PASS")
