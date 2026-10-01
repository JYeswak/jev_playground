# Task t12: bead row parser

Work in $PWD. `beads.py` has `parse_rows(text)` returning a list of
`{'id':..., 'title':..., 'status':...}` for lines shaped like
`- [x] jev-1234 | Some title here`. Status maps: `[x]` closed, `[ ]` open,
`[~]` in_progress, `[-]` deferred. Titles may contain `|` and brackets.
Malformed lines are skipped. It is wrong. Fix it, standard library only.
Verify yourself.
