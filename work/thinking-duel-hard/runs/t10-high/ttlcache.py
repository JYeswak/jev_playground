import time
from collections import OrderedDict


class TTLCache:
    def __init__(self, capacity, ttl, now=None):
        self.cap = capacity
        self.ttl = ttl
        self.now = now or time.monotonic
        self.d = OrderedDict()

    def _expired(self, ts, t):
        return (t - ts) > self.ttl

    def _purge(self, t):
        for k in [k for k, (_, ts) in self.d.items() if self._expired(ts, t)]:
            del self.d[k]

    def get(self, k):
        t = self.now()
        self._purge(t)
        if k not in self.d:
            return None
        v, _ = self.d[k]
        self.d.move_to_end(k)
        return v

    def put(self, k, v):
        t = self.now()
        self._purge(t)
        # refresh timestamp + recency even on overwrite
        if k in self.d:
            del self.d[k]
        self.d[k] = (v, t)
        while len(self.d) > self.cap:
            self.d.popitem(last=False)
