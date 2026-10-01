# Task t06: ranked path touches

Work in $PWD. `touches.py` has `touched_ranks(value, hits)` returning the
sorted unique 1-based ranks where `value` touches a hit: exact equality, or
`value` ends with `/hit`, or `hit` is a substring of `value`. Empty hits or
empty value touch nothing. It is subtly wrong. Fix it, standard library
only. Verify yourself.
