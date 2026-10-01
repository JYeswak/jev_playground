# Task k15: mini template renderer

Work in $PWD. `tmpl.py` has `render(template, ctx)` with `{{name}}`
substitution, `{% if name %}...{% endif %}` conditionals (truthiness of
ctx value, nestable), and `{{name|escape}}` HTML-escaping (`&<>"'`). Unknown
names render as empty string; `{% if %}` on missing/empty is false. shipped
code regex-replaces without nesting or escaping. Fix it, stdlib only
(`html.escape` allowed). Verify nested + escaping yourself.
