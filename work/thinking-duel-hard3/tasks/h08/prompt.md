# Task h08: multi-pattern redact with marker integrity

Work in $PWD. `prefix.py` has `redact(cmd, home, patterns)` returning at
most 200 chars with `home` -> `~` and every match of each compiled pattern
in `patterns` replaced by `[REDACTED]`. Requirements: scrub ALL patterns
before cutting; never cut inside a `[REDACTED]` marker (if the 200-char cut
would split one, end the string before it); secrets straddling char 200 must
be fully removed. shipped code is wrong. Fix it, stdlib only. Verify,
including straddling and adjacent secrets.
