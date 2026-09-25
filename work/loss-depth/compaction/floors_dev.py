#!/usr/bin/env python3
"""Non-Noul keep signals on the blind-labelled dev curve (bead jev-9gtw.6 follow-up). KEYLESS.

  python3 work/loss-depth/compaction/floors_dev.py

Preregistered here, committed before the first run. Question: do the cheap baselines that
tamaratran/fast-jev-compaction#52 reports (keep the largest outputs, AUC 0.847; a 14-feature logistic
regression, 0.836; both on proxy labels) reach the jev-jec6 bar on OUR blind labels?

Rows: the 7-session stub-free dev slice (jev-9gtw.6), unpinned calls, final labels, needed vs
not-needed (50 / 165). Undecidable calls are left out, as in every readout.

Signals, higher = keep, direction fixed now (an AUC below 0.5 is reported as is):
- single features, prefix-visible only: result_chars, position (later = higher), later_overlap,
  input_chars, goal_names_target, written_later_in_prefix; from work/compaction-floors/features-*.jsonl
  and this directory's features.jsonl. horizon_overlap and every use_* field read the future and are
  never used.
- LR: logistic regression (numpy, L2 1.0, standardized) on log1p(result_chars), log1p(input_chars),
  position, tool class one-hot (read / run / other), later_overlap, goal_names_target,
  written_later_in_prefix, result_is_error. Scored leave-one-session-out: each session's calls get
  probabilities from a model fit on the other 6.
- LR+Jev: the same plus A0's keepCall and keepResult from dev-answers.jsonl (a hybrid, reported apart).

Operating point, as in the replay: the dev cut is the smallest observed score at which >= 50% of
not-needed calls drop; report needed kept there with its Wilson 95% interval.

Gate: a signal becomes the next held-out candidate only if, at its dev cut, the needed-kept Wilson
lower bound is >= 0.80 (jev-jec6's bar). For LR the pooled out-of-fold scores come from 7 different
fits, so its dev cut is indicative; a candidate LR would be refit on all 7 sessions and its cut fixed
from that fit before any held-out.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "work" / "compaction-need"))
sys.path.insert(0, str(ROOT / "work" / "compaction-keep"))
import keep as K  # noqa: E402
import need as N  # noqa: E402

L2 = 1.0
DROP_AT_LEAST = 0.50
BAR = 0.80


def auc(pos, neg) -> float:
    return sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (
        len(pos) * len(neg)
    )


def operating(pos, neg) -> tuple[float, int, int, float]:
    t = min(
        v
        for v in sorted(set(pos + neg))
        if sum(x < v for x in neg) >= DROP_AT_LEAST * len(neg)
    )
    kept = sum(x >= t for x in pos)
    lo, _ = N.R1.wilson(kept, len(pos))
    return t, kept, sum(x < t for x in neg), lo


def fit(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """L2 logistic regression by Newton's method; the intercept is not penalized."""
    Xb = np.hstack([np.ones((len(X), 1)), X])
    w = np.zeros(Xb.shape[1])
    pen = np.eye(Xb.shape[1]) * L2
    pen[0, 0] = 0.0
    for _ in range(50):
        p = 1 / (1 + np.exp(-Xb @ w))
        g = Xb.T @ (p - y) + pen @ w
        H = Xb.T @ (Xb * (p * (1 - p))[:, None]) + pen
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-8:
            break
    return w


def main() -> int:
    lab = {}
    for mod in (N, K):
        got = mod.final(mod.calls())
        if isinstance(got, str):
            sys.exit(f"REFUSED: {got}")
        lab.update(got[2])
    mine = {
        (f["session"], f["tool_use_id"]): f
        for f in N.read_jsonl(HERE / "features.jsonl")
    }
    floors = {}
    for name in ("x86y", "jec6"):
        for f in N.read_jsonl(ROOT / f"work/compaction-floors/features-{name}.jsonl"):
            floors[(f["session"], f["tool_use_id"])] = f
    a0 = {
        (r["session"], r["tool_use_id"]): r
        for r in N.read_jsonl(HERE / "dev-answers.jsonl")
        if r["arm"] == "A0"
    }
    stub = {f["session"] for f in mine.values() if f["result_shaken"]}
    rows = [
        k
        for k, f in mine.items()
        if f["session"] not in stub
        and not f["pinned"]
        and lab[k] in ("needed", "not-needed")
    ]
    y = np.array([lab[k] == "needed" for k in rows], dtype=float)
    print(
        f"dev slice: {len({k[0] for k in rows})} sessions, needed {int(y.sum())}, not-needed {int(len(y) - y.sum())}"
    )

    def row(k):
        f, g = mine[k], floors[k]
        return {
            "result_chars": g["result_chars"],
            "position": g["position"],
            "later_overlap": g["later_overlap"],
            "input_chars": f["input_chars"],
            "goal_names_target": float(f["goal_names_target"]),
            "written_later_in_prefix": float(f["written_later_in_prefix"]),
            "tool_class": g["tool_class"],
            "result_is_error": float(f["result_is_error"]),
        }

    feats = [row(k) for k in rows]
    scores = {
        name: np.array([r[name] for r in feats], dtype=float)
        for name in (
            "result_chars",
            "position",
            "later_overlap",
            "input_chars",
            "goal_names_target",
            "written_later_in_prefix",
        )
    }

    def design(with_jev: bool) -> np.ndarray:
        cols = []
        for r, k in zip(feats, rows):
            c = [
                math.log1p(r["result_chars"]),
                math.log1p(r["input_chars"]),
                r["position"],
                float(r["tool_class"] == 2),
                float(r["tool_class"] == 1),
                r["later_overlap"],
                r["goal_names_target"],
                r["written_later_in_prefix"],
                r["result_is_error"],
            ]
            if with_jev:
                c += [a0[k]["keepCall"], a0[k]["keepResult"]]
            cols.append(c)
        return np.array(cols)

    sessions = np.array([k[0] for k in rows])
    for name, with_jev in (
        ("LR (leave-one-session-out)", False),
        ("LR+Jev (leave-one-session-out)", True),
    ):
        X = design(with_jev)
        oof = np.zeros(len(y))
        for s in sorted(set(sessions)):
            tr, te = sessions != s, sessions == s
            mu, sd = X[tr].mean(0), X[tr].std(0)
            sd[sd == 0] = 1.0
            w = fit((X[tr] - mu) / sd, y[tr])
            oof[te] = 1 / (
                1 + np.exp(-np.hstack([np.ones((te.sum(), 1)), (X[te] - mu) / sd]) @ w)
            )
        scores[name] = oof

    print(
        "\n| signal | AUC | dev cut | needed kept at dev cut | not-needed dropped | lower bound | gate |"
    )
    print("|---|---:|---:|---|---:|---:|---|")
    best = None
    for name, s in scores.items():
        pos, neg = list(s[y == 1]), list(s[y == 0])
        t, kept, dropped, lo = operating(pos, neg)
        hi = N.R1.wilson(kept, len(pos))[1]
        print(
            f"| {name} | {auc(pos, neg):.3f} | {t:.4g} | {kept}/{len(pos)} ({max(0.0, lo):.3f}-{min(1.0, hi):.3f}) | {dropped}/{len(neg)} | {lo:.3f} | {'MEETS' if lo >= BAR else 'no'} |"
        )
        if lo >= BAR and (best is None or lo > best[1]):
            best = (name, lo)
    print(
        f"\nnext held-out candidate: {best[0] + ' (lower bound ' + format(best[1], '.3f') + ')' if best else 'none: no signal reaches the bar on the dev curve'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
