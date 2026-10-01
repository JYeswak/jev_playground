# Task h06: glob-aware ranked touches

Work in $PWD. `touches.py` has `touched_ranks(value, hits)` returning sorted
unique 1-based ranks where `value` touches a hit. A hit touches when: exact
equality; `value` ends with `/hit`; `hit` is a substring of `value`; OR the
hit contains `*`/`?`/`[` and `fnmatch.fnmatchcase(value, hit)` or
`fnmatchcase(value, '*/' + hit)` is true. Empty value/hit touches nothing.
shipped code mishandles globs and ranks. Fix it, stdlib only. Verify.
