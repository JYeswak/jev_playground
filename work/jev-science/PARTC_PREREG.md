# Part C prereg: hash-locked predictions (jev-2zbl)

Committed pre-resolution 2026-10-02 (OrangeFrog). Predictions below are locked by
sha256 of the prediction sentences; scored when the resolving runs land. A lock that
resolves wrong is a result about the theory, not a license to edit the lock.

## Method
Each lock states a falsifiable sentence, the resolving run, and the hash of the
sentence committed before the run. No resolution may edit its lock. Score: Brier-style
hit/miss per lock + calibration-in-the-small across locks over time.

## LOCK-1 (resolves on next same-question repeat of any live Choice run)
Sentence: "A same-question fresh repeat of a 30-row live Choice run flips >=1 modal
answer (I0-style instability >0)."
sha256 (computed 2026-10-02 over the exact sentence bytes):
`f8ec8697b2a09b8c8752d239d1136a656bac796b44f407e02f9626d27e949108`
Status: BORN-TRUE on TS v1/v2 pair (1/1: 2/30 modal flips; v1 0 interr/2 miss vs
v2 2 interr/2 miss); stays open for the next pair.

## LOCK-2 (resolves on Part B web arm, if unit text ever becomes available)
Sentence: "On web-screen Score units, T0 repeat same-threshold agreement is <95%
(score-level instability exceeds the Choice-level I0 measured on msax)."
Resolution: rerun scorer on web arm rows when available.

## LOCK-3 (resolves on next metamorphic run on a new task)
Sentence: "On a new Choice task, T1 option-permute flips <=10% (order irrelevance
generalizes beyond msax)."
Resolution: next Part-B-style run (diffrisk-Choice candidate).

## First computed lock (this file's own integrity)
`sha256sum work/jev-science/PARTC_PREREG.md` recorded at commit time in the bead
comment; any later edit changes it, which is itself detectable.
