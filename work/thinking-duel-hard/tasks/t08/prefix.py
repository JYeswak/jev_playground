def redact(cmd, home, secret_re):
    short = cmd.replace(home, "~").strip()[:200]
    return secret_re.sub("[REDACTED]", short)
