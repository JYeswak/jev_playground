def bucket_bounds(base, n):
    return [base**i for i in range(n + 1)]


def assign(v, bounds):
    for i in range(len(bounds) - 1):
        if bounds[i] <= v < bounds[i + 1]:
            return i
    if len(bounds) >= 2 and v == bounds[-1]:
        return len(bounds) - 2
    return -1
