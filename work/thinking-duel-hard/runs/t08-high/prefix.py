def redact(cmd, home, secret_re):
    scrubbed = secret_re.sub("[REDACTED]", cmd.replace(home, "~").strip())
    return scrubbed[:200]
