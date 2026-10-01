# Task k03: safe path join

Work in $PWD. `sjoin.py` has `safe_join(base, *parts)` returning the joined
absolute path, or raising `ValueError` on traversal outside base. Must
normalize (`.`, `..`, duplicate separators) BEFORE the prefix check, and the
prefix check must be directory-aware (`/tmp/x-evil` is NOT inside `/tmp/x`).
Absolute `parts` elements are treated as relative (strip leading `/`).
Symlinks out of scope. shipped code is bypassable twice over. Fix it,
stdlib only. Verify with traversal and prefix-confusion cases.
