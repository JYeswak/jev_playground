"""RFC 6901 JSON pointer lookup (buggy starter)."""


def pointer_get(doc, pointer):
    if pointer == "" or pointer == "/":
        return doc
    parts = pointer.lstrip("/").split("/")
    cur = doc
    for p in parts:
        key = p.replace("~0", "~").replace("~1", "/")
        if isinstance(cur, dict):
            cur = cur.get(key)
        elif isinstance(cur, list):
            if key == "-":
                cur = cur[-1]
            else:
                cur = cur[int(key)]
        else:
            cur = cur[key]
    return cur
