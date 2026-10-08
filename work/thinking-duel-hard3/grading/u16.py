import sys

sys.path.insert(0, SYS_PATH)
from semrange import intersects

assert intersects("^1.2.3", "^1.4.0") is True
assert intersects("^0.2.3", "^0.3.0") is False
assert intersects("~1.2.3", "~1.3.0") is False
assert intersects("^1.3.0", "1.2.0 - 1.3.0") is True
assert intersects("1.2.x", "1.2.5 - 1.3.0") is True
assert intersects("2.x", "^1.0.0") is False
assert intersects("^1.0.0", "1.0.1-alpha") is False
assert intersects(">=1.0.1-alpha <2.0.0", "1.0.1-beta") is True
assert intersects(">=1.0.0 <2.0.0", ">=2.0.0 <3.0.0") is False
assert intersects("~1", "^1.5.0") is True
print("u16 PASS")
