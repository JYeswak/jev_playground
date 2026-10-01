import sys

sys.path.insert(0, SYS_PATH)
from c import Cache

t = [0.0]
c = Cache(2, 100.0, now=lambda: t[0])
c.put("a", 1)
c.put("b", 2)
c.get("a")
c.get("a")
c.get("b")
c.put("c", 3)
assert c.get("a") == 1 and c.get("c") == 3 and c.get("b") is None
c.put("d", 4)
assert c.get("c") is None and c.get("d") == 4 and c.get("a") == 1
t[0] = 200.0
assert c.get("a") is None and c.get("d") is None
print("h10 PASS")
