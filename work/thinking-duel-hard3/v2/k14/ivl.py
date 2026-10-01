def union(intervals, merge_adjacent=False):
    ivs = sorted(intervals)
    out = []
    for lo, hi in ivs:
        if out and lo <= out[-1][1]:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return [tuple(x) for x in out]


def gaps(merged, span):
    return []
