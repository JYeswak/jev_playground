#!/usr/bin/env python3
"""X4 vendored-code TF-IDF probe on the frozen 320-window sample (bead jev-x4-vendored-probe-closeout-82p7).

Reproduces the held AUC and paired DeLong results, then adds:
  * a source-group cluster bootstrap for probe-minus-Jev and probe-minus-Clef AUC differences;
  * ECE after one dev-fitted Platt map per arm (same fit as work/local-decision-arms/vendor.py:145),
    with a source-group bootstrap CI, beside the contract's raw-Jev reference.
Offline, CPU only, no model calls, $0. Prints one JSON object to stdout.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix, hstack
from scipy.stats import norm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "work/vendor-paste/sample.json"
JEV_ROWS = ROOT / "work/vendor-paste/vendor-rows.jsonl"
CLEF_ROWS = ROOT / "work/local-decision-arms/vendor-rows-clefflash.jsonl"
CLEF_DEV_ROWS = ROOT / "work/local-decision-arms/vendor-rows-clefflash-dev.jsonl"
EXPECTED_SAMPLE_SHA256 = (
    "2a167ed69ebfa5aa41399b278c14c1dae5a40ec630f4de97cfbb7faaa39644ab"
)
EXPECTED_DEV = 120
EXPECTED_HELD = 200
SEED = 20261004
BOOTSTRAP_B = 2000
OOF_FOLDS = 5
JEV_RAW_ECE_REFERENCE = (
    0.1846  # work/local-decision-arms/BAR-vendor.md contract reference
)


def load_jsonl(path: Path) -> dict[str, dict]:
    return {
        row["sample_id"]: row
        for row in (
            json.loads(line) for line in path.read_text().splitlines() if line.strip()
        )
    }


def source_group(row: dict) -> str:
    parts = row["file"].split("/")
    return parts[0] + ":" + (parts[1] if len(parts) > 1 else "")


def midranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and sorted_values[end] == sorted_values[start]:
            end += 1
        ranks[start:end] = (start + 1 + end) / 2.0
        start = end
    result = np.empty(len(values), dtype=float)
    result[order] = ranks
    return result


def delong_covariance(
    scores: np.ndarray, labels: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    positives = int(labels.sum())
    negatives = len(labels) - positives
    if positives < 2 or negatives < 2:
        raise ValueError("DeLong needs at least two positive and two negative rows")
    ordered = scores[:, np.argsort(-labels, kind="mergesort")]
    positive_scores, negative_scores = ordered[:, :positives], ordered[:, positives:]
    rank_positive = np.vstack([midranks(row) for row in positive_scores])
    rank_negative = np.vstack([midranks(row) for row in negative_scores])
    rank_all = np.vstack([midranks(row) for row in ordered])
    aucs = rank_all[:, :positives].sum(axis=1) / (positives * negatives) - (
        positives + 1
    ) / (2 * negatives)
    v01 = (rank_all[:, :positives] - rank_positive) / negatives
    v10 = 1.0 - (rank_all[:, positives:] - rank_negative) / positives
    covariance = np.cov(v01) / positives + np.cov(v10) / negatives
    return aucs, np.atleast_2d(covariance)


def delong_pair(scores_a: np.ndarray, scores_b: np.ndarray, labels: np.ndarray) -> dict:
    aucs, covariance = delong_covariance(np.vstack([scores_a, scores_b]), labels)
    variance = float(covariance[0, 0] + covariance[1, 1] - 2 * covariance[0, 1])
    difference = float(aucs[0] - aucs[1])
    if variance <= 0:
        raise ValueError(f"non-positive DeLong variance: {variance}")
    z = difference / math.sqrt(variance)
    return {
        "auc_a": float(aucs[0]),
        "auc_b": float(aucs[1]),
        "difference": difference,
        "z": z,
        "p_two_sided": float(2 * norm.sf(abs(z))),
    }


def holm(p_values: list[float]) -> list[float]:
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted, running = [0.0] * len(p_values), 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted


def ece(scores: np.ndarray, labels: np.ndarray) -> float:
    """10-bin ECE, bin rule min(int(p*10), 9) as in work/local-decision-arms/vendor.py:85."""
    bins = np.minimum((scores * 10).astype(int), 9)
    total = 0.0
    for b in np.unique(bins):
        mask = bins == b
        total += mask.mean() * abs(scores[mask].mean() - labels[mask].mean())
    return float(total)


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def platt_fit(dev_scores: np.ndarray, dev_labels: np.ndarray) -> tuple[float, float]:
    """2,000 steps of gradient descent, lr 0.1, init (1, 0); work/local-decision-arms/BAR-vendor-platt.md."""
    x, a, b = _logit(dev_scores), 1.0, 0.0
    for _ in range(2000):
        p = 1 / (1 + np.exp(-(a * x + b)))
        a -= 0.1 * float(((p - dev_labels) * x).sum()) / len(x)
        b -= 0.1 * float((p - dev_labels).sum()) / len(x)
    return a, b


def platt_apply(scores: np.ndarray, a: float, b: float) -> np.ndarray:
    return 1 / (1 + np.exp(-(a * _logit(scores) + b)))


def fit_probe(train_rows: list[dict], held_ids: set[str]):
    """Fit vectorizers and classifier on train_rows; refuse any row from the held split."""
    leaked = sorted({r["sample_id"] for r in train_rows} & held_ids)
    if leaked or any(r.get("split") == "held" for r in train_rows):
        raise ValueError(f"probe fit refused: held rows in training set ({leaked[:3]})")
    word = TfidfVectorizer(
        analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True
    )
    char = TfidfVectorizer(
        analyzer="char", ngram_range=(3, 5), min_df=2, sublinear_tf=True
    )
    texts = [r["window"] for r in train_rows]
    x = hstack(
        [
            word.fit_transform(texts),
            char.fit_transform(texts),
            csr_matrix(_lic(train_rows)),
        ],
        format="csr",
    )
    y = np.asarray([int(r["label"] == "pos") for r in train_rows], dtype=int)
    model = LogisticRegression(
        C=1.0, solver="liblinear", max_iter=1000, random_state=SEED
    )
    start = time.perf_counter()
    model.fit(x, y)
    fit_seconds = time.perf_counter() - start

    def score(rows: list[dict]) -> np.ndarray:
        texts_ = [r["window"] for r in rows]
        xs = hstack(
            [word.transform(texts_), char.transform(texts_), csr_matrix(_lic(rows))],
            format="csr",
        )
        return model.predict_proba(xs)[:, 1]

    return score, int(x.shape[1] - 1), fit_seconds


def _lic(rows: list[dict]) -> np.ndarray:
    return np.asarray(
        [int(str(r.get("lic")) == "True") for r in rows], dtype=float
    ).reshape(-1, 1)


def cluster_bootstrap(
    stat, labels: np.ndarray, groups: list[str], b: int = BOOTSTRAP_B, seed: int = SEED
) -> dict:
    """Percentile CI from resampling source groups with replacement; refuses window-level resampling."""
    groups_arr = np.asarray(groups)
    units = np.unique(groups_arr)
    if len(units) >= len(labels):
        raise ValueError(
            "cluster bootstrap refused: one unit per window is window resampling, not source groups"
        )
    members = [np.flatnonzero(groups_arr == u) for u in units]
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(b):
        idx = np.concatenate(
            [members[i] for i in rng.integers(0, len(units), len(units))]
        )
        if labels[idx].min() == labels[idx].max():
            continue
        values.append(stat(idx))
    arr = np.asarray(values)
    return {
        "units": int(len(units)),
        "b_used": int(len(arr)),
        "ci95": [float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))],
    }


def main() -> None:
    sample_bytes = SAMPLE.read_bytes()
    sample = json.loads(sample_bytes)
    canonical_sha = hashlib.sha256(
        json.dumps(sample, sort_keys=True).encode()
    ).hexdigest()
    if hashlib.sha256(sample_bytes).hexdigest() != EXPECTED_SAMPLE_SHA256:
        raise SystemExit("sample file SHA256 changed after preregistration")
    if not canonical_sha.startswith("d510050d83bf"):
        raise SystemExit("canonical sample fingerprint differs from preregistration")
    dev, held = sample["dev"], sample["held"]
    if (len(dev), len(held)) != (EXPECTED_DEV, EXPECTED_HELD):
        raise SystemExit(f"unexpected split sizes: dev={len(dev)} held={len(held)}")
    held_ids = {r["sample_id"] for r in held}
    if {r["sample_id"] for r in dev} & held_ids:
        raise SystemExit("dev/held sample IDs overlap")
    dev_groups, held_groups = (
        [source_group(r) for r in dev],
        [source_group(r) for r in held],
    )
    if set(dev_groups) & set(held_groups):
        raise SystemExit("dev/held source groups overlap")
    if any(r.get("label") not in {"pos", "neg"} for r in dev + held):
        raise SystemExit("invalid label")

    jev, clef, clef_dev = (
        load_jsonl(JEV_ROWS),
        load_jsonl(CLEF_ROWS),
        load_jsonl(CLEF_DEV_ROWS),
    )
    if (
        set(jev) != {r["sample_id"] for r in dev + held}
        or set(clef) != held_ids
        or set(clef_dev) != {r["sample_id"] for r in dev}
    ):
        raise SystemExit("incumbent row IDs do not match the preregistered sample")
    for row in dev + held:
        if (
            jev[row["sample_id"]].get("win_sha")
            != hashlib.sha256(row["window"].encode()).hexdigest()[:12]
        ):
            raise SystemExit(f"Jev window hash mismatch for {row['sample_id']}")
    if any(jev[r["sample_id"]].get("status") != "scored" for r in dev + held):
        raise SystemExit("Jev rows contain non-scored outputs")

    y_dev = np.asarray([int(r["label"] == "pos") for r in dev], dtype=int)
    y_held = np.asarray([int(r["label"] == "pos") for r in held], dtype=int)
    lic_dev, lic_held = _lic(dev)[:, 0].astype(int), _lic(held)[:, 0].astype(int)
    majority_held = int(y_held.mean() >= 0.5)
    baselines = {
        "majority": {
            "dev_accuracy": float(np.mean(y_dev == int(y_dev.mean() >= 0.5))),
            "held_accuracy": float(np.mean(y_held == majority_held)),
            "held_auc": float(
                roc_auc_score(y_held, np.full(len(y_held), majority_held))
            ),
        },
        "license_regex": {
            "dev_accuracy": float(np.mean(y_dev == lic_dev)),
            "held_accuracy": float(np.mean(y_held == lic_held)),
            "dev_auc": float(roc_auc_score(y_dev, lic_dev)),
            "held_auc": float(roc_auc_score(y_held, lic_held)),
        },
    }

    score_probe, n_features, fit_seconds = fit_probe(dev, held_ids)
    probe = score_probe(held)
    if not np.isfinite(probe).all():
        raise SystemExit("non-finite held scores")
    # The probe's own dev scores are in-sample; its Platt map is fit on out-of-fold dev scores
    # (GroupKFold over dev source groups), so the map sees scores shaped like held scores.
    probe_dev_oof = np.empty(len(dev))
    for train_idx, test_idx in GroupKFold(n_splits=OOF_FOLDS).split(
        dev, y_dev, dev_groups
    ):
        fold_score, _, _ = fit_probe([dev[i] for i in train_idx], held_ids)
        probe_dev_oof[test_idx] = fold_score([dev[i] for i in test_idx])

    jev_held = np.asarray([jev[r["sample_id"]]["noul"] for r in held], dtype=float)
    jev_dev = np.asarray([jev[r["sample_id"]]["noul"] for r in dev], dtype=float)
    clef_held = np.asarray([clef[r["sample_id"]]["noul"] for r in held], dtype=float)
    clef_dev_s = np.asarray(
        [clef_dev[r["sample_id"]]["noul"] for r in dev], dtype=float
    )
    auc_probe, auc_jev, auc_clef = (
        float(roc_auc_score(y_held, s)) for s in (probe, jev_held, clef_held)
    )

    vs_jev, vs_clef = (
        delong_pair(probe, jev_held, y_held),
        delong_pair(probe, clef_held, y_held),
    )
    vs_jev["p_holm"], vs_clef["p_holm"] = holm(
        [vs_jev["p_two_sided"], vs_clef["p_two_sided"]]
    )

    def auc_diff(other: np.ndarray):
        return lambda idx: float(
            roc_auc_score(y_held[idx], probe[idx])
            - roc_auc_score(y_held[idx], other[idx])
        )

    cluster = {
        "probe_minus_jev": {
            "point": auc_probe - auc_jev,
            **cluster_bootstrap(auc_diff(jev_held), y_held, held_groups),
        },
        "probe_minus_clef": {
            "point": auc_probe - auc_clef,
            **cluster_bootstrap(auc_diff(clef_held), y_held, held_groups),
        },
    }
    for entry in cluster.values():
        entry["excludes_zero"] = entry["ci95"][0] > 0 or entry["ci95"][1] < 0

    calibration = {}
    for name, d_scores, h_scores in (
        ("probe", probe_dev_oof, probe),
        ("jev", jev_dev, jev_held),
        ("clef", clef_dev_s, clef_held),
    ):
        a, b = platt_fit(d_scores, y_dev)
        cal = platt_apply(h_scores, a, b)
        calibration[name] = {
            "platt_a": a,
            "platt_b": b,
            "ece_raw": ece(h_scores, y_held),
            "ece_platt": ece(cal, y_held),
            "ece_platt_bootstrap": cluster_bootstrap(
                lambda idx, c=cal: ece(c[idx], y_held[idx]), y_held, held_groups
            ),
        }

    bar = auc_jev - 0.02
    result = {
        "experiment": "x4-vendored-probe",
        "sample_sha256": hashlib.sha256(sample_bytes).hexdigest(),
        "canonical_sample_sha256": canonical_sha,
        "dev_n": len(dev),
        "held_n": len(held),
        "source_groups": {
            "dev": len(set(dev_groups)),
            "held": len(set(held_groups)),
            "overlap": 0,
        },
        "baselines": baselines,
        "model": {
            "vocabulary_features": n_features,
            "auc_held": auc_probe,
            "accuracy_at_0.5": float(np.mean((probe >= 0.5) == y_held)),
            "fit_seconds": fit_seconds,
        },
        "incumbents": {"jev_auc_held": auc_jev, "clef_auc_held": auc_clef},
        "delong": {
            "probe_vs_jev": vs_jev,
            "probe_vs_clef": vs_clef,
            "jev_vs_clef_check": delong_pair(jev_held, clef_held, y_held),
        },
        "cluster_bootstrap_auc": cluster,
        "calibration": calibration,
        "jev_raw_ece_reference": JEV_RAW_ECE_REFERENCE,
        "primary_bar": {"auc_min": bar, "passes": auc_probe >= bar},
        "contract_ece": {
            "probe_platt_le_jev_raw": calibration["probe"]["ece_platt"]
            <= JEV_RAW_ECE_REFERENCE,
            "probe_platt_le_jev_platt": calibration["probe"]["ece_platt"]
            <= calibration["jev"]["ece_platt"],
        },
        "x4b": "NOT_RUN",
        "spend_usd": 0.0,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
