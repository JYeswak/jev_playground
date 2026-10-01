import os


def safe_join(base, *parts):
    base_abs = os.path.abspath(os.path.normpath(base))
    rel = [p.lstrip("/") for p in parts]
    joined = os.path.join(base_abs, *rel) if rel else base_abs
    norm = os.path.normpath(joined)
    if norm != base_abs and not norm.startswith(base_abs + os.sep):
        raise ValueError("traversal")
    return norm
