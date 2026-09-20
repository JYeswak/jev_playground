# Hardening census re-run — 2026-09-20 `[pending]`

Re-derived after R46 (staged-exposure refused) and R47 (callback-sha
refused), plus the Unit 1 audit (7/7 guard runs agree, zero new drifts).

## Movement

- Rank 1 staged-exposure: **4 → 4, unchanged.** No fifth instance in the
  ledger (1228→1282 lines checked; newest tail cites the census itself).
  Refused, stays prose (R46).
- Rank 2 unpinned live inputs: 5 → 5 instances, but denominator half now
  audited (7 agrees); input-sha half still prose. Partially narrowed,
  rank unchanged.
- Rank 3 callback-sha: 4 → 4, unchanged. Refused, stays prose (R47). All
  9 of tonight's P2 sends carried shas (or were non-packet status sends).
- Selector class +1 (conductor's piped-rc 27th) — a *different shape*
  (exit-status laundering, not silent-zero); vgrep does not cover it.
  Noted, not counted against the wired class.

## Result

**Ranking unchanged; top prose-only count steady at 4. The hardening pass
has converged**: the two mechanizable classes are wired, the top
remainder is refused twice with triggers, and the re-run found nothing
new. Further guards would chase shapes, not recurrences.

## NO-CLAIM

Ledger-grep re-derivation, not an independent audit. Convergence is "no
new instances tonight," not "classes eradicated" — R46/R47 triggers are
the live ends.
