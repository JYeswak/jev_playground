import os


def safe_join(base, *parts):
    base_abs = os.path.abspath(base)
    rel_parts = [p.lstrip("/") for p in parts]
    p = os.path.normpath(os.path.join(base_abs, *rel_parts))
    if p == base_abs:
        return p
    if base_abs == os.sep:
        return p
    if p.startswith(base_abs + os.sep):
        return p
    raise ValueError("traversal")
