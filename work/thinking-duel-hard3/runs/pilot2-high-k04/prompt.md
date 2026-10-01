# Task k04: exact money split

Work in $PWD. `money.py` has `split(cents, weights)` splitting integer
`cents` across integer `weights` proportionally, returning integer shares
summing EXACTLY to cents (largest-remainder on exact fractional parts, ties
to lower index). Exact integer arithmetic only (no floats). Zero/negative
weights and empty weights raise ValueError. shipped code uses floats and
drifts. Fix it. Verify yourself.
