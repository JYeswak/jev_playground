# 19-of-21 export re-sweep — 2026-09-20 `[pending]`

Mechanical re-sweep over all 21 package dirs (`work/omp-jev-*` +
`work/omp-harm-rule`). Rule frozen before running: export=YES iff
`src/` matches `appendEntry|writeFileSync|appendFileSync|recording|
register` AND matches a model-call token (`askJev|systemOne|
askJevChoice|jevClient|client` import); NOT-APPLICABLE iff no model
call. Command: per-dir `grep -rl` both patterns (see audit logit, run
2026-09-20).

## Result: 19/21 HOLDS, nothing moved

- 19 dirs: model≥1 hit AND persist≥1 hit (incl. observer inline,
  failure/foreman injectable-defaults — counted by pattern, not re-judged).
- 2 NOT-APPLICABLE, same as published: `preaction` (model=0 — regexes,
  persist hits are non-Jev writes), `harm-rule` (model=0, persist=0).
- Denominator 21 re-derives (`ls -d … | wc -l`, guard-agree).

## What this does and does not show

- The family is as stable as feared: identical value under an independent
  mechanical rule. That is evidence for stability, not for correctness —
  the 3 judgment calls (observer inline; failure/foreman wired-at-default)
  were NOT re-audited, and per-package identity was NOT diffed against
  the original census (a rename/add could hold 19/21 while changing its
  members — the count-shape of denominator drift).
- Next audit should diff member NAMES, not just the share. Stated here so
  the next run does it.

## NO-CLAIM

Grep-shape census, not the §15 judgment sweep. One window, one machine.
Not a promotion.
