def parse(qs):
    out = []
    for seg in qs.split("&"):
        if "=" in seg:
            k, v = seg.split("=", 1)
            out.append((k.replace("+", " "), v.replace("+", " ")))
        elif seg:
            out.append((seg, None))
    return out
