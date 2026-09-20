# sr end-to-end: scale-invariance finding + closeout (2026-09-20)

## The headline finding (measured, mechanism inferred)

Same task, same skill (`focused-fix`, fits 0.88 in both), different cohort:

| cohort | verdict |
|---|---|
| 1 skill | ranked #1 |
| 6 skills | ranked #1 |
| 57 eligible skills | ABSTAIN (`no-shortlist-match`) |

`fits` is ABSOLUTE (0.88 regardless of cohort), so the flip lives in the
wide→shortlist step: with 57 candidates the mass splits and nothing clears
the bar. Plausible mechanism: Choice probabilities dilute across N options
while the shortlist bar is absolute — but that is INFERENCE from
input/output, not source proof. The Quill prefilter (>254) exists for large
libraries; 57 falls in the unprotected middle.

Practical consequence for us: rank against CURATED subsets (works,
proven USEFUL with discrimination), not the whole 500-library (abstains).

## Also closed this session

- User-config roots DO work with collection-dir shape (my "broken" verdict
  was my shape error — corrected, receipt `skillranker-user-roots`).
- Whole-`~/.claude/skills` dir fails: entry-limit hit + mixed content;
  bounded, superseded by the scale finding above.
- Earlier bisection (47/24/23/6) RETRACTED: fixture loop copied loose files,
  not skills — those runs tested near-empty collections. Redone rigorously
  with python-verified copies; only the 1/6/57/500 points above stand.
- Machine clean: no user config, test collections deleted, ledger missing,
  installed `sr` untouched (pure `0e61cc6`).

## Cost

~14 paid Jev ranks this session (all small: ~2-8k in / ~300-1k out). The
last 4 probes ran on cache (0 calls).

## Ledger line

SCALE sr-ranking — MEASURED flip at 57 (abstain) vs rank at ≤6, fits
absolute — mechanism inferred, not proven — unfilable per native-binary
rule — NO-CLAIM: use curated subsets; whole-library path open.
