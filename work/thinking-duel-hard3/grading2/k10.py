import sys, threading

sys.path.insert(0, SYS_PATH)
from bucket import Bucket

t = [0.0]
b = Bucket(10.0, 5.0, now=lambda: t[0])
assert b.take(5) is True and b.take(1) is False
t[0] = 0.2
assert b.take(2) is True and b.take(1) is False
t[0] = 100.0
assert b.take(5) is True and b.take(1) is False
t2 = [0.0]
b2 = Bucket(1000.0, 1000.0, now=lambda: t2[0])
wins = [0]


def grab():
    for _ in range(200):
        if b2.take(1):
            wins[0] += 1


ths = [threading.Thread(target=grab) for _ in range(5)]
[x.start() for x in ths]
[x.join() for x in ths]
assert wins[0] == 1000, wins
print("k10 PASS")
