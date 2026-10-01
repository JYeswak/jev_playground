def split(cents, weights):
    if not weights:
        raise ValueError("empty")
    for w in weights:
        if not isinstance(w, int) or isinstance(w, bool) or w <= 0:
            raise ValueError("weights must be positive ints")
    if not isinstance(cents, int) or isinstance(cents, bool):
        raise ValueError("cents must be int")
    total = sum(weights)
    floors = [(cents * w) // total for w in weights]
    rem = [(cents * w) % total for w in weights]
    leftover = cents - sum(floors)
    order = sorted(range(len(weights)), key=lambda i: (-rem[i], i))
    for k in range(leftover):
        floors[order[k]] += 1
    return floors
