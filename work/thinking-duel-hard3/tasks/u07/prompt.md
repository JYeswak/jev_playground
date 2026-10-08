# Task u07: order-preserving URL query merge

Work in $PWD. `urlmerge.py` has `merge_url(base, extra)` merging extra params into a URL query string. It is wrong. Fix it, standard library only. Verify yourself with repeated keys, blank values, fragments, and reserved characters.

Rules: `extra` maps `str` to a `str` or a list of `str` (expanded in order); existing params keep their order with extras appended; repeated keys accumulate instead of replacing; blank values (`a=`) survive; the `#fragment` stays at the end; keys/values are percent-encoded; an empty `extra` leaves the URL unchanged.
