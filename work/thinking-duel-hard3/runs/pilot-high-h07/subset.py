def sample_k(n, k, seed):
    if n < 0:
        raise ValueError("n must be >= 0")
    if k < 0 or k > n:
        raise ValueError("k must satisfy 0 <= k <= n")
    a = list(range(n))
    state = seed
    mod = 2**31
    out = []
    for i in range(n - 1, n - k - 1, -1):
        state = (1103515245 * state + 12345) % mod
        j = state % (i + 1)
        a[i], a[j] = a[j], a[i]
        out.append(a[i])
    return out
