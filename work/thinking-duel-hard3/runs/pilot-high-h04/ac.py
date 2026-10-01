def agresti_coull(k, n, z=1.96):
    z2 = z * z
    tilde_n = n + z2
    tilde_p = (k + z2 / 2) / tilde_n
    half = z * (tilde_p * (1 - tilde_p) / tilde_n) ** 0.5
    lo = tilde_p - half
    hi = tilde_p + half
    if lo < 0:
        lo = 0.0
    elif lo > 1:
        lo = 1.0
    if hi < 0:
        hi = 0.0
    elif hi > 1:
        hi = 1.0
    return (lo, hi)
