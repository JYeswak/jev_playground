# Bar census (2026-09-24)

Numbers only. No ruling.

37 receipts in `docs/demos/upstream-repro/` state a bar sha. Re-score:
`python3 work/sr-adopt/audit_bars.py`

`work/sr-adopt/prereg-pairs.tsv` has 70 pairs. `audit_bars.py` exits 0.
The seven hand-checked pairs are still in that file.

`work/sr-adopt/prereg-excluded.tsv` has 43 rows not paired, plus 2 sha notes.

| class | n |
|---|---:|
| pairs audited, bar first-add precedes rows | 70 |
| reversed (rows first-add precedes the stated bar) | 8 |
| input or not an output rows file | 35 |
| stated sha does not resolve | 0 |
| stated sha first-adds no file | 1 |
| stated sha first-adds only rows files | 1 |

The sha that first-adds no file is `c22673b` in
`oracle-kit-select-report-20260923.md`.

The sha that first-adds only rows files is `4447b25` in
`injection-variance-20260924.md`. The bar used for that receipt's pairs is
`142fd5d`, which first-adds the receipt. Bar and rows are not the same commit.
