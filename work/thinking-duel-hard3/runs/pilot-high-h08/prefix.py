def redact(cmd, home, patterns):
    s = cmd.replace(home, "~").strip()
    for pat in patterns:
        s = pat.sub("[REDACTED]", s)
    if len(s) <= 200:
        return s
    mark = "[REDACTED]"
    cut = 200
    for i in range(max(0, cut - len(mark) + 1), cut):
        if s.startswith(mark, i):
            cut = i
            break
    return s[:cut]
