#!/usr/bin/env python3
"""Score the jev_claim_check dogfood (bead jev-sp5). No key, no network, stdlib only.

Reads cases.jsonl (labels, committed before any call) and rows.jsonl (the tool's answers).
The last row per case id wins. A case with no supported/unsupported/unsure verdict counts
against the tool: not supported when true, not caught when planted, and p = 0.5 in the AUC.

Bar (docs/demos/upstream-repro/jev-claim-check-20260924.md, frozen before the first call):
  (a) planted false claims called supported <= 1
  (b) catch-rate: planted false claims called unsupported >= 14 of 19
  (c) supported-rate: true claims called supported >= 12 of 19
  (d) AUC of p, true vs planted, >= 0.80
  PASS = all four. Both constants fail: always-supported fails (a) and (b), always-unsupported
  fails (c), and both have AUC 0.5.

Run: python3 work/jev-claim-check/score.py        (exit 0 PASS, 1 FAIL, 2 no rows)
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = ("supported", "unsupported", "unsure")
BAR = {
    "planted_supported_max": 1,
    "catch_min": 14,
    "supported_min": 12,
    "auc_min": 0.80,
}


def auc(pos, neg):
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def main():
    cases = [
        json.loads(line)
        for line in open(os.path.join(HERE, "cases.jsonl"), encoding="utf-8")
    ]
    path = os.path.join(HERE, "rows.jsonl")
    if not os.path.exists(path):
        print("no rows.jsonl: nothing scored")
        return 2
    last = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            last[r["id"]] = r
    trues = [c for c in cases if c["truth"]]
    plants = [c for c in cases if not c["truth"]]

    def verdict(c):
        r = last.get(c["id"])
        return r["verdict"] if r and r["verdict"] in VERDICTS else "no-verdict"

    def prob(c):
        r = last.get(c["id"])
        return r["probability"] if r and r["verdict"] in VERDICTS else 0.5

    tv = [verdict(c) for c in trues]
    pv = [verdict(c) for c in plants]
    supported = tv.count("supported")
    caught = pv.count("unsupported")
    planted_supported = pv.count("supported")
    a = auc([prob(c) for c in trues], [prob(c) for c in plants])
    n = len(trues)

    print(
        f"cases {len(cases)} ({n} true, {len(plants)} planted); rows answered {sum(v in VERDICTS for v in tv + pv)}/{len(cases)}"
    )
    print("| Set | supported | unsure | unsupported | no verdict |")
    print("|---|---:|---:|---:|---:|")
    for name, vs in (("true README claims", tv), ("planted false", pv)):
        print(
            f"| {name} | {vs.count('supported')} | {vs.count('unsure')} | {vs.count('unsupported')} | {vs.count('no-verdict')} |"
        )
    for kind in ("number", "verdict"):
        ks = [verdict(c) for c in plants if c["kind"] == kind]
        print(
            f"planted kind={kind}: caught {ks.count('unsupported')}/{len(ks)}, unsure {ks.count('unsure')}, supported {ks.count('supported')}"
        )
    print()
    print("| Metric | Tool | always supported | always unsupported | Bar |")
    print("|---|---:|---:|---:|---|")
    print(
        f"| supported-rate (true) | {supported}/{n} | {n}/{n} | 0/{n} | >= {BAR['supported_min']} |"
    )
    print(
        f"| catch-rate (planted) | {caught}/{len(plants)} | 0/{len(plants)} | {len(plants)}/{len(plants)} | >= {BAR['catch_min']} |"
    )
    print(
        f"| planted called supported | {planted_supported}/{len(plants)} | {len(plants)}/{len(plants)} | 0/{len(plants)} | <= {BAR['planted_supported_max']} |"
    )
    print(f"| AUC of p | {a:.3f} | 0.500 | 0.500 | >= {BAR['auc_min']:.2f} |")
    print()
    print("| id | truth | verdict | p |")
    print("|---|---|---|---:|")
    for c in trues + plants:
        r = last.get(c["id"])
        p = r["probability"] if r and r["verdict"] in VERDICTS else None
        print(
            f"| {c['id']} | {c['truth']} | {verdict(c)} | {'-' if p is None else f'{p:.2f}'} |"
        )
    passed = (
        planted_supported <= BAR["planted_supported_max"]
        and caught >= BAR["catch_min"]
        and supported >= BAR["supported_min"]
        and a >= BAR["auc_min"]
    )
    print()
    print(
        f"(a) planted supported {planted_supported} <= {BAR['planted_supported_max']}: {'yes' if planted_supported <= BAR['planted_supported_max'] else 'NO'}"
    )
    print(
        f"(b) caught {caught} >= {BAR['catch_min']}: {'yes' if caught >= BAR['catch_min'] else 'NO'}"
    )
    print(
        f"(c) supported {supported} >= {BAR['supported_min']}: {'yes' if supported >= BAR['supported_min'] else 'NO'}"
    )
    print(
        f"(d) AUC {a:.3f} >= {BAR['auc_min']:.2f}: {'yes' if a >= BAR['auc_min'] else 'NO'}"
    )
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
