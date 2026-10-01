# Task k02: query string parser

Work in $PWD. `qs.py` has `parse(qs)` returning a list of (name, value)
pairs IN ORDER, keeping repeats and blank values: `a=&b=1&a=2` ->
`[('a',''),('b','1'),('a','2')]`; `+` decodes to space; `%2B` decodes to a
literal `+`; `%XX` percent-decoding incl UTF-8; a segment without `=` gets
value None; leading `?` stripped. shipped code drops blanks and mangles
`+`. Fix it, stdlib only (no urllib.parse). Verify yourself.
