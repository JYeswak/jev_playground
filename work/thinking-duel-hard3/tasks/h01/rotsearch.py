def leftmost_rot(a, x):
    found = -1
    for i, v in enumerate(a):
        if v == x:
            found = i
    return found
