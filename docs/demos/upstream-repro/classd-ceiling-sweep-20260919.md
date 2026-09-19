# Class-D ceiling sweep: NOT-ANSWERABLE this way — reuse is long-horizon

Pane 3 (muse), 2026-09-19. Zero API calls (this receipt cost one offline run;
`API_CALLS=0` printed by the harness). Harness:
`work/p3-calibration/ceiling_sweep.py`, 24 frozen turns, original agent's own
continuations as the ceiling.

## Both curves

```
window (assistant msgs) : strict (novel-token facts) | loose (file/path/ident)
1    : 0.000 | 0.000
3    : 0.000 | 0.000
10   : 0.000 | 0.000
20   : 0.083 | 0.000
50   : 0.083 | 0.000
80   : 0.083 | 0.000
inf  : 0.708 | 0.375
```

Loose underperforms strict everywhere because most results contain no
path-like tokens (empty fact set never hits) — the looser notion helps only
where it applies, which is rarely. Neither definition clears 0.5 at any
generable window.

## Verdict: NOT-ANSWERABLE on this corpus

Reuse on these sessions is a LONG-horizon phenomenon: nothing fires before 80
messages, then inf jumps to 0.708. Any generation window a model arm could
afford has a ~zero ceiling, so no arm built on it can separate anything. This
is a refusal with a trigger, not a deferral: reopen when (a) a corpus shows
near-term reuse (re-run this script; it prints the curve in seconds), or (b) a
continuation method cheaper than per-message generation exists.

No preregistration is written because there is nothing to register an arm
against. The fact/definition windows MUST match if that day comes — the fault
R32 records.

## What this says about the ruling

The compaction RULED_OUT rests on a proxy whose checkable horizon this corpus
cannot reach: token-reuse is real (0.708 at inf) but lives 80+ messages out,
where no generable test can follow. The honest restatement, sharper than our
current caveat: the proxy is UNVALIDATABLE on this corpus, not merely
unvalidated. That does not rescue compaction (the drop rate stands on its own
numbers); it retires "but the agent might still need it" as an objection with
force behind it — nobody, including us, can currently check that claim either way.

## NO-CLAIM

n=24 frozen turns, 3 sessions; ceiling measured on the original agents'
continuations, which is the most favorable possible case for the proxy (any
other agent scores lower). Population reuse horizons outside these sessions
unmeasured.
