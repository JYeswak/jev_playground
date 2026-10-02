# PREREG — vendor-paste recognition (bead jev-30hi)

Frozen 2026-10-02 before any vendor live call. Last untested RECOGNITION
candidate per conductor (recognition is the only class with Jev wins).

## Corpus (keyless, frozen)

`work/vendor-paste/corpus.json` sha `e0e028c92b9d`: 72,888 file-windows;
pos = upstream/docs-mirror trees (manifest provenance), neg = own tree
(kit/scripts/foundation/.omp/work, dependency/fork trees excluded).
Sample sha `d510050d83bf`: dev 120 (60/60), held 200 (100/100), split by
source top-dir (no source in both). Builder `build-corpus.py`.

## Candidate check (keyless, done pre-prereg)

- License-header regex baseline: dev prec 1.000 rec 0.017; held prec 0.292
  rec 0.070 acc 0.450. Weak, unstable — headroom is ~90% of positives.
- Noise ceiling: 60-window blind content audit found 7 disagreements, ALL in
  committed dependency trees (work node_modules/.venv) since excluded from
  neg; 30 fresh windows on the cleaned population: 30/30 agree => ceiling
  ~0 (Wilson upper 0.11).

## Design (one Noul, positive-only)

State = pasted code text ONLY (no path — strict content recognition).
"This pasted code is vendored third-party code, not code written for this
repository. Judge only the code text, not any file path."
Predict VENDORED iff noul >= cut (dev-fitted, Youden J, tie-break lowest).
Fail-safe (timeout/error/invalid/refused) -> OWN.

## Bar (held 200, fixed pre-call)

Strongest baseline = license-header regex (recomputed on held).
PASS iff McNemar Jev-vs-baseline p < 0.05 with Jev more accurate AND Jev
recall >= 0.50 AND precision >= 0.50. LOCKED (`LOCK.md`, sha-locked before
dev calls): Jev accuracy exceeds baseline by >= 0.20 AND recall >= 0.60.

## Caps

<= 320 calls (120 dev + 200 held), $0.015 cap (~$0.010 expected), stop on
401/402/403, 20 s timeout, checkpointed by sample_id. Runner
`work/vendor-paste/run_vendor.mjs`; receipt `vendor-rows.jsonl`
(sample_id, split, noul, pred, status, tokens, latency; window text excluded,
win_sha joins). NO-CLAIM beyond file-window recognition on this tree.
