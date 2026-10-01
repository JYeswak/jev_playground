def union(intervals, merge_adjacent=False):
    ivs = sorted(intervals)
    out = []
    for lo, hi in ivs:
        if hi <= lo:
            continue
        if out and (lo < out[-1][1] or (merge_adjacent and lo <= out[-1][1])):
            if hi > out[-1][1]:
                out[-1][1] = hi
        else:
            out.append([lo, hi])
    return [tuple(x) for x in out]


def gaps(merged, span):
    slo, shi = span
    if slo >= shi:
        return []
    out = []
    cur = slo
    for lo, hi in sorted(merged):
        if hi <= lo:
            continue
        if hi <= cur:
            continue
        if lo >= shi:
            break
        if lo > cur:
            out.append((cur, min(lo, shi)))
        if hi > cur:
            cur = hi
        if cur >= shi:
            break
    if cur < shi:
        out.append((cur, shi))
    return out
