import os
import sys
import tempfile
import time

sys.path.insert(0, SYS_PATH)
from lockfile import acquire_lock, release_lock, write_atomically

d = tempfile.mkdtemp()
lp = os.path.join(d, "x.lock")

# 1. basic acquire / held / release / re-acquire
assert acquire_lock(lp) is True
assert acquire_lock(lp) is False
release_lock(lp)
assert acquire_lock(lp) is True
release_lock(lp)

# 2. stale lock (mtime far past stale_after) must be stolen
with open(lp, "w") as f:
    f.write("999999")
old = time.time() - 3600
os.utime(lp, (old, old))
assert acquire_lock(lp, stale_after=10) is True
release_lock(lp)

# 3. fresh lock must NOT be stolen and must be left intact
with open(lp, "w") as f:
    f.write("owner-data")
assert acquire_lock(lp, stale_after=3600) is False
with open(lp) as f:
    assert f.read() == "owner-data"
os.remove(lp)

# 4. releasing an absent lock is a silent no-op
release_lock(os.path.join(d, "nope.lock"))

# 5. atomic write: exact bytes, overwrite, no temp files left
t = os.path.join(d, "data.bin")
write_atomically(t, b"hello")
with open(t, "rb") as f:
    assert f.read() == b"hello"
write_atomically(t, b"world")
with open(t, "rb") as f:
    assert f.read() == b"world"
leftovers = [p for p in os.listdir(d) if p.startswith("data.bin.")]
assert leftovers == [], leftovers
print("u01 PASS")
