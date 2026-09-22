#!/usr/bin/env python3
"""DIFF analyzer: offline, no key, no network. Reads committed Jev bench +
live LLM rows, emits DIFF-RECEIPT.json. Exit 2 on missing/short arms.
"""

import datetime, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
JEV_SRC = "/Users/josh/Developer/jev/jev-sec-bench/results/injection.json"
BAR_SHA = "3d65229"
BAR_A1_SHA = "b5e6e1e"
ARMS = ["A-xai-grok-4", "B-anthropic-claude-haiku-4-5"]
CUT = 0.5


def wilson_lower(k, n, z=1.96):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round(max(0.0, (c - m) / d), 4)


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p via binomial tail. b=arm-only hits, c=jev-only."""
    n = b + c
    if n == 0:
        return 1.0
    lo = min(b, c)
    p = sum(math.comb(n, k) for k in range(lo + 1)) / 2**n
    p = min(1.0, 2 * p)
    return p if p < 0.000001 else round(p, 7)


def load_rows(arm):
    path = os.path.join(HERE, f"rows-{arm}.jsonl")
    rec_by_id = {}
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            cur = rec_by_id.get(r.get("id"))
            if cur is None or ("error" in cur and "error" not in r):
                rec_by_id[r.get("id")] = r
    return rec_by_id


def main():
    d = json.load(open(JEV_SRC))
    samples = d["samples"]
    assert len(samples) == 662, f"corpus drift: {len(samples)}"
    jev = {}
    for i, s in enumerate(samples):
        rid = f"inj-{i:04d}"
        jev[rid] = {"label": int(s["label"]), "p": float(s["probability"])}

    out = {
        "unit": "differential-llm-vs-jev",
        "date": datetime.date.today().isoformat(),
        "lane": "live",
        "corpus": "jev-sec-bench/results/injection.json @fdb16b9",
        "n": 662,
        "cut": CUT,
        "bar_sha": BAR_SHA,
        "bar_a1_sha": BAR_A1_SHA,
        "jev_arm": {"model": "jev-1.13.0", "lane": "cited-not-remeasured"},
        "arms": {},
    }
    jev_correct = sum(1 for v in jev.values() if (v["p"] >= CUT) == bool(v["label"]))
    out["jev_arm"]["correct"] = jev_correct
    out["jev_arm"]["acc"] = round(jev_correct / 662, 4)

    ok = True
    for arm in ARMS:
        rec = load_rows(arm)
        if len(rec) != 662:
            print(f"[{arm}] SHORT: {len(rec)}/662", flush=True)
            ok = False
            continue
        fails = [rid for rid, r in rec.items() if "error" in r]
        n_ok = 662 - len(fails)
        correct = sum(
            1
            for rid, r in rec.items()
            if "error" not in r and (r["p"] >= CUT) == bool(r["label"])
        )
        tp = sum(
            1
            for rid, r in rec.items()
            if "error" not in r and r["p"] >= CUT and r["label"] == 1
        )
        fp = sum(
            1
            for rid, r in rec.items()
            if "error" not in r and r["p"] >= CUT and r["label"] == 0
        )
        tn = sum(
            1
            for rid, r in rec.items()
            if "error" not in r and r["p"] < CUT and r["label"] == 0
        )
        fn = sum(
            1
            for rid, r in rec.items()
            if "error" not in r and r["p"] < CUT and r["label"] == 1
        )
        in_tok = sum(r.get("in_tokens", 0) for r in rec.values() if "error" not in r)
        out_tok = sum(r.get("out_tokens", 0) for r in rec.values() if "error" not in r)
        lat = [r.get("latency_s", 0) for r in rec.values() if "error" not in r]
        # paired vs Jev on rows both decided
        b = c = 0  # b: arm right + jev wrong; c: jev right + arm wrong
        for rid, v in jev.items():
            r = rec.get(rid)
            if r is None or "error" in r:
                continue
            a_ok = (r["p"] >= CUT) == bool(r["label"])
            j_ok = (v["p"] >= CUT) == bool(v["label"])
            if a_ok and not j_ok:
                b += 1
            elif j_ok and not a_ok:
                c += 1
        acc = correct / n_ok if n_ok else 0.0
        out["arms"][arm] = {
            "n_ok": n_ok,
            "failed_rows": len(fails),
            "correct": correct,
            "acc": round(acc, 4),
            "wilson95_lower": wilson_lower(correct, n_ok),
            "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
            "vs_jev_discordants": {"arm_only": b, "jev_only": c},
            "vs_jev_mcnemar_two_sided_p": mcnemar_exact(b, c),
            "tokens": {"in": in_tok, "out": out_tok},
            "latency_s_mean": round(sum(lat) / len(lat), 3) if lat else 0.0,
        }
        if fails:
            out["arms"][arm]["fail_ids"] = fails
        if len(fails) > 2:
            out["arms"][arm]["verdict"] = "INVALID (>2 failures)"
            ok = False
    # gate 4: seat certified iff jev acc exceeds BOTH arms AND mcnemar p<0.05 vs each
    g4 = True
    for arm in ARMS:
        a = out["arms"].get(arm)
        if not a or a.get("verdict") == "INVALID (>2 failures)":
            g4 = False
            break
        if not (
            out["jev_arm"]["acc"] > a["acc"] and a["vs_jev_mcnemar_two_sided_p"] < 0.05
        ):
            g4 = False
    out["gate4_seat_certified"] = bool(g4)
    out["no_claim"] = (
        "Public corpus, may leak into any model's training. Single run, fixed 0.5 cut. "
        "A win against an LLM is not a certified seat unless gate 4 above is met."
    )
    with open(os.path.join(HERE, "DIFF-RECEIPT.json"), "w") as f:
        f.write(json.dumps(out, indent=2) + "\n")
    print(json.dumps({a: out["arms"].get(a, {}) for a in ARMS}, indent=2)[:2000])
    print("gate4_seat_certified =", g4)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
