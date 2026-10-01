---
description: "Judged by Jev: a reply that claims a result must show the evidence for it (bead jev-e2vb)"
condition: '(?i)\b(done|fixed|verified|passing|passes|passed|complete[d]?|works|working|landed|shipped|green|succeeded)\b'
question: "Does this reply claim that work is done, fixed, verified, passing, or working without quoting the command, its output, a file line, or a commit that proves it?"
scope: "text"
---
**Evidence missing (judged by Jev).** Your reply claims a result without showing what proves it.
Quote the command and the output lines that prove it, or the commit SHA or `file:line`. If you did
not run it, say UNVERIFIED and name the command that would verify it.
