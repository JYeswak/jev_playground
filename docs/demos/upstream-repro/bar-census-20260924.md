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
| reused prior-run cell, audited under its originating receipt | 4 |
| reused prior-run cell, no audited bar | 4 |
| input or not an output rows file | 35 |
| stated sha does not resolve | 0 |
| stated sha first-adds no file | 1 |
| stated sha first-adds only rows files | 1 |

The 8 cells whose rows first-add precedes the later receipt are not
preregistration failures. Each is an earlier run reused as a baseline.

Audited under the originating receipt (4):
`work/noul-fever/rows-jev.jsonl` under `noul-fever-20260924.md` bar `834a569`.
The reusing receipt names that path at line 24.
`work/choice-banking77/rows-jev.jsonl` under `choice-banking77-20260924.md`
bar `a0ed3c1`. `work/noul-scifact/rows-jev.jsonl` and `rows-haiku.jsonl` under
`noul-scifact-20260924.md` bar `15b0371`. `second-incumbent-20260924.md` names
none of those three paths.

No audited bar (4). No receipt states the adding commit as a bar:
`work/nev-differential/rows-A-xai-grok-4.jsonl` and `rows-B-anthropic-claude-haiku-4-5.jsonl`,
first-add `57d30e9`. The reusing receipt names both paths (lines 26 and 23).
`work/jev-injection-flag/rows-jev-withheld.jsonl`, first-add `888efbe`. The
reusing receipt names the path and says reused (lines 29-30).
`work/choice-banking77/rows-haiku.jsonl`, first-add `3709ee6`. The reusing
receipt does not name that path.

The sha that first-adds no file is `c22673b` in
`oracle-kit-select-report-20260923.md`.

The sha that first-adds only rows files is `4447b25` in
`injection-variance-20260924.md`. The bar used for that receipt's pairs is
`142fd5d`, which first-adds the receipt. Bar and rows are not the same commit.
