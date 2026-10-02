#!/usr/bin/env python3
"""Calibration across committed Jev rows (jev-2zbl): reliability, Brier, ECE, AUC,
dev-fitted cut + isotonic/Platt evaluated on held-out. Keyless. Seed 20261002."""

import json
import math
import random

SEED = 20261002
D = "/Users/josh/Developer/jev/"
S = "/Users/josh/.local/state/jev/memory-filter-full.jsonl"


def split(pairs, presplit=None, seed=SEED):
    if presplit:
        return pairs[: presplit[0]], pairs[presplit[0] :]
    rng = random.Random(seed)
    idx = list(range(len(pairs)))
    rng.shuffle(idx)
    half = len(idx) // 2
    return [pairs[i] for i in idx[:half]], [pairs[i] for i in idx[half:]]


def choice_pairs(path, default):
    out = []
    for ln in open(D + path, errors="ignore"):
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if (
            r.get("ok") is False
            or r.get("valid") is False
            or r.get("status") == "error"
        ):
            continue
        ch = r.get("choice")
        cf = r.get("conf", r.get("confidence", 0)) or 0
        lab = r.get("label")
        if ch is None or lab is None:
            continue
        out.append((cf if ch == default else 1 - cf, 1 if lab == default else 0))
    return out


def load():
    tasks = {}
    ms = [
        json.loads(l) for l in open(D + "work/jev-msax/retry-rows.jsonl") if l.strip()
    ]
    tasks["msax-v1"] = {
        "type": "prob",
        "pairs": [(r["v1_noul"], r["label"]) for r in ms if r.get("v1_ok", True)],
        "bar": ("acc>=0.70", 0.70),
    }
    side = {}
    for ln in open(S, errors="ignore"):
        try:
            o = json.loads(ln)
        except Exception:
            continue
        side[(o.get("ts"), o.get("memoryHash"))] = o.get("noul")
    lab = json.load(open(D + "work/jev-m959/labels.json"))
    pairs = []
    for x in lab:
        n = side.get((x["ref"][0], x["ref"][1]))
        if isinstance(n, (int, float)):
            pairs.append((n, 1 if x["label"] == "relevant" else 0))
    tasks["m959-noul"] = {
        "type": "prob",
        "pairs": pairs,
        "bar": ("keep-prec>=0.42", None),
    }
    ws = [
        json.loads(l)
        for l in open(D + "work/hermes-webscreen-repro/rows.jsonl")
        if l.strip()
    ]
    wdev, wheld = [], []
    srcs = sorted({r.get("source_sha") for r in ws})
    heldsrc = set(srcs[len(srcs) // 2 :])
    for r in ws:
        sc = r.get("scores") or {}
        mx = max([float(v) for v in sc.values()], default=0.0)
        (wheld if r.get("source_sha") in heldsrc else wdev).append(
            (mx, 1 if r.get("attack") else 0)
        )
    tasks["webscreen-rowmax"] = {
        "type": "prob",
        "pairs": wdev + wheld,
        "presplit": (len(wdev), len(wheld)),
        "bar": ("catch", None),
    }
    tasks["d1-read"] = {
        "type": "choice",
        "pairs": choice_pairs("work/jev-r524/d1-rows.jsonl", "read"),
        "bar": ("acc>=0.60", 0.60),
    }
    tasks["triage-ignore"] = {
        "type": "choice",
        "pairs": choice_pairs(
            "var/agent-tmp/triage-6c8n.34880/receipt.jsonl", "ignore"
        ),
        "bar": ("acc>=0.75", 0.75),
    }
    tasks["ztfe-ignore"] = {
        "type": "choice",
        "pairs": choice_pairs(
            "var/agent-tmp/ztfe-feas.34880/zt_receipt.jsonl", "ignore"
        ),
        "bar": ("acc>=0.75", 0.75),
    }
    tasks["v10-inapplicable"] = {
        "type": "choice",
        "pairs": choice_pairs(
            "var/agent-tmp/dr4p-feas.34880/live_receipt.jsonl", "inapplicable"
        ),
        "bar": ("harm0", None),
    }
    return tasks


def brier(pairs):
    n = len(pairs)
    return sum((p - y) ** 2 for p, y in pairs) / n if n else None


def ece(pairs, bins=10):
    n = len(pairs)
    if not n:
        return None
    e = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        cell = [
            (p, y)
            for p, y in pairs
            if p >= lo and (p < hi or (b == bins - 1 and p <= hi))
        ]
        if cell:
            e += (
                len(cell)
                / n
                * abs(
                    sum(p for p, _ in cell) / len(cell)
                    - sum(y for _, y in cell) / len(cell)
                )
            )
    return e


def auc(pairs):
    pos = [p for p, y in pairs if y == 1]
    neg = [p for p, y in pairs if y == 0]
    if not pos or not neg:
        return None
    wins = sum(1 for p in pos for q in neg if p > q) + 0.5 * sum(
        1 for p in pos for q in neg if p == q
    )
    return wins / (len(pos) * len(neg))


def best_cut(dev):
    best, best_acc = 0.5, -1.0
    for i in range(5, 100, 5):
        c = i / 100
        acc = sum(((p >= c) == bool(y)) for p, y in dev) / len(dev)
        if acc > best_acc:
            best, best_acc = c, acc
    return best


def isotonic_fit(dev):
    xs = sorted(dev)
    out = []
    for p, y in xs:
        out.append([p, float(y), 1])
        while len(out) >= 2 and out[-2][1] / out[-2][2] > out[-1][1] / out[-1][2]:
            b = out.pop()
            a = out.pop()
            out.append([a[0], a[1] + b[1], a[2] + b[2]])
    pts = [(b[0], b[1] / b[2]) for b in out]

    def f(p):
        cand = [v for x, v in pts if x <= p]
        return cand[-1] if cand else pts[0][1]

    return f


def platt_fit(dev):
    best, best_ll = (1.0, 0.0), 1e18
    for ai in range(-10, 21):
        for bi in range(-10, 11):
            a, b = ai / 2, bi / 2
            ll = 0.0
            for p, y in dev:
                q = 1 / (1 + math.exp(-(a * p + b)))
                q = min(0.999, max(0.001, q))
                ll -= y * math.log(q) + (1 - y) * math.log(1 - q)
            if ll < best_ll:
                best, best_ll = (a, b), ll
    a, b = best
    return lambda p: 1 / (1 + math.exp(-(a * p + b)))


def main():
    tasks = load()
    report = {}
    for name, t in tasks.items():
        pairs = t["pairs"]
        dev, held = split(pairs, t.get("presplit"))
        n_pos = sum(y for _, y in pairs)
        full = {
            "n": len(pairs),
            "base_rate": n_pos / len(pairs) if pairs else None,
            "brier": brier(pairs),
            "ece": ece(pairs),
            "auc": auc(pairs),
            "mean_p": sum(p for p, _ in pairs) / len(pairs) if pairs else None,
        }
        cut = best_cut(dev) if dev else 0.5
        iso = isotonic_fit(dev) if dev else None
        pla = platt_fit(dev) if dev else None
        hres = {}
        if held:
            pred = [1 if p >= cut else 0 for p, _ in held]
            hy = [y for _, y in held]
            hres = {
                "n": len(held),
                "cut": cut,
                "acc_cut": sum(a == b for a, b in zip(pred, hy)) / len(held),
                "brier_raw": brier(held),
                "brier_iso": sum((iso(p) - y) ** 2 for p, y in held) / len(held),
                "brier_platt": sum((pla(p) - y) ** 2 for p, y in held) / len(held),
                "auc_raw": auc(held),
                "auc_iso": auc([(iso(p), y) for p, y in held]),
                "auc_platt": auc([(pla(p), y) for p, y in held]),
            }
        report[name] = {"full": full, "held": hres, "bar": t["bar"]}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
