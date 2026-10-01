import base64


_ALPHABET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
)


def decode_chunks(chunks):
    s = "".join(chunks)
    # Ignore whitespace; reject any other non-alphabet char.
    t = "".join(c for c in s if not c.isspace())
    for c in t:
        if c not in _ALPHABET:
            raise ValueError(f"invalid base64 character: {c!r}")
    if not t:
        return b""
    if len(t) % 4 != 0:
        raise ValueError("invalid base64 length: missing terminal padding")
    # Padding '=' only valid as the final 1-2 chars.
    if t.endswith("=="):
        if "=" in t[:-2]:
            raise ValueError("misplaced padding '='")
    elif t.endswith("="):
        if "=" in t[:-1]:
            raise ValueError("misplaced padding '='")
    elif "=" in t:
        raise ValueError("misplaced padding '='")
    return base64.b64decode(t, validate=True)
