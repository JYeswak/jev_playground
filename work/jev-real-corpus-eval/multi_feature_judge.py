#!/usr/bin/env python3
"""Offline multi-feature judge for the frozen toolcall corpus.

Loads work/p3-calibration/toolcall-corpus-frozen.jsonl, prints mean loss vs
always-abstain (0.212210043), and MUST attempt to beat it.

Two judges:
  1. rule-list — always-abstain, then ALLOW only on train-estimated P(GOOD)>2/3
     exact-session / high-precision token rules (loss math requires p>2/3).
  2. logistic — L2 logistic on mined features; allow iff P(GOOD)>thr, thr
     chosen on train to minimize mean loss.

5-fold CV: fit on train only, report mean test loss. No invented cases.

    python3 work/jev-real-corpus-eval/multi_feature_judge.py \
      work/p3-calibration/toolcall-corpus-frozen.jsonl
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jev_real_corpus_eval import (  # noqa: E402
    FROZEN_BAD,
    FROZEN_GOOD,
    FROZEN_N,
    FROZEN_SHA256,
    STUDIO_ABSTAIN,
    identity_lock,
    load_rows,
    loss,
)

ALLOW_PREC = 2.0 / 3.0  # allow only if P(GOOD|rule) > this


def cmd_of(row: dict) -> str:
    raw = row.get("args") or ""
    try:
        a = json.loads(raw)
        return a.get("command") or a.get("code") or ""
    except Exception:
        return raw


def sess_repo(sess: str) -> str:
    if not sess:
        return ""
    if sess.startswith("-Developer-"):
        return "-Developer-" + sess[len("-Developer-") :].split("/")[0]
    if sess.startswith("--"):
        return sess.split("/")[0]
    return sess.split("/")[0]


def mean_loss_picks(rows: list[dict], picks: list[str]) -> tuple[float, int, int, int]:
    total = 0
    tp = fp = fn = 0
    for r, p in zip(rows, picks):
        total += loss(r["outcome"], p)
        if p == "allow":
            if r["outcome"] == "GOOD":
                tp += 1
            else:
                fp += 1
        elif r["outcome"] == "GOOD":
            fn += 1
    return total / len(rows), tp, fp, fn


# ---------- rule-list judge ----------

def rule_keys(row: dict) -> list[str]:
    """Atomic rule keys that can fire an allow (if train P>2/3)."""
    s = row.get("sess") or ""
    c = cmd_of(row).lower()
    keys = [f"sess={s}"]
    # token rules with historically high precision
    for tok in ("pipefail", "mcp", "skills", "curl"):
        if re.search(rf"(^|[^a-z0-9]){re.escape(tok)}([^a-z0-9]|$)", c) or tok in c:
            keys.append(f"tok={tok}")
            keys.append(f"repo_tok={sess_repo(s)}|{tok}")
    return keys


def fit_rule_allow_set(train: list[dict], min_n: int = 15) -> set[str]:
    """Return rule keys whose train P(GOOD) > 2/3 and n>=min_n."""
    cg: Counter[str] = Counter()
    cn: Counter[str] = Counter()
    for r in train:
        seen = set(rule_keys(r))
        for k in seen:
            cn[k] += 1
            if r["outcome"] == "GOOD":
                cg[k] += 1
    allow: set[str] = set()
    for k, c in cn.items():
        if c < min_n:
            continue
        if cg[k] / c > ALLOW_PREC:
            allow.add(k)
    return allow


def rule_pick(row: dict, allow_keys: set[str]) -> str:
    if row.get("isError") is True:
        return "abstain"  # never allow errors (also all BAD in frozen)
    for k in rule_keys(row):
        if k in allow_keys:
            return "allow"
    return "abstain"


# ---------- logistic judge ----------

FEATURE_NAMES = [
    "bias",
    "isError",
    "args_len_n",
    "cmd_len_n",
    "has_pipe",
    "has_and",
    "has_dollar",
    "has_Users",
    "tok_pipefail",
    "tok_skills",
    "tok_mcp",
    "tok_set",
    "tok_curl",
    "tok_franken",
    "tok_gb",
    "tok_templates",
    "tok_wc",
    "tok_cut",
    "tok_timeout",
    "tok_null",
    "tok_dev",
    "tok_ls",
    "tok_git",
    "tok_cargo",
    "tok_ntm",
    "tok_omp",
    "tok_python",
    "tok_echo",
    "tok_sed",
    "tok_grep",
    "tok_jq",
    "tok_find",
    "repo_grokbot",
    "repo_control_plane",
    "repo_omp",
    "repo_franken",
    "repo_jev",
    "repo_WWJD",
    "repo_cfs",
    "repo_private",
]


def feat_vec(row: dict) -> np.ndarray:
    c = cmd_of(row)
    cl = c.lower()
    s = row.get("sess") or ""
    repo = sess_repo(s)
    d = {
        "bias": 1.0,
        "isError": 1.0 if row.get("isError") else 0.0,
        "args_len_n": len(row.get("args") or "") / 200.0,
        "cmd_len_n": min(len(c), 300) / 300.0,
        "has_pipe": 1.0 if "|" in c else 0.0,
        "has_and": 1.0 if "&&" in c else 0.0,
        "has_dollar": 1.0 if "$" in c else 0.0,
        "has_Users": 1.0 if "/Users/" in c else 0.0,
        "tok_pipefail": 1.0 if "pipefail" in cl else 0.0,
        "tok_skills": 1.0 if "skills" in cl else 0.0,
        "tok_mcp": 1.0 if re.search(r"\bmcp\b", cl) else 0.0,
        "tok_set": 1.0 if re.search(r"\bset\b", cl) else 0.0,
        "tok_curl": 1.0 if re.search(r"\bcurl\b", cl) else 0.0,
        "tok_franken": 1.0 if "franken-harvest" in cl else 0.0,
        "tok_gb": 1.0 if re.search(r"\bgb\b", cl) else 0.0,
        "tok_templates": 1.0 if "templates" in cl else 0.0,
        "tok_wc": 1.0 if re.search(r"\bwc\b", cl) else 0.0,
        "tok_cut": 1.0 if re.search(r"\bcut\b", cl) else 0.0,
        "tok_timeout": 1.0 if "timeout" in cl else 0.0,
        "tok_null": 1.0 if "null" in cl else 0.0,
        "tok_dev": 1.0 if re.search(r"\bdev\b", cl) else 0.0,
        "tok_ls": 1.0 if re.search(r"(^|[|&;]\s*)ls\b", c) else 0.0,
        "tok_git": 1.0 if re.search(r"\bgit\b", cl) else 0.0,
        "tok_cargo": 1.0 if re.search(r"\bcargo\b", cl) else 0.0,
        "tok_ntm": 1.0 if re.search(r"\bntm\b", cl) else 0.0,
        "tok_omp": 1.0 if re.search(r"\bomp\b", cl) else 0.0,
        "tok_python": 1.0 if re.search(r"\bpython3?\b", cl) else 0.0,
        "tok_echo": 1.0 if re.search(r"\becho\b", cl) else 0.0,
        "tok_sed": 1.0 if re.search(r"\bsed\b", cl) else 0.0,
        "tok_grep": 1.0 if re.search(r"\bgrep\b", cl) else 0.0,
        "tok_jq": 1.0 if re.search(r"\bjq\b", cl) else 0.0,
        "tok_find": 1.0 if re.search(r"\bfind\b", cl) else 0.0,
        "repo_grokbot": 1.0 if repo == "-Developer-grokbot" else 0.0,
        "repo_control_plane": 1.0 if repo == "-Developer-control-plane" else 0.0,
        "repo_omp": 1.0 if repo == "-Developer-omp-orchestrator" else 0.0,
        "repo_franken": 1.0 if "franken" in repo else 0.0,
        "repo_jev": 1.0 if repo == "-Developer-jev" else 0.0,
        "repo_WWJD": 1.0 if repo == "-Developer-WWJD" else 0.0,
        "repo_cfs": 1.0 if "clutterfreespaces" in repo else 0.0,
        "repo_private": 1.0 if repo.startswith("--private") else 0.0,
    }
    # sess hash buckets (captures exact-session concentration without listing IDs)
    h = int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
    vec = [d[name] for name in FEATURE_NAMES]
    for b in range(16):
        vec.append(1.0 if (h % 16) == b else 0.0)
    return np.asarray(vec, dtype=float)


def build_X(rows: list[dict]) -> np.ndarray:
    return np.vstack([feat_vec(r) for r in rows])


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def fit_logistic(X: np.ndarray, y: np.ndarray, l2: float = 2.0, steps: int = 500, lr: float = 0.8) -> np.ndarray:
    w = np.zeros(X.shape[1])
    n = len(y)
    for _ in range(steps):
        p = sigmoid(X @ w)
        grad = X.T @ (p - y) / n + (l2 / n) * w
        grad[0] = (X[:, 0] * (p - y)).sum() / n  # no L2 on bias
        w -= lr * grad
    return w


def logistic_picks(w: np.ndarray, X: np.ndarray, thr: float) -> list[str]:
    p = sigmoid(X @ w)
    return ["allow" if pi > thr else "abstain" for pi in p]


def choose_thr(w: np.ndarray, X: np.ndarray, rows: list[dict]) -> float:
    best_thr, best_ml = 0.67, 1e9
    for thr in np.linspace(0.50, 0.95, 19):
        picks = logistic_picks(w, X, float(thr))
        ml, _, _, _ = mean_loss_picks(rows, picks)
        if ml < best_ml:
            best_ml, best_thr = ml, float(thr)
    return best_thr


def kfold_indices(n: int, k: int = 5, seed: int = 42) -> list[tuple[np.ndarray, np.ndarray]]:
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    folds = np.array_split(idx, k)
    out = []
    for i in range(k):
        te = folds[i]
        tr = np.concatenate([folds[j] for j in range(k) if j != i])
        out.append((tr, te))
    return out


def fmt(x: float) -> str:
    return f"{x:.9f}"


def main(argv: list[str]) -> int:
    path = Path(argv[0] if argv else "work/p3-calibration/toolcall-corpus-frozen.jsonl")
    rows = load_rows(path)
    identity_lock(path, rows)
    n = len(rows)
    good = sum(1 for r in rows if r["outcome"] == "GOOD")
    y = np.array([1.0 if r["outcome"] == "GOOD" else 0.0 for r in rows])
    abstain_ml = good / n

    print(f"FROZEN  sha256={FROZEN_SHA256}")
    print(f"n={n}  GOOD={good}  BAD={n - good}  prevalence={fmt(abstain_ml)}")
    print(f"CONTROL always-abstain  mean_loss={fmt(abstain_ml)} (want {STUDIO_ABSTAIN})")
    print(
        "LOSS math: allow saves 1 on GOOD / costs 2 on BAD → need P(GOOD|allow)>2/3 "
        "to beat always-abstain under class imbalance (GOOD=21.2%)."
    )
    print()

    # ---- full-data rule-list ----
    allow_keys = fit_rule_allow_set(rows, min_n=15)
    rule_picks = [rule_pick(r, allow_keys) for r in rows]
    r_ml, r_tp, r_fp, r_fn = mean_loss_picks(rows, rule_picks)
    print(
        f"JUDGE rule-list (full)  mean_loss={fmt(r_ml)}  allows={r_tp + r_fp}  "
        f"tp={r_tp} fp={r_fp} fn={r_fn}  allow_keys={len(allow_keys)}  "
        f"vs_control={'BEAT' if r_ml < abstain_ml else 'MISS'}"
    )
    # show top allow keys
    top = sorted(allow_keys, key=lambda k: (0 if k.startswith("sess=") else 1, k))[:12]
    print(f"  sample allow_keys: {top}")

    # ---- full-data logistic ----
    X = build_X(rows)
    w = fit_logistic(X, y)
    thr = choose_thr(w, X, rows)
    log_picks = logistic_picks(w, X, thr)
    l_ml, l_tp, l_fp, l_fn = mean_loss_picks(rows, log_picks)
    print(
        f"JUDGE logistic (full)   mean_loss={fmt(l_ml)}  thr={thr:.2f}  allows={l_tp + l_fp}  "
        f"tp={l_tp} fp={l_fp} fn={l_fn}  "
        f"vs_control={'BEAT' if l_ml < abstain_ml else 'MISS'}"
    )

    # ---- 5-fold CV ----
    print()
    print("5-fold CV (fit + thr/keys on train only; eval on held-out rows):")
    rule_cv = []
    log_cv = []
    for fi, (tr_i, te_i) in enumerate(kfold_indices(n, 5, 42)):
        tr = [rows[i] for i in tr_i]
        te = [rows[i] for i in te_i]
        # rules
        keys = fit_rule_allow_set(tr, min_n=15)
        rp = [rule_pick(r, keys) for r in te]
        rml, rtp, rfp, _ = mean_loss_picks(te, rp)
        rule_cv.append(rml)
        # logistic
        Xtr, Xte = X[tr_i], X[te_i]
        ytr = y[tr_i]
        ww = fit_logistic(Xtr, ytr)
        tthr = choose_thr(ww, Xtr, tr)
        lp = logistic_picks(ww, Xte, tthr)
        lml, ltp, lfp, _ = mean_loss_picks(te, lp)
        log_cv.append(lml)
        print(
            f"  fold{fi}  rule_loss={fmt(rml)} (allow={rtp + rfp} tp={rtp} fp={rfp} keys={len(keys)})  "
            f"log_loss={fmt(lml)} thr={tthr:.2f} (allow={ltp + lfp} tp={ltp} fp={lfp})"
        )

    rule_cv_m = float(np.mean(rule_cv))
    log_cv_m = float(np.mean(log_cv))
    best_cv = min(rule_cv_m, log_cv_m)
    best_name = "rule-list" if rule_cv_m <= log_cv_m else "logistic"
    print()
    print(f"CV rule-list mean_loss={fmt(rule_cv_m)}  vs_control={'BEAT' if rule_cv_m < abstain_ml else 'MISS'}")
    print(f"CV logistic  mean_loss={fmt(log_cv_m)}  vs_control={'BEAT' if log_cv_m < abstain_ml else 'MISS'}")
    print(
        f"BEST  judge={best_name}  cv_mean_loss={fmt(best_cv)}  "
        f"full_rule={fmt(r_ml)}  full_logistic={fmt(l_ml)}  "
        f"always_abstain={fmt(abstain_ml)}  "
        f"RESULT={'BEAT 0.212' if best_cv < abstain_ml else 'MISS 0.212'}"
    )
    print(
        "NO-CLAIM  [pending] promoted=0  offline  no TYPESAFE  no CASS  "
        "features mined from frozen JSONL only"
    )
    print("EXIT  0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
