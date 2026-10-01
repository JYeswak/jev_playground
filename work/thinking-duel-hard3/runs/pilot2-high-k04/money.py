def split(cents, weights):
    if isinstance(cents, bool) or not isinstance(cents, int):
        raise ValueError("cents must be int")
    if not weights:
        raise ValueError("empty")
    ws = list(weights)
    for w in ws:
        if isinstance(w, bool) or not isinstance(w, int) or w <= 0:
            raise ValueError("bad weight")
    total = sum(ws)
    floors = [(cents * w) // total for w in ws]
    rems = [(cents * w) % total for w in ws]
    leftover = cents - sum(floors)
    order = sorted(range(len(ws)), key=lambda i: (-rems[i], i))
    out = list(floors)
    for i in order[:leftover]:
        out[i] += 1
    return out
