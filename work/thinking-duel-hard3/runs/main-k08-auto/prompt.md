# Task k08: parameterized WHERE builder

Work in $PWD. `where.py` has `build(node)` where node is
`('and'|'or', [children])`, `('not', child)`, or `('col', op, value)` with
op in `=,!=,<,>,<=,>=,LIKE`. Return `(sql, params)` with `$1,$2,...`
placeholders in encounter order and raw values in params (NEVER interpolate
values into sql). shipped code interpolates and flattens nesting. Fix it.
Verify yourself, including an injection attempt staying inert in params.
