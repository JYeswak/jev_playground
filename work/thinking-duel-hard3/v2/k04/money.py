def split(cents, weights):
    if not weights:
        raise ValueError("empty")
    total = sum(weights)
    out = [int(cents * w / total) for w in weights]
    return out
