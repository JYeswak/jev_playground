import sys, math

sys.path.insert(0, SYS_PATH)
from ac import agresti_coull as ac


def ref(k, n, z=1.96):
    nt = n + z * z
    pt = (k + z * z / 2) / nt
    h = z * math.sqrt(pt * (1 - pt) / nt)
    return (pt - h, pt + h)


for k, n in [(5, 350), (0, 350), (268, 300), (0, 5), (3, 9), (99, 100)]:
    a, b = ac(k, n), ref(k, n)
    assert abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9, (k, n, a, b)
    assert a[0] <= a[1], (k, n, a)
print("h04 PASS")
