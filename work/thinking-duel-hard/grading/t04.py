import sys, math

sys.path.insert(0, SYS_PATH)
from wilson import wilson


def ref(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


for k, n in [(5, 350), (0, 350), (268, 300), (1, 1), (0, 10), (7, 13), (499, 1000)]:
    a, b = wilson(k, n), ref(k, n)
    assert abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9, (k, n, a, b)
    assert -1e-9 <= a[0] <= a[1] <= 1 + 1e-9, (k, n, a)
print("t04 PASS")
