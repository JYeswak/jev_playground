# Task h09: delimited export with NULLs

Work in $PWD. `delim.py` has `write_delim(path, rows, delim='|', none_as='')`
(rows = list of lists of str|None) and `read_delim` inverting it. Encoding
rules: None -> none_as, or `'""'` when none_as is empty; empty string ->
bare empty field always; fields containing delim, quotes, or newlines, or
equal to a nonempty none_as, are `"`-quoted with inner quotes doubled.
`read_delim` inverts exactly (quoted-empty decodes per the same rule, so
round-trips preserve None vs ''). shipped code is wrong. Fix both
directions, stdlib only. Verify round-trips yourself.
