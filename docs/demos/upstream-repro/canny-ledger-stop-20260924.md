# Canny ledger — stop — 2026-09-24

Packet: `notes/deep/dispatch/p2-canny-ledger.md`. No Jev call. No `.omp/` edit. Clone untouched.

The gate was: score Canny's deterministic ledger (no Jev) on the frozen 24 and on 100+ finished turns labelled the same way, and stop if it does not beat always-not-done.

## Label

Frozen in `/tmp/canny-w70/extract.mjs:1-6` and reused by `/tmp/canny-ledger-measure/extract-all.mjs`. A finished turn is an assistant message with `stopReason` `stop` and at least 40 characters. Done iff a code file was edited and a Canny `isVerify` command exited 0 after the last such edit. No-edit turns are not-done. Unknown verify exits after an edit are excluded. Ledger allow is `!edited || verified` (`Canny/src/hook.ts:246`, `claimsDone` unset). Allow is scored as predicting done.

## Same 24

`/tmp/canny-w70/rows.jsonl`. All 24 were edited. Ledger allow iff verified iff done. Correct 24/24. Always-not-done 12/24. That beat is the label restated. It is not evidence.

## 100+ turns

Command: `node /tmp/canny-ledger-measure/extract-all.mjs`

```
scanned 86 sessions, stops 1187, excludedUnknown 0, labelled 1145
done 37, not_done 1108, edited 1067, no_edit 78
ledger_allow_as_done_correct 1067
always_not_done 1108
beats false
```

On the 1067 edited rows the ledger matches the label 1067/1067, again by construction. The 78 no-edit rows are labelled not-done and the ledger allows all 78, so it predicts done and is wrong on every one of them.

Prevalence, after the labels, score = 1 if allow else 0:

```
node work/jev-prevalence-first/prevalence-check.mjs /tmp/canny-ledger-measure/scored.jsonl --score p --truth done
near-threshold: 0/1145 (window ±0.1 around 0.5)
own-constant: always-no 1108/1145 (majority share 96.8%)
verdict: 1067/1145 vs best-constant 1108 + near 0 → WEAK
EXIT:3
```

Labels-only, before that score was attached:

```
near-threshold: n/a (no scores yet)
own-constant: always-false 1108/1145 (majority share 96.8%)
verdict: DEFERRED — no model scores; a question on this set must beat always-false 1108/1145
EXIT:0
```

## Stop

The ledger does not beat always-not-done on the set the packet named (1145 labelled turns, 1067 vs 1108). No advisory hook. No L0. No L3. No bead for a tool that failed the gate.

## Boundary

NO-CLAIM: this does not say a completion-claim reminder is useless. That is a different predicate (message claims done, and no verify after the last edit). It was not the gate. This does not re-measure Jev. Spend: 0 calls. The 24-row 24/24 figure is `[Invalid]` as a win and `[test]` as a count on those rows. The 1145-row WEAK is `[test]`, lane offline, date 2026-09-24, model not called.

## Rows committed — 2026-09-24

`/tmp/canny-ledger-measure/scored.jsonl` copied byte-identical (`cmp`) to `work/tmp-rescue/canny-ledger-scored.jsonl`, sha256 `be928b7f52c622bb86cdb3f03af16ffc27f1f40ff8b2cfd19f8f4c0e062db595`. Re-score that file. The `/tmp` copy was not deleted.
