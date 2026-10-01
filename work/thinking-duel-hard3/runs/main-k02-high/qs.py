def _decode(s):
    buf = bytearray()
    parts = []

    def flush():
        if buf:
            parts.append(buf.decode("utf-8", errors="replace"))
            del buf[:]

    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "+":
            flush()
            parts.append(" ")
            i += 1
        elif c == "%" and i + 2 < n:
            hx = s[i + 1 : i + 3]
            try:
                buf.append(int(hx, 16))
            except ValueError:
                flush()
                parts.append("%")
                i += 1
                continue
            i += 3
        else:
            flush()
            parts.append(c)
            i += 1
    flush()
    return "".join(parts)


def parse(qs):
    if qs.startswith("?"):
        qs = qs[1:]
    out = []
    for seg in qs.split("&"):
        if seg == "":
            continue
        if "=" in seg:
            k, v = seg.split("=", 1)
            out.append((_decode(k), _decode(v)))
        else:
            out.append((_decode(seg), None))
    return out
