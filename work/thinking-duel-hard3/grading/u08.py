import sys

sys.path.insert(0, SYS_PATH)
from money import allocate as a

# 1. uneven split: floors plus leftover to largest remainder
assert a(100, [1, 1, 1]) == [34, 33, 33]
assert a(10, [3, 1]) == [8, 2]
assert a(100, [3, 2, 1]) == [50, 33, 17]
assert a(5, [3, 1, 1]) == [3, 1, 1]
assert sum(a(100, [3, 2, 1])) == 100

# 2. tie order goes to lowest index; zero-weight parties get nothing extra
assert a(100, [1, 1, 1, 1]) == [25, 25, 25, 25]
assert a(10, [1, 1, 1]) == [4, 3, 3]
assert a(7, [0, 1, 1]) == [0, 4, 3]
assert a(0, [5, 5]) == [0, 0]
assert a(3, [2, 0, 0]) == [3, 0, 0]

# 3. huge totals stay exact with integer math (no float drift)
big = 10 ** 18 + 7
got = a(big, [3, 2, 1])
assert sum(got) == big, got
assert got == [500000000000000003, 333333333333333336, 166666666666666668], got
got = a(10 ** 15 + 1, [7, 7, 7])
assert sum(got) == 10 ** 15 + 1, got

# 4. invalid inputs raise ValueError (and banker's rounders fail the sum)
for args in ((-1, [1, 2]), (100, []), (100, [0, 0]),
             (100, [-1, 2]), (10.5, [1, 2]), (100, [1.5, 2]),
             ("100", [1, 2]), (100, "ab"), (100, [1, -1])):
    try:
        a(*args)
    except ValueError:
        pass
    else:
        raise SystemExit(f"u08 FAIL: accepted {args!r}")
assert sum(a(1, [1, 1, 1])) == 1
print("u08 PASS")
