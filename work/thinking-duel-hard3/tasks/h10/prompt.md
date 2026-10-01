# Task h10: TTL LFU cache

Work in $PWD. `c.py` has `Cache(capacity, ttl, now=time.monotonic)` with
`get(k)`/`put(k, v)`. Eviction beyond capacity removes the
least-frequently-used entry (ties -> least recently used); entries older
than ttl (by `now()`) are expired on access and never returned; get and put
both count as a use and refresh recency; put on an existing key updates the
value and counts as a use. shipped code is plain TTL LRU and wrong. Fix it,
stdlib only. Verify with a fake clock.
