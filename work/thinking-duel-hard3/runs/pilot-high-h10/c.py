import time


class Cache:
    def __init__(self, capacity, ttl, now=None):
        self.cap = capacity
        self.ttl = ttl
        self.now = now or time.monotonic
        self.d = {}  # k -> [value, put_time, freq, recency]
        self._tick = 0

    def _expired(self, put_time, t):
        return (t - put_time) > self.ttl

    def _purge(self, t):
        for k in list(self.d.keys()):
            _, ts, _, _ = self.d[k]
            if self._expired(ts, t):
                del self.d[k]

    def _use(self, k):
        self._tick += 1
        self.d[k][2] += 1
        self.d[k][3] = self._tick

    def get(self, k):
        t = self.now()
        if k not in self.d:
            # still purge expired so they never linger/count
            self._purge(t)
            return None
        v, ts, _, _ = self.d[k]
        if self._expired(ts, t):
            del self.d[k]
            self._purge(t)
            return None
        self._purge(t)
        self._use(k)
        return self.d[k][0]

    def put(self, k, v):
        t = self.now()
        if k in self.d:
            _, ts, _, _ = self.d[k]
            if self._expired(ts, t):
                del self.d[k]
            else:
                self.d[k][0] = v
                self.d[k][1] = t
                self._purge(t)
                # purge cannot remove k (just refreshed); guard anyway
                if k in self.d:
                    self._use(k)
                else:
                    self._tick += 1
                    self.d[k] = [v, t, 1, self._tick]
                return
        self._purge(t)
        if self.cap <= 0:
            return
        if k not in self.d and len(self.d) >= self.cap:
            # evict LFU, ties -> LRU (smallest recency)
            victim = min(self.d.keys(), key=lambda x: (self.d[x][2], self.d[x][3]))
            del self.d[victim]
        self._tick += 1
        self.d[k] = [v, t, 1, self._tick]
