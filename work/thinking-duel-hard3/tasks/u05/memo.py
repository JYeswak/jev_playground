class Memoizer:
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        value = self.func(key)
        self.cache[key] = value
        return value
