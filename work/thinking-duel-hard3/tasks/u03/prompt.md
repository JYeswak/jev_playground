# Task u03: CSV loader across encodings and line endings

Work in $PWD. `csvload.py` has `load_table(path)` returning a list of row dicts keyed by the header row. It is wrong. Fix it, standard library only. Verify yourself with a BOM file, lone-\r endings, quoted commas/quotes/newlines, and a latin-1 file.

Rules: decode bytes as utf-8-sig (strips a BOM) with fallback to cp1252 for non-UTF-8 bytes; parse with the `csv` module so quoted commas, `""` escapes, and newlines inside quoted fields all work; accept `\n`, `\r\n`, and lone-`\r` row separators; skip blank lines; return `[]` for an empty or header-only file.
