# Frozen toolcall corpus — Studio numbers, reproduced offline

**Date:** 2026-09-20 · **Level:** `[test]` · **Tag:** `[pending]` · **promoted=0**

Studio already measured this file. These numbers are **baked**, not re-derived
as a new claim. The in-tree scorer's job is to reprint them.

## Studio (authority)

Command:

```text
python3 work/jev-real-corpus-eval/jev_real_corpus_eval.py \
  work/p3-calibration/toolcall-corpus-frozen.jsonl
```

| | |
|---|---|
| n | **7846** |
| GOOD / BAD | **1665** / **6181** |
| always-abstain mean loss | **0.212210043** (1665/7846) |
| isError-only mean loss | **1.495284221** (11732/7846) |

**Mapping:** GOOD→allow; BAD→abstain/block.
**Loss:** correct=0, abstain on GOOD=1, allow on BAD=2.

**Finding:** isError-only **loses** to always-abstain. A useful Jev judge must
beat **0.212** mean loss on this split.

## Reproduced here

```text
python3 work/jev-real-corpus-eval/jev_real_corpus_eval.py \
  work/p3-calibration/toolcall-corpus-frozen.jsonl
```

```text
n=7846  GOOD=1665  BAD=6181  prevalence=0.212210043
CONTROL always-abstain mean_loss=0.212210043 (1665/7846)
BASELINE isError-only mean_loss=1.495284221 (11732/7846)  vs_control=LOSE
FINDING  isError-only loses to always-abstain; a useful Jev judge must beat 0.212 mean loss on this split.
NO-CLAIM  [pending] promoted=0  offline  no TYPESAFE  no CASS
```

Also: `node work/jev-real-corpus-eval/run.mjs` (same fractions, plus planted
RED). `node --test work/jev-real-corpus-eval/test/score.test.mjs`.

Identity lock: sha256 `dc90a374bbdb11bb521244be40afdaf096e56344e1c11baffb200bab05741580`.
A 10-row `diagnostic_synthetic` substitute is refused, not scored.

## Next levers, not queried

This cloud VM cannot reach `/Volumes/ZestData/cass-data/agent_search.db`
(~59.8k conv / 5.2M msgs) or live agent-mail (~6510 messages). Those are
offline-export levers. **Do not cite this receipt as CASS or mail access.**

## NO-CLAIM

- `[pending]` / **promoted=0**. Joshua promotes, not this run.
- Offline control + isError-only baseline only. No Jev call. No omp seam.
- isError is a component of the published BAD predicate; the lose-to-abstain
  result is still the number a judge has to beat.
