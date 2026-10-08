# PREREG — longres true disjoint replication (jev-4se3 follow-up)

Frozen 2026-10-02 before calls. Exclusion set is every source session file
from `work/longres/corpus.json`, `work/longres-rep/corpus.json`, and
`work/longres/corpus2.json` (WindyLantern's first, our prior, and her fresh
matched-miss population); compare canonical file-path SHA-256 membership.
Extract 200 new >=10k results from the same seven-day pool and mechanical
3-probe label, seed 20261008, fit 100 / held 100 by file, write corpus3.json.
Verify zero excluded-file overlap AND zero exact head+tail hash overlap before
calling. Freeze question/state/choices/timeout/fail-safe from
PREREG-longres.md. Jev <=200 calls, $0.015 cap, stop 401/402/403.

Baseline: fit size+tool Youden-J on dev-100, as frozen in original prereg.
Primary matched-miss comparison: on held-100, find the size threshold with
minimum absolute difference from Jev's held reference-drop miss count; ties
choose greatest baseline unreferenced savings, then larger threshold. Report
both exact miss counts and savings on held unreferenced rows, Jev/base ratio,
Wilson miss CIs, call-level rows/tokens/latency/status and spend. Replication
signal: Jev unreferenced savings strictly exceed matched-miss baseline; no
claims about enforcement. Secondary locked original-bar result also reported:
Jev miss <= fitted-baseline miss AND Jev savings >=1.2x fitted-baseline
savings. No tuning after calls. Invalid/refused -> KEEP.