# Task u14: JSON pointer lookup

Work in $PWD. `jptr.py` has `pointer_get(doc, pointer)` implementing RFC
6901: `""` returns the whole document, otherwise `pointer` must start with
`/` and is split on `/`; each token unescapes `~1` to `/` THEN `~0` to `~`
(so `/~01` addresses the key `~1`, not `/`); a `~` followed by anything
other than `0`/`1` is a `ValueError`. Object lookup of a missing key
raises `KeyError`; array tokens must be `0` or digits without leading
zeros (`-`, out-of-range, and non-numeric tokens raise `IndexError`);
traversing into a scalar raises `TypeError`. It is wrong. Fix it, standard
library only. Verify yourself with escaped keys, the `~01` ordering trap,
`-` handling, and each error type above.
