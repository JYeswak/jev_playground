import heapq


def merge_sorted(sources, key=None):
    key = key or (lambda x: x)
    heap = []
    for src in sources:
        for x in src:
            heapq.heappush(heap, (key(x), x))
    while heap:
        yield heapq.heappop(heap)[1]
