def redact(cmd, home, patterns):
    short = cmd.replace(home, "~").strip()[:200]
    for pat in patterns:
        short = pat.sub("[REDACTED]", short)
    return short
