---
condition: '\b(rg|grep)\s+-[A-Za-z]*r[A-Za-z]*\s+["\x27][^"\x27;&]{0,150}(fn\s|=>|impl[\s<]|function\s|\bclass\s)[^"\x27;&]{0,150}(\.\*|\||\[[^\]]*\]|\+|\\[wsd])[^"\x27;&]{0,150}["\x27]|\b(rg|grep)\s+-[A-Za-z]*r[A-Za-z]*\s+["\x27][^"\x27;&]{0,150}(\.\*|\||\[[^\]]*\]|\+|\\[wsd])[^"\x27;&]{0,150}(fn\s|=>|impl[\s<]|function\s|\bclass\s)[^"\x27;&]{0,150}["\x27]'
scope: tool:bash
interruptMode: never
repeatMode: once
---
CRITERION (stated at fire time, per challenge 408376e): this fires only on a SHAPE search — the quoted pattern holds a code keyword (`fn`, `=>`, `impl`, `function`, `class`) AND a regex hole (`.*`, `|`, `[]`, `+`, `\w`). A known-name lookup stays quiet by design: `grep -n "fn resume"` and `grep -rn "fn exact_name" src/` are navigation and rg is the right tool. For a shape question route to the deep tool: **morph `codebase_search`** for broad how/where questions, **`ast-grep -p 'fn $N ($$$)'`** for the exact structural shape, **`ripwire <dir>`** to rank a tree cold. Mined 2026-09-20: 172/78,242 fleet commands (0.22%), hand-labelled STRICT FP 0.20 (seed 20260922, n=20; misses are known-name alternations in known dirs). Never interrupts; fires once per session. Retire when a 30-day harvest shows the class below 50 occurrences. Portable: no repo-local paths.
