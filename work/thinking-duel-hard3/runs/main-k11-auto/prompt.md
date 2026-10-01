# Task k11: markdown table parser

Work in $PWD. `mdtable.py` has `parse(text)` returning a list of dicts from
the FIRST markdown table in text: header row, delimiter row (`---`, `:--`,
`--:`, `:-:`), data rows; cells split on unescaped `|` (escaped `\|` stays
literal); rows with fewer cells pad with None, extra cells truncate;
leading/trailing pipes tolerated; returns [] if no table. shipped code
splits naively and misaligns. Fix it, stdlib only. Verify yourself.
