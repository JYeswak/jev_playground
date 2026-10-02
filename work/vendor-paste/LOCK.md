# LOCK — vendor-paste predictions (bead jev-30hi)

Locked 2026-10-02 BEFORE any vendor live call. Predictions about the HELD 200:

1. Jev accuracy exceeds the license-header baseline by >= 0.20.
2. Jev recall >= 0.60 (recognition: the answer is visible in the judged text).
3. Jev precision >= 0.50.
4. Dev-fitted cut lands in [0.15, 0.85] (a degenerate 0/1 cut means no signal).

All four must hold alongside McNemar p < 0.05 for PASS. Any other outcome is
reported as measured, no retrofit.
