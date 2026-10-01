def order(n, seed):
    xs = list(range(n))
    state = seed % 2**31
    for i in range(n - 1, 0, -1):
        state = (1103515245 * state + 12345) % 2**31
        j = state % (i + 1)
        xs[i], xs[j] = xs[j], xs[i]
    return xs
