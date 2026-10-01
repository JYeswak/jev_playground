import sys

sys.path.insert(0, SYS_PATH)
from cronx import next_fire
from datetime import datetime as dt

assert next_fire("0 9", dt(2026, 1, 1, 8, 0)) == dt(2026, 1, 1, 9, 0)
assert next_fire("0 9", dt(2026, 1, 1, 9, 0)) == dt(2026, 1, 2, 9, 0)
assert next_fire("*/15 *", dt(2026, 1, 1, 10, 7)) == dt(2026, 1, 1, 10, 15)
assert next_fire("30 23", dt(2026, 1, 1, 23, 45)) == dt(2026, 1, 2, 23, 30)
assert next_fire("0 0", dt(2026, 1, 1, 0, 0)) == dt(2026, 1, 2, 0, 0)
assert next_fire("5 4", dt(2026, 1, 1, 4, 5)) == dt(2026, 1, 2, 4, 5)
assert next_fire("0,30 12", dt(2026, 1, 1, 12, 30)) == dt(2026, 1, 2, 12, 0)
print("h16 PASS")
