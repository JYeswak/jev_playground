# Task k07: semver range intersection

Work in $PWD. `semver.py` has `intersect(a, b)` where each range is one of:
exact `1.2.3`, caret `^1.2.3` (>=1.2.3 <2.0.0; ^0.2.3 means <0.3.0;
^0.0.3 means <0.0.4), tilde `~1.2.3` (>=1.2.3 <1.3.0), `>=1.2.3`, `<2.0.0`,
or `*`. Return the tightest `(lo_inclusive, hi_exclusive)` version-tuple
pair covering the intersection, or None if empty. shipped code compares
strings and mishandles ^0.x. Fix it. Verify yourself.
