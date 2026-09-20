---
condition: '\bgrep\b[^;&]*\|[^;&]*grep\s+-v[^;&]*fn\s'
scope: tool:bash
interruptMode: never
repeatMode: once
---
You are excluding the **definition** from the results — this is a **call-site / references search**, and `grep -v 'fn …'` is the shallow way to ask it: it misses renames, re-exports, and trait impls. Use **`ast-grep -p '$N ($$$)'`** for call sites, **`ripwire <dir> --for="<task>"`** for callers/callees ranked, or **morph `codebase_search`** for who-calls-this across the tree. Ignore this when scanning a diff (`grep '^[+-]'`) or a single file you already know. Mined 2026-09-20: 64/78,242 fleet commands (0.08%), hand-labelled FP 0.30 (seed 20260920, n=20; misses are diff-line scans). Never interrupts; fires once per session. Retire when a 30-day harvest shows the class below 50 occurrences. Portable: no repo-local paths.
KIND: defect-guidance. Bar applied: rate (0.08%) + labelled precision (FP 0.30, seed 20260920). Judged as a defect claim, not topic routing.
