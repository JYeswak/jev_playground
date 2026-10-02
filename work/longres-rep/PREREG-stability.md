# PREREG — longres run-to-run stability (jev-4se3 follow-up)

Frozen 2026-10-02 before calls. Population is the exact 100 held rows from
WindyLantern's `work/longres/corpus.json` (not the misidentified replica rows).
Frozen choice prompt/classes/state/20s timeout; `jev-1.13.0`; 3 repeated calls
per row, 300-call cap, $0.025 cap, stop 401/402/403. Append one row per call
with sample_id, held-row win_sha, run (1..3), model/status/choice/usage/
latency. No text in receipt. Primary stability metric: fraction of rows whose
three decisions are not all identical (any-flip), plus pairwise differing
fraction over 300 row-pairs (three per sample). Also report every run's
reference-drop misses /100 and unreferenced savings using preregistered
(len-400)/len summarize and 100% drop. Report range and per-sample changes;
no majority-vote reclassification and no threshold changes. This estimates
repeatability on the fixed held rows, not population generalization.
