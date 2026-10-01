def merge_patch(target, patch):
    if not isinstance(patch, dict):
        return patch
    for k, v in patch.items():
        if v is None:
            target.pop(k, None)
        elif isinstance(v, dict) and isinstance(target.get(k), dict):
            target[k] = merge_patch(target[k], v)
        else:
            target[k] = v
    return target
