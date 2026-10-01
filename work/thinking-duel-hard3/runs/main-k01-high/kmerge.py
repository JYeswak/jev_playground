import heapq


def merge(streams, key=None):
    keyfunc = key if key is not None else (lambda x: x)
    heap = []
    out = []
    for idx, s in enumerate(streams):
        it = iter(s)
        try:
            first = next(it)
        except StopIteration:
            continue
        heapq.heappush(heap, (keyfunc(first), idx, first, it))
    while heap:
        _, idx, val, it = heapq.heappop(heap)
        out.append(val)
        try:
            nxt = next(it)
        except StopIteration:
            continue
        heapq.heappush(heap, (keyfunc(nxt), idx, nxt, it))
    return out
