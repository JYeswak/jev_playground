#!/usr/bin/env python3
"""Reproduce RECIPES.md recipe 4 and measure the predicate it depends on.

No API key and no training: upstream's out-of-fold scores are committed in their repo, so this
reads them and recomputes. Run from the repo root:

    python3 ensemble/run_lingspam.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from decorrelation import analyze  # noqa: E402

SCORES = Path("upstream/bitnovus/jev-spam-eval/results/lingspam_tfidf_oof.jsonl")
BARE = "TypeSafe: bare question (0 labels)"
CRITERIA = "TypeSafe: structured criteria (0 labels)"


def main() -> int:
    if not SCORES.exists():
        print(f"missing {SCORES} -- upstream clone not present", file=sys.stderr)
        return 2
    rows = [json.loads(line) for line in SCORES.open()]
    truth = [r["label"] == "spam" for r in rows]
    logreg_key = next(k for k in rows[0] if k.startswith("TF-IDF logreg, grouped"))

    print(f"{len(rows)} emails from {SCORES}\n")
    print(f"{'scorer':34s} {'acc':>8s} {'FN':>4s} {'FP':>4s}")
    for key in (BARE, CRITERIA, logreg_key):
        r = analyze([x[key] for x in rows], [x[logreg_key] for x in rows], truth)
        s = r.b if key == logreg_key else r.a
        print(
            f"{key[:34]:34s} {s.accuracy:8.4f} {s.false_negatives:4d} {s.false_positives:4d}"
        )

    print()
    for key, label in ((BARE, "bare + logreg"), (CRITERIA, "criteria + logreg")):
        r = analyze([x[key] for x in rows], [x[logreg_key] for x in rows], truth)
        print(
            f"{label:20s} acc={r.averaged.accuracy:.4f} FN={r.averaged.false_negatives} "
            f"FP={r.averaged.false_positives} | phi={r.phi:+.4f} "
            f"gain={r.gain_over_best_input:+.4f} {r.verdict}"
        )
    print(
        "\nphi is the predicate: near zero means the two scorers fail on different items, which is"
        "\nwhy averaging pays. A high phi would predict no gain."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
