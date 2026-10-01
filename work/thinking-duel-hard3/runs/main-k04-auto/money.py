def split(cents, weights):
    if not weights:
        raise ValueError("empty")
    for w in weights:
        if w <= 0:
            raise ValueError("weights must be positive")
    total = sum(weights)
    base = [(cents * w) // total for w in weights]
    rems = [(cents * w) % total for w in weights]
    leftover = cents - sum(base)
    order = sorted(range(len(weights)), key=lambda i: (-rems[i], i))
    out = list(base)
    for k in range(leftover):
        out[order[k]] += 1
    return out
