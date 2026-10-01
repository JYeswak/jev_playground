# Task h13: JSON merge patch

Work in $PWD. `mpatch.py` has `merge_patch(target, patch)` implementing RFC
7396: non-dict patch replaces target; dict patch merges per key with null
values REMOVING the key; arrays replace wholesale (no merge); neither input
is mutated. shipped code is wrong (mutates, mishandles null/arrays).
Fix it, stdlib only (copy inputs first). Verify yourself.
