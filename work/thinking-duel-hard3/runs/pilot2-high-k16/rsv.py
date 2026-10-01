"""Reservoir sampling (Algorithm R) with an inline LCG.

One pass over an arbitrary iterable, O(k) memory, deterministic per seed.
No `random` module: j comes from state = (1103515245 * state + 12345) % 2**31.
"""

_MOD = 2**31
_MUL = 1103515245
_INC = 12345


def sample(stream, k, seed=0):
    if k < 0:
        raise ValueError("k must be non-negative")
    state = seed
    reservoir = []
    for item_index, item in enumerate(stream):
        if item_index < k:
            reservoir.append(item)
        else:
            state = (_MUL * state + _INC) % _MOD
            j = state % (item_index + 1)
            if j < k:
                reservoir[j] = item
    return reservoir
