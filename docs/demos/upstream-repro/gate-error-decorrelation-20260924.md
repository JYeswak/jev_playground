# Gate error decorrelation (bead `jev-gate-error-decorrelation-ltk`)

Numbers only. No proposal to drop or merge a gate.

Re-score, keyless: `python3 work/gate-decor/score.py`

The scorer reads `docs/demos/upstream-repro/gate-error-decor-extract-20260924.tsv`.
It calls `ensemble.decorrelation.analyze` unchanged. A failure is exit code
nonzero. `analyze` is given score `1.0` on failure and `0.0` on pass, and a
truth vector of all false, so its error indicator is the failure vector.
`_phi` returns `0.0` when a vector is constant. This wrapper reports that case
as `undefined`, not `0`.

## Alignment

Source log `foundation/gate-outcomes.tsv`, 4,909 rows at scoring time. Mode
`run` only: 4,798 rows. The 111 `--selftest` rows are not in the extract.

`all-runs` aligns on the same timestamp and head sha. A `gates.sh` invocation
stamps stages seconds apart, so many pairs have `n=0` under that rule.

`one-per-sha` keeps the last timestamp per stage per sha. 10 stage-sha pairs
had more than one exit code; the last timestamp won. Repeated runs at one sha
are not independent.

**The verdict uses `one-per-sha`.**

## Constant stages

Run-mode failures were 0 for stages 10, 15, 16, 17, 20, 30, 40, 85, 90, and
96. Every pair that includes one of those stages is `phi=undefined`.

Non-constant, failures / runs seen: 44 is 5/27, 50 is 5/388, 60 is 1/386,
70 is 9/386, 80 is 25/368, 95 is 5/368, 97 is 9/368.

## Defined pairs, one-per-sha (the verdict)

| pair | n | phi | disagree | gain |
|---|---:|---:|---:|---:|
| 44 x 60 | 23 | -0.0978 | 0.2174 | -0.1739 |
| 44 x 70 | 23 | -0.2418 | 0.3913 | -0.2174 |
| 44 x 80 | 22 | 0.0000 | 0.5000 | -0.4091 |
| 44 x 97 | 22 | -0.1873 | 0.3182 | -0.1818 |
| 50 x 60 | 324 | -0.0044 | 0.0093 | -0.0062 |
| 50 x 70 | 324 | -0.0108 | 0.0247 | -0.0185 |
| 50 x 80 | 319 | -0.0129 | 0.0533 | -0.0502 |
| 50 x 95 | 319 | -0.0045 | 0.0094 | -0.0063 |
| 50 x 97 | 319 | -0.0071 | 0.0188 | -0.0157 |
| 60 x 70 | 324 | 0.4051 | 0.0154 | -0.0154 |
| 60 x 80 | 319 | -0.0129 | 0.0533 | -0.0502 |
| 60 x 95 | 319 | -0.0045 | 0.0094 | -0.0063 |
| 60 x 97 | 319 | -0.0071 | 0.0188 | -0.0157 |
| 70 x 80 | 319 | 0.4968 | 0.0376 | -0.0345 |
| 70 x 95 | 319 | -0.0110 | 0.0251 | -0.0188 |
| 70 x 97 | 319 | 0.5399 | 0.0157 | -0.0094 |
| 80 x 95 | 319 | 0.3457 | 0.0439 | -0.0439 |
| 80 x 97 | 319 | 0.5491 | 0.0345 | -0.0345 |
| 95 x 97 | 319 | -0.0100 | 0.0219 | -0.0157 |

`44 x 80` phi `0.0000` is computed. Both vectors vary on that overlap. It is
not the constant-vector case.

Every defined pair has negative gain. `analyze().verdict` is
`AVERAGE_DID_NOT_PAY` on each of them. That label is the function's output.
It is not a decision about a gate.

## Defined pairs, all-runs (same timestamp and sha)

| pair | n | phi | disagree | gain |
|---|---:|---:|---:|---:|
| 60 x 70 | 323 | 0.3744 | 0.0186 | -0.0186 |
| 80 x 95 | 203 | 0.4682 | 0.0493 | -0.0493 |
| 80 x 97 | 162 | 0.5261 | 0.0309 | -0.0309 |
| 95 x 97 | 325 | -0.0143 | 0.0308 | -0.0215 |

Other all-runs pairs are `undefined` or `n=0`.
