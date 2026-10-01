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
        if k not in self.d:
            return None
        v, ts = self.d[k]
        if self._expired(ts, self.now()):
            del self.d[k]
            return None
        self.d.move_to_end(k)
        return v

    def put(self, k, v):
        t = self.now()
        self._purge(t)
        self.d[k] = (v, t)
        self.d.move_to_end(k)
        while len(self.d) > self.cap:
            self.d.popitem(last=False)
