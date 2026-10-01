def leftmost_rot(a, x):
    for i, v in enumerate(a):
        if v == x:
            return i
    return -1
