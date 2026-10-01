# Task t09: CSV export quoting

Work in $PWD. `csvexp.py` has `write_csv(path, rows)` (rows = list of lists
of str) and `cli.py` reads a JSON array-of-arrays from stdin and writes CSV
to stdout. Fields containing commas, quotes, or newlines must round-trip
through any RFC-4180 reader. Quoting is currently broken. Fix the exporter
(standard library only), keep the `cli.py` interface. Verify with a
round-trip yourself.
