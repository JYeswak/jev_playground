import sys

sys.path.insert(0, SYS_PATH)
from durations import parse_duration as p

DAY = 86400.0

# 1. basics, weeks-alone, and week-combination rejection
assert p("PT0S") == 0
assert p("P1D") == DAY
assert p("P1W") == 7 * DAY
assert p("P2W") == 14 * DAY
for bad in ("P1W1D", "P1WT2H", "P1Y1W", "P1M1W", "P", "PT", "P1YT"):
    try:
        p(bad)
    except ValueError:
        pass
    else:
        raise SystemExit(f"u06 FAIL: accepted {bad!r}")

# 2. full span, month-vs-minute disambiguation, negatives
assert p("P1Y2M3DT4H5M6S") == (365 + 60 + 3) * DAY + 4 * 3600 + 5 * 60 + 6
assert p("P1M") == 30 * DAY
assert p("PT1M") == 60.0
assert p("P1M2D") == 32 * DAY
assert p("-P1D") == -DAY
assert p("-PT2H30M") == -(2 * 3600 + 30 * 60)
assert abs(p("PT0.5S") - 0.5) < 1e-9
assert abs(p("PT1,5S") - 1.5) < 1e-9
assert abs(p("P1DT2H") - (DAY + 7200)) < 1e-9
try:
    p("--P1D")
except ValueError:
    pass
else:
    raise SystemExit("u06 FAIL: accepted double negative")

# 3. fractions: only the last component may be fractional
assert abs(p("PT1H0.5M") - 3630.0) < 1e-9
assert abs(p("P0.5Y") - 0.5 * 365 * DAY) < 1e-6
assert abs(p("PT2,5H") - 2.5 * 3600) < 1e-9
for bad in ("PT1.5H2M", "P1.5Y2M", "PT1.5M2S", "P1.5D2H", "PT1H2.5M3S"):
    try:
        p(bad)
    except ValueError:
        pass
    else:
        raise SystemExit(f"u06 FAIL: accepted non-final fraction {bad!r}")

# 4. malformed shapes and ordering violations
for bad in ("", "hello", "1D", "P1S", "PT1Y", "P1H", "PD", "P1D2Y",
            "PT1S1H", "P1DT", "P-1D", "PT1H ", " P1D", "P1.2.3D", "P--1D"):
    try:
        p(bad)
    except ValueError:
        pass
    else:
        raise SystemExit(f"u06 FAIL: accepted {bad!r}")
print("u06 PASS")
