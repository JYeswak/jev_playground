def union(intervals, merge_adjacent=False):
    ivs = sorted(intervals)
    out = []
    for lo, hi in ivs:
        if lo >= hi:
            continue
        if out and (lo < out[-1][1] or (merge_adjacent and lo <= out[-1][1])):
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
        if hi <= cur or lo >= span_hi:
            continue
        if lo > cur:
            out.append((cur, lo if lo < span_hi else span_hi))
        if hi > cur:
            cur = hi if hi < span_hi else span_hi
        if cur >= span_hi:
            break
    if cur < span_hi:
        out.append((cur, span_hi))
    return out
