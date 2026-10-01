import heapq


def merge(streams, key=None):
    streams = list(streams)
    if key is None:
        return list(heapq.merge(*streams))
    return list(heapq.merge(*streams, key=key))
