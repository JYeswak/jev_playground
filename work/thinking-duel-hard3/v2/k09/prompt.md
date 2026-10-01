# Task k09: unified diff applier

Work in $PWD. `patcher.py` has `apply_patch(original, diff)` applying a
subset of unified diff: `---/+++` headers (ignored), `@@ -a,b +c,d @@`
hunks, ` ` context, `-` removals, `+` additions. Hunk positions refer to the
ORIGINAL (not shifted) file; multiple hunks apply top-down with an offset
accumulator. Mismatched context raises ValueError. shipped code ignores
offsets and never validates. Fix it, stdlib only. Verify yourself.
