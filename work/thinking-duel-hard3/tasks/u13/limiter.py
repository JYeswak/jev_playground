"""Sliding-window rate limiter (buggy starter)."""

import time
from collections import deque


class RateLimiter:
    def __init__(self, limit, window):
        self.limit = limit
        self.window = window
        self._hits = deque()

    def allow(self, now=None):
        t = time.time() if now is None else now
        while self._hits and self._hits[0] < t - self.window:
            self._hits.popleft()
        if len(self._hits) <= self.limit:
            self._hits.append(t)
            return True
        return False
