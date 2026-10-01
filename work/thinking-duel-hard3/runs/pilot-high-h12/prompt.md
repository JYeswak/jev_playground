# Task h12: bead parser with word statuses

Work in $PWD. `beads.py` has `parse_rows(text)` for lines shaped like
`- [x] jev-1234 | Title` OR `- closed jev-1234: Title` (status word then id
then `:`). Marks: `[x]` closed, `[ ]` open, `[~]` in_progress, `[-]`
deferred; words: closed/open/in_progress/deferred (also `in-progress`).
Titles may contain `|`, `:`, brackets. Malformed lines skipped. shipped code
handles only the first shape and two marks. Fix it, stdlib only. Verify.
