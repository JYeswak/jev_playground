# REPORT — longres independent replication (jev-4se3, OrangeFrog)

Population: 200 long results (>=10k chars), seed 20261007, disjoint files
(0 overlap with hers), dev 100 (ref 18) / held 100 (ref 22). Ref rate lower
than hers (0.20 vs 0.42) — different population, disclosed.

Live: 200 calls jev-1.13.0, 199 scored + 1 no-answers->KEEP, 0 exclusions,
144,368 input tok ~$0.0061 (cap $0.015). Choices: keep 120 / summarize 49 /
drop 31. Baseline T refit on MY dev: T=10938 (J=0.075).

Held results:
- Jev miss 5/22 = 0.227, 95% CI [0.101, 0.434]; savings 21.6 row-units.
- Fitted baseline miss 21/22 = 0.955; savings 69.0.
- Bar: miss 0.227 <= 0.955 MET; savings 21.6 >= 1.2x69.0=82.8 NOT MET.
- Matched-miss baseline (T=39297, miss 5/22): savings 13.0; Jev 1.66x.

Verdict: REPLICATE-FAIL on the bar letter, SAME DIRECTION as original
(hers: safer 0.04 vs 0.31, loses savings race). Jev is the safer arm on both
populations; neither population funds enforcement on savings. No model
quality verdict beyond: miss CIs overlap partially (hers 0.04 vs mine 0.227 —
population differs, disclosed, not a model comparison).
