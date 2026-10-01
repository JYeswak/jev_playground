def union(intervals, merge_adjacent=False):
    out = []
    for lo, hi in sorted(intervals):
        if hi <= lo:
            continue
        if out and (lo < out[-1][1] or (merge_adjacent and lo == out[-1][1])):
            if hi > out[-1][1]:
                out[-1][1] = hi
        else:
            out.append([lo, hi])
    return [tuple(x) for x in out]


def gaps(merged, span):
    span_lo, span_hi = span
    if span_lo >= span_hi:
        return []
    out = []
    cur = span_lo
    for lo, hi in sorted(merged):
        if hi <= lo:
            continue
        if hi <= cur:
            continue
        if lo >= span_hi:
            break
        if lo > cur:
            out.append((cur, min(lo, span_hi)))
        if hi > cur:
            cur = hi
        if cur >= span_hi:
            break
    if cur < span_hi:
        out.append((cur, span_hi))
    return out
