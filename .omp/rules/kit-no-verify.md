---
description: "Kit B5 / forbidden pattern 1: never bypass the pre-commit honesty gate"
condition:
  - 'git\s+commit\b[^\n]*(--no-verify|\s-[a-zA-Z]*n[a-zA-Z]*\b)'
  - 'git\s+push\b[^\n]*--no-verify'
  - 'core\.hooksPath'
scope: "tool:bash"
interruptMode: always
---
STOP. You were about to bypass or re-point the pre-commit honesty gate (CHECKLIST.md B5; AGENTS.md forbidden pattern 1, "gate self-weakening").

If the hook is failing, the failure is the signal. Read its stderr, fix the cause, and commit normally. If you believe the gate itself is wrong, do NOT change it: file a bead describing the false rejection with the exact command and output (B7 requires two-direction evidence for any gate change), then continue with other ready work.
