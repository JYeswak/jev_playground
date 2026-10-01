import os


def safe_join(base, *parts):
    p = os.path.join(base, *parts)
    if not p.startswith(base):
        raise ValueError("traversal")
    return p
