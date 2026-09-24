#!/usr/bin/env python3
"""Score the numeric-exact claim check (bead jev-2mp, the R83 retry). No key, stdlib only.

Reads numeric-cases.jsonl (claims, per-number checks and fresh plants, committed before any call)
and numeric-rows.jsonl (one row per distinct check; the last verdict-bearing row per check wins).
A check is keyed by set, claim key, clause and value, so a planted claim's unchanged checks share
the real claim's answer. A check with no verdict counts as unsure.

Bar (docs/demos/upstream-repro/claim-check-numeric-20260924.md, frozen before the first call), in
EACH set (readme, close), over its n plants:
  (a) the planted number's check called supported <= 10% of n (floor)
  (b) the planted number's check called unsupported >= 60% of n (ceil)
  (c) the ORIGINAL number's check, same position in the real claim, called supported >= 60% of n
  PASS = (a), (b) and (c) in both sets. Always-supported fails (a) and (b); always-unsupported fails (c).
Descriptive: whole-claim verdicts for real and planted claims, and every real claim called
unsupported as a whole, with the check(s) that sank it.

Run: python3 work/jev-claim-check/score-numeric.py   (exit 0 PASS, 1 FAIL, 2 no rows)
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = ("supported", "unsupported", "unsure")


def key(case, clause, value):
    return "\x00".join((case["set"], case["key"], clause, value))


def main():
    cases = [
        json.loads(line)
        for line in open(os.path.join(HERE, "numeric-cases.jsonl"), encoding="utf-8")
    ]
    path = os.path.join(HERE, "numeric-rows.jsonl")
    if not os.path.exists(path):
        print("no numeric-rows.jsonl: nothing scored")
        return 2
    rows = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            if r["verdict"] in VERDICTS or r["check"] not in rows:
                rows[r["check"]] = r

    def check(case, clause, value):
        r = rows.get(key(case, clause, value))
        return (
            (r["verdict"], r["probability"])
            if r and r["verdict"] in VERDICTS
            else ("unsure", None)
        )

    def whole(case):
        vs = [check(case, k["clause"], k["value"])[0] for k in case["checks"]]
        if not vs:
            return "no-number"
        if all(v == "supported" for v in vs):
            return "supported"
        return "unsupported" if "unsupported" in vs else "unsure"

    answered = sum(1 for r in rows.values() if r["verdict"] in VERDICTS)
    print(f"distinct checks answered: {answered}/{len(rows)} rows on file")
    passed = True
    for s in ("readme", "close"):
        cs = [c for c in cases if c["set"] == s]
        reals = {c["key"]: c for c in cs if c["truth"]}
        plants = [c for c in cs if not c["truth"]]
        n = len(plants)
        pv, rv = [], []
        for p in plants:
            pl = p["plant"]
            pv.append(check(p, pl["plantedClause"], pl["to"]))
            rv.append(check(reals[p["key"]], pl["realClause"], pl["from"]))
        wrong = sum(v == "supported" for v, _ in pv)
        caught = sum(v == "unsupported" for v, _ in pv)
        hit = sum(v == "supported" for v, _ in rv)
        bar = {
            "wrong_max": math.floor(0.10 * n),
            "caught_min": math.ceil(0.60 * n),
            "hit_min": math.ceil(0.60 * n),
        }
        ok = (
            wrong <= bar["wrong_max"]
            and caught >= bar["caught_min"]
            and hit >= bar["hit_min"]
        )
        passed = passed and ok
        print(f"\n## set {s}: {len(reals)} real claims, {n} plants")
        print("| Metric | Tool | always supported | always unsupported | Bar | Met |")
        print("|---|---:|---:|---:|---|---|")
        print(
            f"| (a) planted number called supported | {wrong}/{n} | {n}/{n} | 0/{n} | <= {bar['wrong_max']} | {'yes' if wrong <= bar['wrong_max'] else 'NO'} |"
        )
        print(
            f"| (b) planted number called unsupported | {caught}/{n} | 0/{n} | {n}/{n} | >= {bar['caught_min']} | {'yes' if caught >= bar['caught_min'] else 'NO'} |"
        )
        print(
            f"| (c) original number called supported | {hit}/{n} | {n}/{n} | 0/{n} | >= {bar['hit_min']} | {'yes' if hit >= bar['hit_min'] else 'NO'} |"
        )
        for flag in (True, False):
            sub = [
                (pvv, rvv)
                for p, pvv, rvv in zip(plants, pv, rv)
                if p["plant"]["inEvidence"] is flag
            ]
            if sub:
                print(
                    f"plants with original {'in' if flag else 'NOT in'} evidence: {len(sub)}; planted caught {sum(a[0] == 'unsupported' for a, _ in sub)}, planted supported {sum(a[0] == 'supported' for a, _ in sub)}, original supported {sum(b[0] == 'supported' for _, b in sub)}"
                )
        wr = [whole(c) for c in reals.values()]
        wp = [whole(c) for c in plants]
        print(
            f"whole claim, real: supported {wr.count('supported')}, unsure {wr.count('unsure')}, unsupported {wr.count('unsupported')}, no number {wr.count('no-number')}"
        )
        print(
            f"whole claim, planted: supported {wp.count('supported')}, unsure {wp.count('unsure')}, unsupported {wp.count('unsupported')}"
        )
        print(
            "\n| key | original -> planted | original verdict (p) | planted verdict (p) |"
        )
        print("|---|---|---|---|")
        for p, (a, ap), (b, bp) in zip(plants, pv, rv):
            fmt = lambda v, q: f"{v} ({'-' if q is None else f'{q:.2f}'})"
            print(
                f"| {p['key']} | {p['plant']['from']} -> {p['plant']['to']} | {fmt(b, bp)} | {fmt(a, ap)} |"
            )
        print("\nreal claims unsupported as a whole (read these):")
        for c in reals.values():
            if whole(c) == "unsupported":
                bad = [
                    f"{k['value']} [{k['clause'][:80]}] p={check(c, k['clause'], k['value'])[1]}"
                    for k in c["checks"]
                    if check(c, k["clause"], k["value"])[0] == "unsupported"
                ]
                print(f"  {c['key']}: " + " | ".join(bad))
    print("\nPASS" if passed else "\nFAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
