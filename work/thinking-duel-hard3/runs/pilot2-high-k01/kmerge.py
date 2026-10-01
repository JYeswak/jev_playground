import heapq


def merge(streams, key=None):
    return list(heapq.merge(*streams, key=key))
