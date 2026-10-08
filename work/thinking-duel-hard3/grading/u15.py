import random
import sys
from collections import deque

sys.path.insert(0, SYS_PATH)
from ldiff import diff_lists


def apply(seq, ops):
    s = list(seq)
    for op in ops:
        if op[0] == "del":
            del s[op[1]]
        elif op[0] == "ins":
            s.insert(op[1], op[2])
        elif op[0] == "move":
            x = s.pop(op[1])
            s.insert(op[2], x)
        else:
            raise AssertionError("bad op %r" % (op,))
    return s


def optimal_len(a, b):
    start, goal = tuple(a), tuple(b)
    if start == goal:
        return 0
    cap = len(a) + len(b)
    seen = {start}
    q = deque([(start, 0)])
    while q:
        state, d = q.popleft()
        n = len(state)
        nbrs = []
        for i in range(n):
            lst = list(state)
            del lst[i]
            nbrs.append(tuple(lst))
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                lst = list(state)
                x = lst.pop(i)
                lst.insert(j, x)
                if tuple(lst) != state:
                    nbrs.append(tuple(lst))
        for v in set(b):
            for j in range(n + 1):
                lst = list(state)
                lst.insert(j, v)
                if len(lst) <= cap:
                    nbrs.append(tuple(lst))
        for t in nbrs:
            if t == goal:
                return d + 1
            if t not in seen and len(t) <= cap and d + 1 < cap:
                seen.add(t)
                q.append((t, d + 1))
    return cap


small = [
    ([1, 2, 3], [3, 1, 2]),
    ([1, 2], [2, 1]),
    ([1, 2, 3], [1, 2, 3]),
    ([1, 2, 3], [1, 4, 3]),
    ([1], [2]),
    ([1, 1, 2], [1, 2, 1]),
    ([], [1, 2]),
    ([1, 2, 3], [3, 2, 1]),
]
for a, b in small:
    sc = diff_lists(a, b)
    assert apply(a, sc) == b, (a, b, sc)
    assert len(sc) == optimal_len(a, b), (a, b, sc)

sc = diff_lists([1, 2, 3, 4], [4, 1, 2, 3])
assert apply([1, 2, 3, 4], sc) == [4, 1, 2, 3]
assert any(op[0] == "move" for op in sc), sc

random.seed(7)
for trial in range(6):
    n = 12
    a = random.sample(range(40), n)
    b = a[:]
    random.shuffle(b)
    sc = diff_lists(a, b)
    assert apply(a, sc) == b, (trial, sc)
    assert len(sc) <= len(a) + len(b), (trial, sc)
a = [1] * 6 + [2] * 6
b = [2] * 6 + [1] * 6
sc = diff_lists(a, b)
assert apply(a, sc) == b
assert len(sc) <= len(a) + len(b)
print("u15 PASS")
