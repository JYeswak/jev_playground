def merge(streams, key=None):
    key = key or (lambda x: x)
    out = []
    for s in reversed(list(streams)):
        out.extend(s)
    out.sort(key=lambda x: key(x))
    return out
