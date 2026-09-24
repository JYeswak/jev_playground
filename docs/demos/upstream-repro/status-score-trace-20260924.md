# Score-trace correction (bead `jev-5937`)

The score column is a demand score. `ba05c3e` marked six rows `UNVERIFIED` because
those demand scores were not in the cited receipts. That erased verdicts the
receipts do source. This file is the correction.

Each prior score had no source. The verdicts did. Scores are now `0`, the file's
existing unscored value. Verdicts are restored to `ba05c3e^`.

| candidate | prior score | restored verdict | verdict source |
|---|---:|---|---|
| UP-R1-tier-routing-for-cost | 905 | RULED_OUT | `router-savings-inverts-20260919.md:18` Jev +90.2% more expensive than flat |
| UP-R2-commit-security-triage | 885 | CLEARED | `router-savings-inverts-20260919.md:68` adopt commit-triage |
| UP-R3-worker-supervision | 870 | CLEARED | `router-savings-inverts-20260919.md:68` adopt supervision |
| UP-R4-jev-judged-compaction | 930 | RULED_OUT | `compaction-retention-oracle-20260919.md:57` `keep_p` 0.361 |
| UP-R5-jev-toolcall-gate | 940 | HELD | `bicameral-gate-adoption-20260919.md:55` the ADOPT does not survive the held-out run |
| UP-R7-foreman-supervision | 610 | RULED_OUT | `foreman-supervision-adoption-20260919.md:70` REAL AUC=0.750 |

The trace table at `status-score-trace-20260924.tsv` still records those six
scores as `NOT_FOUND`. That class is about the demand score, not the verdict.
