# Task t08: redacted command prefix

Work in $PWD. `prefix.py` has `redact(cmd, home, secret_re)` returning at
most the first 200 chars of the command with `home` replaced by `~` and
every `secret_re` match replaced by `[REDACTED]`. Critical: scrub BEFORE
cutting, so a secret straddling char 200 is still fully removed. It is
wrong. Fix it, standard library only (`secret_re` is a compiled pattern).
Verify yourself, including a straddling secret.
