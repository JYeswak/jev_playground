import time
from collections import OrderedDict


class TTLCache:
    def __init__(self, capacity, ttl, now=None):
        self.cap = capacity
        self.ttl = ttl
        self.now = now or time.monotonic
        self.d = OrderedDict()

    def get(self, k):
        if k not in self.d:
            return None
        v, _ = self.d[k]
        self.d.move_to_end(k)
        return v

    def put(self, k, v):
        self.d[k] = (v, self.now())
        self.d.move_to_end(k)
        while len(self.d) > self.cap:
            self.d.popitem(last=False)
