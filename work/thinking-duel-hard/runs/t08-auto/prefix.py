def redact(cmd, home, secret_re):
    s = secret_re.sub("[REDACTED]", cmd.replace(home, "~"))
    return s.strip()[:200]
