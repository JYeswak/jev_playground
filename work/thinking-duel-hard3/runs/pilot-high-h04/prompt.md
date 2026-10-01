# Task h04: Agresti-Coull interval

Work in $PWD. `ac.py` has `agresti_coull(k, n, z=1.96)` returning `(lo, hi)`:
tilde_n = n + z^2, tilde_p = (k + z^2/2) / tilde_n,
half = z * sqrt(tilde_p * (1 - tilde_p) / tilde_n), return
(tilde_p - half, tilde_p + half). It is wrong. Fix it to match reference to
1e-9 with outputs inside [0, 1] within 1e-9 slop. stdlib only. Verify.
