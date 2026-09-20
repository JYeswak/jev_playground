# omp-jev-foreman question measurement

**Unit:** P2-38
**Script:** `work/omp-jev-foreman/measure.mjs`
**Runs:** 3 Infisical-backed calls, identical script bytes and eight constructed windows each.

## Per-case table

Scores are run 1 / run 2 / run 3. HIT/MISS is against the construction label at threshold 0.50.

| Case | Truth | repeating | progress | stuck |
|---|---|---|---|---|
| same-failing-command | repeat=yes, progress=no, stuck=yes | .97/.97/.97 HIT | .12/.12/.12 HIT | .86/.86/.87 HIT |
| varied-edits | no/no | .10/.10/.10 HIT | .70/.71/.68 HIT | .11/.10/.11 HIT |
| twenty-reads-no-writes | repeat=no, progress=no, stuck=yes | .16/.16/.15 HIT | .53/.56/.53 MISS | .18/.20/.21 MISS |
| build-test-commit | no/progress=yes/stuck=no | .08/.08/.09 HIT | .77/.76/.77 HIT | .09/.08/.09 HIT |
| retry-then-move-on | repeat=no, progress=yes, stuck=no | .91/.91/.91 MISS | .42/.43/.42 MISS | .75/.74/.74 MISS |
| same-permission-failure | repeat=yes, progress=no, stuck=yes | .98/.98/.98 HIT | .06/.05/.06 HIT | .93/.92/.92 HIT |
| multi-file-refactor | no/progress=yes/stuck=no | .11/.11/.11 HIT | .74/.74/.72 HIT | .11/.10/.11 HIT |
| test-fix-commit | no/progress=yes/stuck=no | .28/.28/.28 HIT | .80/.80/.80 HIT | .08/.08/.08 HIT |

## Question totals and baselines

| Question | Hits / 8 | Always-no | Always-yes | Coin flip | Near threshold | Three-run range | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| repeating | 7/8 | 6/8 | 2/8 | 4/8 | 0 | .08–.98 | DISCRIMINATES, weak n |
| progress | 6/8 | 3/8 | 5/8 | 4/8 | 6 scores | .05–.80 | DISCRIMINATES, weak and boundary-sensitive |
| stuck | 6/8 | 5/8 | 3/8 | 4/8 | 0 | .08–.93 | DISCRIMINATES, weak n |

All three questions beat their own best constant baseline by one item. None is degenerate on this
constructed set, so no question was cut. `progress` has the clearest near-threshold instability:
the same byte-identical cases vary across .42–.56 around the decision boundary. The measurement
also exposes semantic traps: retry-then-move-on is healthy progress but the repeating/stuck scores
fire, and twenty reads/no writes is ambiguous enough that two labels miss.

## NO-CLAIM

These are eight hand-built windows authored for this measurement, one Jev model version, three
runs, and no production labels. The results do not establish supervision accuracy, calibration,
real-traffic precision, or a deployment threshold. The existing real-observation Foreman ruling
remains AUC 0.750 below the 0.90 bar.
