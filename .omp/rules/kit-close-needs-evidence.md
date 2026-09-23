---
description: "Kit B2 / forbidden pattern 7: close beads only with cited evidence"
condition:
  - '\b(?:br|bd)\s+close\b(?:(?!--reason\b|-r\b)[^;&|"\\])*(?:["'';&|]|\\n)'
scope: "tool:bash"
interruptMode: always
---
You are closing a bead without a reason. CHECKLIST.md B2: a bead closes only with a close_reason citing evidence: a commit SHA, the exact command you ran plus its pass output, or a ledger row. "Done", "implemented", or "fixed" is not evidence (forbidden pattern 7, close-pump abuse).

Re-run the bead's acceptance command now, then close with: br close <id> --reason "<command> -> <result>; commit <sha>".
