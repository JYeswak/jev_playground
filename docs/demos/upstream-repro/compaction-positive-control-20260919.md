# Positive control: the harness detects signal, so the keep_p null is REAL (verdict A)

Pane 3 (muse), 2026-09-19. Same 150 calls, same sessions, same single-request
batching, same SDK path as the calibration arm — run from the pinned
`work/pysdk` env (`uv.lock`, no local-path refs). 150 live requests,
`jev-latest` -> `jev-1.13.0`, run once. Harness: `work/p3-calibration/pos_control.py`;
outputs `control_probs.jsonl` (committed); AUC = Mann-Whitney, the same code for
all three lines below.

## Design

Two deterministic-label questions per tool result, truth computable without a model:

- **err** (n_pos 56/150): is the result an error/failure message — regex
  (error|failed|exit status|traceback|rc=[1-9]|…) OR the session's own is_error flag.
- **read** (n_pos 23/150): did the call read a file — toolName == read.
- Reference line: keep_p (from probs.jsonl) vs the needed-later oracle.

Near-empty (<40 chars, 6/150) rejected for base rate before spending.

## Result

```
err:  AUC=0.698 n_pos=56/150
read: AUC=0.941 n_pos=23/150
keep-vs-needed: AUC=0.457 n_pos=111/150
```

## Verdict: A

**Harness detects signal (AUC 0.94 / 0.70), therefore the keep_p null is REAL.**
The read line is the clean proof: same pipeline, same SDK, same scorer family —
a crisp concept scores 0.94, so a null at 0.457 is a property of the keep
judgment, not harness blindness. The err line at 0.70 (not 0.9) is consistent
with a noisier truth (the word "error" appears in benign contexts like "0 errors"
and "error handling") rather than pipeline failure — and 0.70 still clears 0.5
by a margin the keep line never approaches. Combined with pane 1's richer-state
AUCs (0.522/0.348/0.648, straddling 0.5): two SDKs, two state shapes, three
sessions each, same answer.

## NO-CLAIM: what this control does NOT rule out

- That the keep-question WORDING is worse than the control wording (a better
  keep prompt might find signal; the null is about the shipped wording).
- That full-transcript states would discriminate where call-local ones do not —
  but pane 1's richer-state null already closes most of that gap.
- That the needed-ORACLE (rather than the judge) is the null source: err/read
  AUCs use deterministic labels, so they validate judge+pipeline, not the oracle.
  The oracle's own validation is the sibling arm's planted negatives
  (noise→0/200, end-of-transcript→0/200), not this receipt.
