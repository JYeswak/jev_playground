# Task u15: minimal list edit script with moves

Work in $PWD. `ldiff.py` has `diff_lists(old, new)` returning a list of
ops, plus a correct `apply_script(seq, ops)` that applies them in order
against the CURRENT list state: `("del", i)` removes index `i`;
`("ins", i, v)` inserts `v` before index `i` (`i` may equal the length);
`("move", i, j)` removes the element at `i` then inserts it before index
`j` of the shortened list. `diff_lists` must return a script that applies
to exactly `new`, is minimal-length (a pure rotation needs ONE `move`,
identical lists need ZERO ops), and handles duplicates. The shipped
`diff_lists` just deletes everything and reinserts (correct but bloated:
no moves, never minimal). Fix it, standard library only. Verify yourself
with rotations, swaps, duplicate shuffles, and an independent applier.
