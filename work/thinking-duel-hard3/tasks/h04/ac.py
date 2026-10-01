def agresti_coull(k, n, z=1.96):
    p = k / n
    half = z * (p * (1 - p) / n) ** 0.5
    return (p - half, p + half)
