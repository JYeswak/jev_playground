import sys

sys.path.insert(0, SYS_PATH)
from jptr import pointer_get

assert pointer_get({"a/b": 1, "m~n": 2}, "/a~1b") == 1
assert pointer_get({"a/b": 1, "m~n": 2}, "/m~0n") == 2
assert pointer_get({"~1": 3, "/": 4}, "/~01") == 3
assert pointer_get({"": 5}, "/") == 5
assert pointer_get({"a": [10, 20]}, "/a/1") == 20
assert pointer_get([1, {"x": 2}], "/1/x") == 2
assert pointer_get({"a": 1}, "") == {"a": 1}
try:
    pointer_get({"a": 1}, "/b")
    assert False, "missing key must raise"
except KeyError:
    pass
try:
    pointer_get({"a": [1]}, "/a/-")
    assert False, "'-' must raise"
except IndexError:
    pass
try:
    pointer_get({"a": [1]}, "/a/5")
    assert False, "oob must raise"
except IndexError:
    pass
try:
    pointer_get({"a": 1}, "/a/b")
    assert False, "scalar traversal must raise"
except TypeError:
    pass
try:
    pointer_get({"a": 1}, "a")
    assert False, "relative pointer must raise"
except ValueError:
    pass
try:
    pointer_get({"a": 1}, "/a~2")
    assert False, "bad escape must raise"
except ValueError:
    pass
print("u14 PASS")
