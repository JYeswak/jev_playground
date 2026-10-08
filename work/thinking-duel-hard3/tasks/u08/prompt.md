# Task u08: largest-remainder money split

Work in $PWD. `money.py` has `allocate(total_cents, weights)` splitting an integer cent total across integer weights. It is wrong. Fix it, standard library only. Verify yourself with uneven splits, tie order, huge totals, and bad inputs.

Rules: `total_cents` is an `int >= 0` and `weights` a non-empty list of `int`s with at least one positive; anything else raises `ValueError`. Shares are proportional floors with the leftover cents dealt one each to the largest fractional remainders; remainder ties go to the lowest index first. Shares sum exactly to the total. Use integer arithmetic only (no float). `allocate(0, [5, 5]) == [0, 0]`.
