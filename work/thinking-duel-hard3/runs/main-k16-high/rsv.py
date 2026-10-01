def sample(stream, k, seed):
    if k <= 0:
        for _ in stream:
            pass
        return []
    reservoir = []
    state = seed % 2147483648
    for idx, item in enumerate(stream):
        if idx < k:
            reservoir.append(item)
        else:
            state = (1103515245 * state + 12345) % 2147483648
            j = state % (idx + 1)
            if j < k:
                reservoir[j] = item
    return reservoir
