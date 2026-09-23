# W7.4 preregistered bars (TopazRaven, committed [pending] before any live call)

## jev-deep-kit-8q7.6 — applicability pre-gate (omp-jev-review)

Bar: diffs with <10 code lines changed OR no code hunks return
`applicable:false`; a >100-line suite diff still scores. Metric: gate
decision on our 669-commit draw. Fails if any thin diff scores or any
substantial diff refuses.

## jev-deep-kit-8q7.7 — select/report helper (oracle-kit)

Bar: on the held-out phishing half, select-on-A/report-on-B beats the
single verdict by >=5 AUROC points (single baseline 0.689 per receipt).
Fails if the gain is smaller or the planted single-signal input shows
any gain.

## jev-deep-kit-8q7.8 — structured criteria variant (question-writing)

Bar: {what,includes}+focus variant matches-or-beats the current shape on
the held-out lingspam split by logreg OOF AUROC (no regression vs
current). Fails on any regression or on gain in the focus-free negative.
