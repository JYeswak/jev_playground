# Exposure-ranked census of our own defect classes — 2026-09-20 (P2)

No rules shipped or proposed here. Ranked by exposure (occurrences with
denominator), not by how interesting the doctrine is. Every number states
its denominator. Dialect: Python `re` (matches `exposure-check.sh`'s
heredoc; rerun there to confirm).

## Ranked

| # | class | hits | N (denominator) | sessions | top-1 | detectable in payload | verdict |
|---|---|---:|---|---|---|---|---|
| 1 | backtick-in-quotes | 1,417 | 78,242 bash cmds | N/A (harvest has no session attribution) | — | bash yes | REFUSE: ```-fence dominated |
| 2 | grep-glob-silenced | 820 | 78,242 | N/A | — | bash yes | SHIPPED |
| 3 | pipe-exit (`\| head/tail` + `$?`) | 807 | 78,242 | N/A | — | bash yes | SHIPPED |
| 4 | destructive list | 258 | 78,242 | N/A | — | bash yes | REFUSE: dcg enforces |
| 5 | timeout-led commands | 247 | 78,242 | N/A | — | bash yes | REFUSE: form correct (R55-analog) |
| 6 | empty-as-finding (B0) | 218 | 45,220 turns | 63 files | 11% | text yes | REFUSE FP 1.00 (R57) |
| 7 | workaround-talk (A1) | 147 | 45,220 | 52 | 10% | text yes | discussion, not defect (R56 covers conjunction) |
| 8 | foreign-pm | 110 | 78,242 | N/A | — | bash yes | REFUSE FP 1.00 (R62) |
| 9 | pipe-status-in-edit (SH2) | 95 | 416 .sh edits; 30/1,817 sess (1.65%) | 30 sess | 21% | edit yes | REFUSE FP 1.00 (R65) |
| 10 | workaround+upstream (A2) | 89 | 45,220 | 40 | 10% | text yes | REFUSE FP 0.95 (R56) |
| 11 | number-no-provenance (MD1) | 37 | 3,588 .md edits; 9 sess | 9 sess | 49% | text yes | REFUSE FP 1.00 + floor (R65) |
| 12 | empty+timeout conj (B1) | 27 | 45,220 | 16 | 15% | text yes | REFUSE floor + FP (R58) |
| 13 | backtick-in-record-body | 12 | 78,242 | N/A | — | bash yes | REFUSE floor; residuals deliberate (R59) |
| 14 | branch-create / vercel / bun-test / secrets-true | 0–4 | 78,242 | — | — | bash yes | REFUSE absent |
| 15 | number-without-denominator (handed: 5 today) | 5 anecdotal + MD1 row | today's sessions + row 11 | — | — | text NO / tool YES | REDIRECT: `scripts/denominator-sweep.sh` already exists |
| 16 | R47/R48 refused guards | 4 instances each | case files | — | — | case-specific | exposure-only rows, already refused |
| 17 | NEGATIVE_EVIDENCE meta | 70 refutations | the ledger | — | — | no | process corpus, not a rule source |

## Detectable count

Of the top 5 by exposure, 5/5 are detectable in a tool-call payload —
and 2 shipped, 3 refused (fence-dominated, dcg-redundant, form-correct).
Detectability was never the constraint; **exposure to a shippable shape**
was. The handed class (row 15) is the inverse: highest direct evidence,
undetectable as a single-string predicate, already containered as a tool.

## For P3's exposure-check.sh

Machine table: `work/exposure-census-20260920.tsv` (label, pattern,
not_pattern, path_pattern, hits, N, sessions_touched, top1_share,
detectable_in_payload, verdict, evidence). Patterns are mine, recorded
for rerun, not asserted as the tool's final form.
