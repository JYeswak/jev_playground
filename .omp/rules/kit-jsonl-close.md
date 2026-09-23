---
description: "Kit B2: direct JSONL closes must carry a substantive close_reason"
condition:
  - '"status"\s*:\s*"closed"(?![^\n]*"close_reason"\s*:\s*"[^"]{20,}")'
scope: "tool:edit(**/.beads/issues.jsonl), tool:write(**/.beads/issues.jsonl)"
interruptMode: always
---
You are marking a bead closed in .beads/issues.jsonl without a substantive close_reason (at least a command + result or a commit SHA). Add "close_reason":"<command> -> <result>; commit <sha>" and "closed_at":"<UTC>" on the same line, or leave the bead open.
