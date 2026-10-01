def _decode(s):
    buf = bytearray()
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "+":
            buf.append(0x20)
            i += 1
        elif c == "%" and i + 2 < n + 1:
            hx = s[i + 1 : i + 3]
            if (
                len(hx) == 2
                and hx[0] in "0123456789abcdefABCDEF"
                and hx[1] in "0123456789abcdefABCDEF"
            ):
                buf.append(int(hx, 16))
                i += 3
            else:
                buf.append(0x25)
                i += 1
        else:
            o = ord(c)
            if o < 128:
                buf.append(o)
            else:
                buf.extend(c.encode("utf-8"))
            i += 1
    return bytes(buf).decode("utf-8", errors="replace")


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
