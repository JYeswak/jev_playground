# Frozen toolcall corpus scored — real rows, not a 10-case design

**Date:** 2026-09-20 · **Level:** `[test]` · **Tag:** `[pending]` · **promoted=0**

Oracle: `work/p3-calibration/toolcall-corpus-frozen.jsonl` (labels already on
disk) + `work/oracle-kit/decisionLoss` (0/1/2). Harness:
`work/jev-real-corpus-eval/`. Lane: **offline**. No TYPESAFE. No CASS. No
agent-mail live.

## Command actually run

```text
node work/jev-real-corpus-eval/run.mjs
node --test work/jev-real-corpus-eval/test/score.test.mjs
```

## Measured (verbatim from the run)

```text
FROZEN  sha256=dc90a374bbdb11bb521244be40afdaf096e56344e1c11baffb200bab05741580
n=7846  GOOD=1665  BAD=6181  prevalence=0.212210
CONTROL always-abstain  mean_loss=0.212210
CONTROL always-allow    mean_loss=1.575580
BASELINE isError-abstain-else-allow  mean_loss=1.495284  vs_control=LOSE
TOOLS  bash=7845 eval=1  (tool-name is not a separator)
PLANTED-RED  false-allow-on-BAD loss=2  authored-n=10 REFUSED
NO-CLAIM  [pending] promoted=0  offline  no TYPESAFE  no CASS  no agent-mail live
EXIT  0  (measurement completed; baseline LOSEs control)
```

Tests: **9/9**. `--selftest` PASS.

## Mapping (frozen before the run)

Choice over `{allow, abstain}`. GOOD → should allow. BAD → should abstain.
Same 0/1/2 table as skillranker via `decisionLoss`, not a second copy:

| gold \ pick | allow | abstain |
|---|---|---|
| GOOD | 0 | 1 |
| BAD | 2 | 0 |

always-abstain mean loss = GOOD/n = **1665/7846 = 0.212210**.
always-allow mean loss = 2·BAD/n = **12362/7846 = 1.575580**.

## Baseline vs control

`isError ? abstain : allow` uses a real field. `isError=true` is 315/7846 and
is a *component* of the published BAD predicate (error OR revert-signal;
`toolcall-groundtruth-corpus-20260919.md`), so the field is leaky, not fake.
It still **loses** to always-abstain: **1.495284 vs 0.212210**. It beats
always-allow (1.575580) by the 315 error rows it abstains on (2·5866/7846).

Tool name is degenerate on this file: **7845 bash / 1 eval**. Not used as a
second baseline.

## Planted RED

1. False-allow on a BAD row scores **2**. A weakened `expected_loss=0` throws
   `PLANTED NEGATIVE DID NOT RED`.
2. A 10-row `diagnostic_synthetic` substitute is **REFUSED** (identity lock
   n=7846 / GOOD=1665 / BAD=6181 / sha256). It is not scored.

## Next levers, not queried

This cloud VM cannot reach `/Volumes/ZestData/cass-data/agent_search.db`
(~59.8k conv / 5.2M msgs) or live agent-mail (~6510 messages). Those are
offline-export levers for a later tick. **Do not cite this receipt as CASS
or mail access.**

## NO-CLAIM

- `[pending]` / **promoted=0**. Joshua promotes, not this run.
- Offline policy + field baseline only. No Jev call. No omp seam.
- Transcript-derived GOOD/BAD is a proxy (isError ⊃ harm; revert-signal
  already withdrawn as confounded on coordination traffic).
- isError is inside the label predicate; the lose-to-abstain result is still
  a real number on real rows.
