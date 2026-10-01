# Task t10: TTL LRU cache

Work in $PWD. `ttlcache.py` has `TTLCache(capacity, ttl, now=time.monotonic)`
with `get(k)`/`put(k, v)`. It must: evict least-recently-used beyond
capacity; expire entries older than ttl seconds (using `now()`); return None
for missing/expired keys; refresh recency on get and put. It is wrong. Fix
it, standard library only. Verify yourself with a fake clock.
