# CROSS-CHECK — second-slice verification (Wave B §6 Pass 8 of P1-P12)

Same code path as `pipeline-run.mjs` (Pass 6), second 40-file window over
local omp session logs. `cross-check.mjs` imports `joinOutcomes` /
`checkPresence` / `randomBaseline` / `ownConstant` — no copied logic — with a
`--skip N` flag (default 40). Read-only over session logs; 0 Jev calls.

## Quoted rows

Slice-1 (Pass 6, `pipeline-run.mjs`, files 1–40):

`"LIVE matched=15529 unmatched=0 zeroHit=false presence=ABSENT-NEXT-TO-FIRING top3=[dcg_allow:8310,lane_allow:7111,dcg_block:108] ownConstant=0.5351(8310/15529,label='dcg_allow') randomBaseline=0.4954 [kind-as-label skew baselines only, NOT judge quality] files=40"`

Slice-2 (this pass, `cross-check.mjs --skip 40`, files 41–80):

`"LIVE matched=4012 unmatched=0 zeroHit=false presence=ABSENT-NEXT-TO-FIRING top3=[dcg_allow:3905,dcg_block:71,lane_allow:35] ownConstant=0.9733(3905/4012,label='dcg_allow') randomBaseline=0.9487 [kind-as-label skew baselines only, NOT judge quality] files=40 skip=40"`

## Comparison

| Field | Slice-1 | Slice-2 | Δ |
|---|---|---|---|
| matched | 15529 | 4012 | −11517 (−74%) |
| unmatched | 0 | 0 | 0 |
| zeroHit | false | false | same |
| presence | ABSENT-NEXT-TO-FIRING | ABSENT-NEXT-TO-FIRING | same |
| top kind | dcg_allow:8310 (53.5%) | dcg_allow:3905 (97.3%) | +43.8pp share |
| 2nd kind | lane_allow:7111 (45.8%) | dcg_block:71 (1.8%) | lane_allow ~vanishes (35 rows) |
| ownConstant | 0.5351 | 0.9733 | +0.4382 |
| randomBaseline | 0.4954 | 0.9487 | +0.4533 |

## Verdict: DIVERGED (slice composition) / STABLE (pipeline mechanics)

The pipeline mechanics are stable: both slices join cleanly
(unmatched=0, zeroHit=false, no refusal), return the same presence verdict
(ABSENT-NEXT-TO-FIRING), and compute both skew baselines without error.

The slices themselves diverge: slice-2 is a near-monomorphic dcg_allow
window (97.3% majority; ownConstant 0.9733, random shuffle still lands
0.9487 because there is almost nothing to permute), while slice-1 is a
mixed dcg_allow/lane_allow window (53.5/45.8%; ownConstant 0.5351). The
kind-as-label baselines describe per-window label skew, not judge quality
— so the divergence says the two file windows cover different session
eras/content, not that the pipeline misbehaved. Consequence: any constant
baseline quoted from one 40-file slice does not transfer to another; the
window must be stated alongside the number (as both rows do with
`files=40` / `skip=40`).
