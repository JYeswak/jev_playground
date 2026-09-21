# structural-def n=77 — 2026-09-21 `[receipt]`

**Lane:** offline labels on real transcripts. **Oracle:** Wilson two-sided
95% (stdlib hand-roll; no scipy here — the bar is the Wilson upper, same as
P4). **Decision bar (preregistered):** Wilson 95% upper ≤ 0.30 → CERTIFIED,
else RETIRED.

Sampling frame and seed were written **before** the draw:
`structural-n77-preregister-20260920.md`. Seed `2026092105`, mulberry32, 77
without replacement from 185 fires over 1,877 session jsonl files (condition
read from the rule file, Python `re`). Replacement sample (original n=20
identities were not persisted).

## Blinding

Frame = fires, so every row already fired. Labels are gold class: TP =
genuine structural-shape search (seeks unknown structure via code keyword
AND regex hole); FP = known-name lookup, navigation, census, or incidental
match. Labeller saw command + match span.

## Result

| | |
|---|---|
| n | 77 |
| TP | 22 |
| FP | 55 |
| p̂ | 0.7143 |
| Wilson 95% | **[0.605, 0.803]** |

**Upper 0.803 > 0.30. RETIRED.** The lower bound alone (0.605) clears the
bar — this is not close, and no borderline relabelling moves it: flipping
all six borderline FPs still leaves 49/77 (upper ≈ 0.74).

The shipped FP 0.20 (n=20) was underpowered optimism, same direction as
absence (0.20 → 0.27) but far larger. Dominant FP class: known-name
alternations (`fn reap\|reap_finished`), exactly the miss class the rule
text itself names.

## Action

Disable `bash-structural-def-search` via `ttsr.disabledRules` the same day.
Rule file stays on disk (no deletion). Verify by ENUMERATION
(`omp ttsr list`, rule absent in both scopes), never by probe silence —
repeatMode-once makes silence ambiguous.

## NO-CLAIM

Not a claim the original 4/20 was fraud — it was n=20. Not a new
predicate. Frame is Python-`re` matches, not live JS-RegExp fires; the two
agree on this condition's feature set, stated as a caveat.
