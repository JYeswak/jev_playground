# Task t03: session tool-call census

Work in $PWD. `census.py` has `count_calls(path)` returning a dict
{tool_name: count} over assistant `toolCall` items in a JSONL session file.
It must skip malformed JSON lines and non-dict rows silently, and count only
items with type exactly `toolCall` and a string `name`. It is wrong. Fix it,
standard library only. A sample file `sample.jsonl` is included. Verify yourself.
