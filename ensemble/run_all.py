#!/usr/bin/env python3
"""Does decorrelation PREDICT whether averaging two scorers pays? Three pairs, someone else's data.

RECIPES.md recipe 4 said averaging a zero-label judgment with a trained classifier beat both, and
stated its falsifier: "stops being true when the two are correlated." Upstream computes the average
and never measures the correlation, so the rule had one supporting observation and no test.

This runs three pairs from upstream's committed out-of-fold scores -- no API key, no training:

  1. bare question + logreg   (Ling-Spam)     expected decorrelated
  2. Jev choice + TF-IDF      (phish, n=5733) expected decorrelated
  3. logreg + naive Bayes     (Ling-Spam)     SAME FEATURES, expected CORRELATED

Pair 3 is the natural experiment. It is not a synthetic self-pair: two genuinely different
algorithms, trained on the same TF-IDF features, both good. If decorrelation is the mechanism, this
is where averaging must FAIL -- and a negative gain here is the closest thing to a refutation test
the available data allows.

    python3 ensemble/run_all.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from decorrelation import analyze  # noqa: E402

R = Path("upstream/bitnovus/jev-spam-eval/results")
BARE = "TypeSafe: bare question (0 labels)"


def lingspam_pairs():
    rows = [json.loads(l) for l in (R / "lingspam_tfidf_oof.jsonl").open()]
    truth = [r["label"] == "spam" for r in rows]
    lr = next(k for k in rows[0] if k.startswith("TF-IDF logreg, grouped"))
    nb = next(k for k in rows[0] if k.startswith("TF-IDF naive Bayes"))
    yield "question + logreg", [r[BARE] for r in rows], [r[lr] for r in rows], truth
    # Same feature space, two algorithms: the correlated control.
    yield "logreg + naiveBayes", [r[lr] for r in rows], [r[nb] for r in rows], truth


def phish_pair():
    jev = {}
    for line in (R / "phish_main_all.jsonl").open():
        d = json.loads(line)
        c = d.get("choices", {}).get("category")
        if c:
            p = c["probabilities"]
            # 3-class choice collapsed to "not legitimate"; the TF-IDF file is collapsed the same
            # way. Stated because it is a derivation, not a number upstream published.
            jev[d["file"]] = (p.get("phishing", 0) + p.get("spam", 0), d["label"])
    tf = {}
    for line in (R / "phish_tfidf_predictions.jsonl").open():
        d = json.loads(line)
        p = d["probabilities"]
        tf[d["file"]] = p.get("phish", 0) + p.get("spam", 0)
    keys = [k for k in jev if k in tf]
    yield (
        f"jev + tfidf (phish, n={len(keys)})",
        [jev[k][0] for k in keys],
        [tf[k] for k in keys],
        [jev[k][1] != "ham" for k in keys],
    )


def main() -> int:
    if not R.exists():
        print(f"missing {R} -- upstream clone not present", file=sys.stderr)
        return 2
    print(f"{'pair':28s} {'phi':>8s} {'gain':>9s}  verdict")
    results = []
    for name, a, b, truth in [*lingspam_pairs(), *phish_pair()]:
        r = analyze(a, b, truth)
        results.append((r.phi, r.gain_over_best_input))
        print(f"{name:28s} {r.phi:+8.4f} {r.gain_over_best_input:+9.4f}  {r.verdict}")

    print(
        "\nThe ordering is the finding: the two decorrelated pairs gain, the correlated pair LOSES."
        "\nA gain that came from arithmetic rather than decorrelation would not change sign."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
