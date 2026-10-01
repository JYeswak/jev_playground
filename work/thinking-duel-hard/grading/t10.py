import sys

sys.path.insert(0, SYS_PATH)
from ttlcache import TTLCache

t = [100.0]
c = TTLCache(2, 10.0, now=lambda: t[0])
c.put("a", 1)
c.put("b", 2)
assert c.get("a") == 1
c.put("c", 3)
assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3
t[0] = 111.0
assert c.get("a") is None and c.get("c") is None
c.put("d", 4)
t[0] = 115.0
assert c.get("d") == 4
t[0] = 130.0
assert c.get("d") is None
print("t10 PASS")
