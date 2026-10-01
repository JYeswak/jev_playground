def pmap(fn, items, limit):
    return [fn(x) for x in items]
