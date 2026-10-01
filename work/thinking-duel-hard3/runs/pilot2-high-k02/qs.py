def _decode(s):
    b = bytearray()
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "+":
            b += b" "
            i += 1
        elif (
            c == "%"
            and i + 2 <= n
            and len(s[i + 1 : i + 3]) == 2
            and all(ch in "0123456789ABCDEFabcdef" for ch in s[i + 1 : i + 3])
        ):
            b.append(int(s[i + 1 : i + 3], 16))
            i += 3
        else:
            b += c.encode("utf-8")
            i += 1
    return b.decode("utf-8", errors="strict")


def parse(qs):
    if qs.startswith("?"):
        qs = qs[1:]
    out = []
    for seg in qs.split("&"):
        if not seg:
            continue
        if "=" in seg:
            k, v = seg.split("=", 1)
            out.append((_decode(k), _decode(v)))
        else:
            out.append((_decode(seg), None))
    return out
