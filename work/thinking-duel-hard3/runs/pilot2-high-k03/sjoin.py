import os


def safe_join(base, *parts):
    base_abs = os.path.abspath(base)
    rel = [p.lstrip(os.sep) for p in parts]
    p = os.path.normpath(os.path.join(base_abs, *rel))
    if p != base_abs and base_abs != os.sep and not p.startswith(base_abs + os.sep):
        raise ValueError("traversal")
    return p
