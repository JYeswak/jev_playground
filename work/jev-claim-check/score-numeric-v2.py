#!/usr/bin/env python3
"""Score numeric claim check v2 (bead jev-h8s, R83 retry 2). No key, stdlib only.

Reads numeric-v2-cases.jsonl (claims, per-number checks with their narrowed evidence, fresh plants;
committed before any call) and numeric-v2-rows.jsonl (one row per asked check; the last row with a
verdict wins). A check with empty evidence was never asked and is not confirmed, with no p.
Confirmed = supported; unsure and unsupported are both "not confirmed".

Bar (docs/demos/upstream-repro/claim-check-numeric-v2-20260924.md, frozen before the first call),
in EACH set. n = its plants. m = the plants whose ORIGINAL number occurs literally in the planted
check's narrowed evidence (the same evidence its original check gets).
  (a) planted number confirmed <= 10% of n (floor)
  (b) planted number not confirmed >= 80% of n (ceil)
  (c) original number confirmed >= 70% of m (ceil), over the m pairs
  (d) p(planted) < p(original) on >= 70% of m (ceil), over the m pairs; a missing p is not lower
  PASS = all four in both sets. Always-supported fails (a) and (b); always-unsure fails (c) and (d).

Run: python3 work/jev-claim-check/score-numeric-v2.py   (exit 0 PASS, 1 FAIL, 2 no rows)
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = ("supported", "unsupported", "unsure")


def main():
    cases = [
        json.loads(line)
        for line in open(os.path.join(HERE, "numeric-v2-cases.jsonl"), encoding="utf-8")
    ]
    path = os.path.join(HERE, "numeric-v2-rows.jsonl")
    if not os.path.exists(path):
        print("no numeric-v2-rows.jsonl: nothing scored")
        return 2
    rows = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            if r["verdict"] in VERDICTS or r["check"] not in rows:
                rows[r["check"]] = r

    def find(case, clause, value):
        return next(
            k for k in case["checks"] if k["clause"] == clause and k["value"] == value
        )

    def answer(case, k):
        if not k["evidence"]:
            return ("no-evidence", None)
        r = rows.get("\x00".join((case["set"], case["key"], k["clause"], k["value"])))
        return (
            (r["verdict"], r["probability"])
            if r and r["verdict"] in VERDICTS
            else ("no-verdict", None)
        )

    passed = True
    for s in ("readme", "close"):
        cs = [c for c in cases if c["set"] == s]
        reals = {c["key"]: c for c in cs if c["truth"]}
        plants = [c for c in cs if not c["truth"]]
        n = len(plants)
        pairs = []
        for p in plants:
            pl = p["plant"]
            pk = find(p, pl["plantedClause"], pl["to"])
            rk = find(reals[p["key"]], pl["realClause"], pl["from"])
            pairs.append(
                (
                    p,
                    answer(p, pk),
                    answer(reals[p["key"]], rk),
                    pl["from"] in pk["evidence"],
                )
            )
        covered = [x for x in pairs if x[3]]
        m = len(covered)
        confirmed_plants = sum(a[0] == "supported" for _, a, _, _ in pairs)
        not_confirmed = n - confirmed_plants
        originals = sum(b[0] == "supported" for _, _, b, _ in covered)
        lower = sum(
            a[1] is not None and b[1] is not None and a[1] < b[1]
            for _, a, b, _ in covered
        )
        bar = {
            "a": math.floor(0.10 * n),
            "b": math.ceil(0.80 * n),
            "c": math.ceil(0.70 * m),
            "d": math.ceil(0.70 * m),
        }
        met = {
            "a": confirmed_plants <= bar["a"],
            "b": not_confirmed >= bar["b"],
            "c": originals >= bar["c"],
            "d": lower >= bar["d"],
        }
        passed = passed and all(met.values())
        yn = lambda k: "yes" if met[k] else "NO"
        print(
            f"\n## set {s}: {len(reals)} real claims, n={n} plants, m={m} with the original in the narrowed evidence"
        )
        print("| Metric | Tool | Bar | Met |")
        print("|---|---:|---|---|")
        print(
            f"| (a) planted number confirmed | {confirmed_plants}/{n} | <= {bar['a']} | {yn('a')} |"
        )
        print(
            f"| (b) planted number not confirmed | {not_confirmed}/{n} | >= {bar['b']} | {yn('b')} |"
        )
        print(
            f"| (c) original confirmed (of m) | {originals}/{m} | >= {bar['c']} | {yn('c')} |"
        )
        print(
            f"| (d) p(planted) < p(original) (of m) | {lower}/{m} | >= {bar['d']} | {yn('d')} |"
        )
        pv = [a[0] for _, a, _, _ in pairs]
        print(
            f"planted verdicts: supported {pv.count('supported')}, unsure {pv.count('unsure')}, unsupported {pv.count('unsupported')}, no evidence {pv.count('no-evidence')}, no verdict {pv.count('no-verdict')}"
        )
        whole = []
        for c in reals.values():
            vs = [answer(c, k)[0] for k in c["checks"]]
            whole.append(
                "no-number"
                if not vs
                else "confirmed"
                if all(v == "supported" for v in vs)
                else "not confirmed"
            )
        print(
            f"whole real claims: confirmed {whole.count('confirmed')}, not confirmed {whole.count('not confirmed')}, no number {whole.count('no-number')}"
        )
        print(
            "\n| key | original -> planted | in narrowed evidence | original (p) | planted (p) |"
        )
        print("|---|---|---|---|---|")
        fmt = lambda v: f"{v[0]} ({'-' if v[1] is None else f'{v[1]:.2f}'})"
        for p, a, b, cov in pairs:
            print(
                f"| {p['key']} | {p['plant']['from']} -> {p['plant']['to']} | {'yes' if cov else 'no'} | {fmt(b)} | {fmt(a)} |"
            )
        print("\nreal checks called unsupported (read these):")
        for c in reals.values():
            for k in c["checks"]:
                v, q = answer(c, k)
                if v == "unsupported":
                    print(
                        f"  {c['key']}: {k['value']} [{k['clause'][:80]}] p={q} in-evidence={k['value'] in k['evidence']}"
                    )
    print("\nPASS" if passed else "\nFAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
