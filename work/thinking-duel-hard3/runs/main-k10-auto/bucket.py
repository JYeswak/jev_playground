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
        with self.lock:
            t = self.now()
            elapsed = t - self.last
            if elapsed > 0:
                self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
                self.last = t
            if self.tokens >= n:
                self.tokens -= n
                return True
            return False
