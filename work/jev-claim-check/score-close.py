#!/usr/bin/env python3
"""Score the close-reason dogfood (bead jev-10t). No key, no network, stdlib only.

Reads close-cases.jsonl (real close reasons and planted twins, committed before any call) and
close-rows.jsonl (the tool's answers; the last row per id wins). A case with no evidence is not
sent and sits outside every denominator (counted). A case with evidence but no verdict counts
against the tool: not caught when planted, not supported when real, p = 0.5 in AUC and pairing.

Bar (docs/demos/upstream-repro/close-reason-check-20260924.md, frozen before the first call):
  (a) planted reasons called supported <= 10% of scored plants (floor)
  (b) catch-rate: planted reasons called unsupported >= 50% of scored plants (ceil)
  (c) AUC of p, real vs planted, >= 0.70
  (d) paired: on beads with both, p(planted) < p(real) on >= 60% (ceil); a tie is not lower
  PASS = all four. The real supported-rate carries no bar: a real reason is not known to be true,
  and one the tool calls unsupported is read, not assumed wrong. Constants: always-supported fails
  (a) and (b); always-unsupported passes (a) and (b) but has AUC 0.5 and 0 paired wins.

Run: python3 work/jev-claim-check/score-close.py   (exit 0 PASS, 1 FAIL, 2 no rows)
"""

import json
import math
import os
import sys

from score import VERDICTS, auc

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    cases = [
        json.loads(line)
        for line in open(os.path.join(HERE, "close-cases.jsonl"), encoding="utf-8")
    ]
    path = os.path.join(HERE, "close-rows.jsonl")
    if not os.path.exists(path):
        print("no close-rows.jsonl: nothing scored")
        return 2
    last = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            last[r["id"]] = r

    def verdict(c):
        r = last.get(c["id"])
        return r["verdict"] if r and r["verdict"] in VERDICTS else "no-verdict"

    def prob(c):
        r = last.get(c["id"])
        return r["probability"] if r and r["verdict"] in VERDICTS else 0.5

    scored = [c for c in cases if c["evidence"]]
    no_ev = [c["id"] for c in cases if not c["evidence"]]
    reals = [c for c in scored if c["truth"]]
    plants = [c for c in scored if not c["truth"]]
    rv = [verdict(c) for c in reals]
    pv = [verdict(c) for c in plants]
    n_p = len(plants)
    caught = pv.count("unsupported")
    planted_supported = pv.count("supported")
    a = auc([prob(c) for c in reals], [prob(c) for c in plants])
    real_by_bead = {c["bead"]: c for c in reals}
    pairs = [(real_by_bead[c["bead"]], c) for c in plants if c["bead"] in real_by_bead]
    wins = sum(prob(p) < prob(r) for r, p in pairs)
    bar = {
        "planted_supported_max": math.floor(0.10 * n_p),
        "catch_min": math.ceil(0.50 * n_p),
        "auc_min": 0.70,
        "paired_min": math.ceil(0.60 * len(pairs)),
    }

    print(
        f"cases {len(cases)}; without evidence (not sent) {len(no_ev)}: {' '.join(no_ev) or '-'}"
    )
    print(
        f"scored: {len(reals)} real, {n_p} planted, {len(pairs)} pairs; answered {sum(v in VERDICTS for v in rv + pv)}/{len(reals) + n_p}"
    )
    print("| Set | supported | unsure | unsupported | no verdict |")
    print("|---|---:|---:|---:|---:|")
    for name, vs in (("real close reasons", rv), ("planted (one number changed)", pv)):
        print(
            f"| {name} | {vs.count('supported')} | {vs.count('unsure')} | {vs.count('unsupported')} | {vs.count('no-verdict')} |"
        )
    for flag in (True, False):
        ks = [verdict(c) for c in plants if c["plant"]["inEvidence"] is flag]
        print(
            f"plants whose original number is {'in' if flag else 'NOT in'} the evidence: caught {ks.count('unsupported')}/{len(ks)}, unsure {ks.count('unsure')}, supported {ks.count('supported')}"
        )
    print()
    print("| Metric | Tool | always supported | always unsupported | Bar |")
    print("|---|---:|---:|---:|---|")
    print(
        f"| (a) planted called supported | {planted_supported}/{n_p} | {n_p}/{n_p} | 0/{n_p} | <= {bar['planted_supported_max']} |"
    )
    print(
        f"| (b) catch-rate | {caught}/{n_p} | 0/{n_p} | {n_p}/{n_p} | >= {bar['catch_min']} |"
    )
    print(
        f"| (c) AUC real vs planted | {a:.3f} | 0.500 | 0.500 | >= {bar['auc_min']:.2f} |"
    )
    print(
        f"| (d) paired p(planted) < p(real) | {wins}/{len(pairs)} | 0/{len(pairs)} | 0/{len(pairs)} | >= {bar['paired_min']} |"
    )
    print(
        f"| real supported-rate (no bar) | {rv.count('supported')}/{len(reals)} | {len(reals)}/{len(reals)} | 0/{len(reals)} | - |"
    )
    print()
    print("| bead | real verdict | real p | planted | plant verdict | plant p |")
    print("|---|---|---:|---|---|---:|")
    plant_by_bead = {c["bead"]: c for c in plants}
    for r in reals:
        p = plant_by_bead.get(r["bead"])
        pp = "-" if not p or verdict(p) not in VERDICTS else f"{prob(p):.2f}"
        rp = "-" if verdict(r) not in VERDICTS else f"{prob(r):.2f}"
        change = f"{p['plant']['from']} -> {p['plant']['to']}" if p else "no plant"
        print(
            f"| {r['bead']} | {verdict(r)} | {rp} | {change} | {verdict(p) if p else '-'} | {pp} |"
        )
    checks = [
        ("(a)", planted_supported <= bar["planted_supported_max"]),
        ("(b)", caught >= bar["catch_min"]),
        ("(c)", a >= bar["auc_min"]),
        ("(d)", wins >= bar["paired_min"]),
    ]
    print()
    for name, ok in checks:
        print(f"{name} {'yes' if ok else 'NO'}")
    passed = all(ok for _, ok in checks)
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
