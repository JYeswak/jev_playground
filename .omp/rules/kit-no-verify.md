---
description: "Kit B5 / forbidden pattern 1: never bypass the pre-commit honesty gate"
condition:
  - '\bgit\s+(?:-[cC]\s+[^\s"\\;&|]+\s+)*commit\b(?:\s+(?:[^\s"''\\;&|]|\\?["''][^"''\\]*\\?["''])+)*?\s+(?:--no-verify|-[a-zA-Z]*n[a-zA-Z]*)(?=[\s;&|"]|\\n)'
  - '\bgit\s+(?:-[cC]\s+[^\s"\\;&|]+\s+)*push\b(?:\s+(?:[^\s"''\\;&|]|\\?["''][^"''\\]*\\?["''])+)*?\s+--no-verify(?=[\s;&|"]|\\n)'
  - '\bgit\s+config\b(?:(?!--get|--list|-l\b)[^;&|"\\])*?\score\.hooksPath\s+(?![0-9]*[<>])(?:[^\s;&|"\\<>]|\\["''])+(?=[\s;&|"]|\\n)'
  - '\bgit\s+config\b[^;&|"\\]*?\s--unset(?:-all)?\s+core\.hooksPath\b'
  - '\bgit\b[^;&|"\\]*?\s-c\s*core\.hooksPath='
scope: "tool:bash"
interruptMode: always
---
**Blocked before it ran.** Your last `bash` call bypasses or re-points the pre-commit hook. That command did not execute. Do not re-issue it unchanged.

STOP. You were about to bypass or re-point the pre-commit honesty gate (CHECKLIST.md B5; AGENTS.md forbidden pattern 1, "gate self-weakening").

If the hook is failing, the failure is the signal. Read its stderr, fix the cause, and commit normally. If you believe the gate itself is wrong, do NOT change it: file a bead describing the false rejection with the exact command and output (B7 requires two-direction evidence for any gate change), then continue with other ready work.
