import base64

_ALPHABET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
)


def decode_chunks(chunks):
    s = "".join(chunks)
    cleaned = "".join(s.split())
    if not cleaned:
        return b""
    for ch in cleaned:
        if ch != "=" and ch not in _ALPHABET:
            raise ValueError(f"invalid base64 character: {ch!r}")
    if len(cleaned) % 4 != 0:
        raise ValueError("missing terminal padding: length not multiple of 4")
    stripped = cleaned.rstrip("=")
    n_pad = len(cleaned) - len(stripped)
    if n_pad > 2:
        raise ValueError("invalid padding: too many '='")
    if "=" in stripped:
        raise ValueError("invalid padding: '=' not at end")
    try:
        return base64.b64decode(cleaned, validate=True)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(str(exc)) from exc
