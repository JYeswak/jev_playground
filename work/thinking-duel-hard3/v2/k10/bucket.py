import time, threading


class Bucket:
    def __init__(self, rate, burst, now=None):
        self.rate = rate
        self.burst = burst
        self.now = now or time.monotonic
        self.tokens = burst
        self.last = self.now()
        self.lock = threading.Lock()

    def take(self, n=1):
        self.tokens = self.tokens + (self.now() - self.last) * self.rate
        self.last = self.now()
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False
