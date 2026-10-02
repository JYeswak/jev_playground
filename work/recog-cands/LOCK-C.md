# LOCK-C (locked pre-run 2026-10-02, resolves on fresh-30 scored + blind-labeled)

Sentence: "B cut-0.04 no-gate on fresh-30 unscored held rows: FPR in [0.05,0.40]
AND recall >= 0.80."
sha256: `4aeae34e98d44e8ccd2e4f472331c8118b21bb6d3d4a2b7ba567c1cf28ff6a94`

Why proper this time: fresh-30 ids drawn from held-minus-scored (never asked at lock
time); gold = blind labels made AFTER the run without seeing scores. The quantity was
unobserved at lock; the lock can fail. (LOCK-A/B retired as BORN-TRUE: dev overlap
sealed their fates before locking.)

Context: confidence-gate variable tested dead first — 60/60 dev Noul confidences
exactly 0.0, so g fitted vacuous (0.0, dev-FPR 0.083 unchanged). Fresh-30 confirms the
cut-0.04 operating point independently (held-30 gave FPR 0.208).
