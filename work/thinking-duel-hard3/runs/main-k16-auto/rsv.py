def sample(stream, k, seed):
    if k <= 0:
        # still consume stream (one pass) but return empty
        for _ in stream:
            pass
        return []
    state = seed % 2**31
    reservoir = []
    for idx, item in enumerate(stream):
        state = (1103515245 * state + 12345) % 2**31
        j = state % (idx + 1)
        if idx < k:
            reservoir.append(item)
        elif j < k:
            reservoir[j] = item
    return reservoir
