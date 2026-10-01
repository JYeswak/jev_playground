import base64


def decode_chunks(chunks):
    s = "".join(chunks)
    t = "".join(s.split())
    if not t:
        return b""
    valid = frozenset(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    )
    for ch in t:
        if ch not in valid:
            raise ValueError(f"invalid character: {ch!r}")
    if len(t) % 4 != 0:
        raise ValueError("missing terminal padding: length not multiple of 4")
    pad = len(t) - len(t.rstrip("="))
    if pad > 2:
        raise ValueError("too much padding")
    if pad and "=" in t[: len(t) - pad]:
        raise ValueError("'=' only valid at the very end")
    return base64.b64decode(t, validate=True)
