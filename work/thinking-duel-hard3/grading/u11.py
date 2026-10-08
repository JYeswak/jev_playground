import sys
from datetime import datetime


sys.path.insert(0, SYS_PATH)
from cronnext import next_fire

D = datetime

# 1. dom-vs-dow OR: 1st-of-month OR Sunday at noon. From Thu 2026-10-01
# 13:00 (today's noon fire already missed), next is Sun 2026-10-04 12:00
# (AND logic would say 2026-11-01).
assert next_fire("0 12 1 * 0", D(2026, 10, 1, 13, 0)) == D(2026, 10, 4, 12, 0)
# dow-restricted-only still works: next Sunday midnight from Thursday.
assert next_fire("0 0 * * 0", D(2026, 10, 1, 0, 0)) == D(2026, 10, 4, 0, 0)

# 2. steps and ranges: */15 from 10:07 -> 10:15; 10-50/20 endpoints included.
assert next_fire("*/15 * * * *", D(2026, 10, 1, 10, 7)) == D(2026, 10, 1, 10, 15)
assert next_fire("10-50/20 * * * *", D(2026, 10, 1, 10, 0)) == D(2026, 10, 1, 10, 10)
assert next_fire("10-50/20 * * * *", D(2026, 10, 1, 10, 50)) == D(2026, 10, 1, 11, 10)

# 3. strictly after: an exact hit is skipped; seconds are truncated first.
assert next_fire("0 12 * * *", D(2026, 10, 1, 12, 0)) == D(2026, 10, 2, 12, 0)
assert next_fire("* * * * *", D(2026, 10, 1, 10, 0, 30)) == D(2026, 10, 1, 10, 1)

# 4. 7 is Sunday; month restriction; invalid input raises ValueError.
assert next_fire("0 0 * * 7", D(2026, 10, 3, 12, 0)) == D(2026, 10, 4, 0, 0)
assert next_fire("0 0 * 2 *", D(2026, 1, 15, 0, 0)) == D(2026, 2, 1, 0, 0)
for bad in ["61 * * * *", "*/0 * * * *", "* * * *", "0 0 0 * *"]:
    try:
        next_fire(bad, D(2026, 10, 1))
        raise AssertionError(f"{bad!r} should raise")
    except ValueError:
        pass

print("u11 PASS")
