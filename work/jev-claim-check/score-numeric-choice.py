#!/usr/bin/env python3
"""Score the Choice-based numeric claim check (bead jev-25r). No key, stdlib only.

Reads numeric-choice-cases.jsonl (checks with their options and, for every value, the option labels
that match it, precomputed by the build with equalsValue; committed before any call) and
numeric-choice-rows.jsonl (one row per call; the last ok row per call wins). A value is CONFIRMED when
the chosen label is one of its matching labels. A check with no call, or a failed call, confirms
nothing.

Bar (docs/demos/upstream-repro/claim-check-numeric-choice-20260924.md, frozen before the first call):
  (F) feasibility: >= 7 of the 8 single-number items choose the expected token
  In EACH set:
  (a) digit plants confirmed <= 10% of digit plants (floor)
  (b) role plants confirmed <= 10% of role plants (floor)
  (c) real numbers confirmed >= 70% (ceil) of m, the real checks whose value is among their options
  PASS = F and (a), (b), (c) in both sets. Always choosing not_stated passes (a) and (b) and fails (c).

Run: python3 work/jev-claim-check/score-numeric-choice.py   (exit 0 PASS, 1 FAIL, 2 no rows)
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    cases = [
        json.loads(line)
        for line in open(
            os.path.join(HERE, "numeric-choice-cases.jsonl"), encoding="utf-8"
        )
    ]
    path = os.path.join(HERE, "numeric-choice-rows.jsonl")
    if not os.path.exists(path):
        print("no numeric-choice-rows.jsonl: nothing scored")
        return 2
    rows = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            if r["ok"] or r["call"] not in rows:
                rows[r["call"]] = r

    def chosen(call):
        r = rows.get(call) if call else None
        return r["choice"] if r and r["ok"] else None

    feas = [r for k, r in rows.items() if k.startswith("feasibility-")]
    feas_ok = sum(
        1
        for r in feas
        if r["ok"]
        and r["token"] is not None
        and r["token"].replace(",", "") == r["expect"].replace(",", "")
    )
    passed = feas_ok >= 7
    print(
        f"(F) feasibility: {feas_ok}/8 chose the expected token (bar >= 7): {'yes' if feas_ok >= 7 else 'NO'}"
    )
    for r in sorted(feas, key=lambda r: r["call"]):
        print(
            f"    {r['call']}: expect {r['expect']}, chose {r['token'] if r['ok'] else r['reason']}"
        )

    for s in ("readme", "close"):
        cs = [c for c in cases if c["set"] == s]
        real_checks = [k for c in cs if c["truth"] for k in c["checks"]]
        m_checks = [k for k in real_checks if k["inOptions"]]
        conf_real = sum(chosen(k["call"]) in k["match"] for k in m_checks)
        digit = [c for c in cs if c.get("kind") == "digit"]
        role = [c for c in cs if c.get("kind") == "role"]
        dconf = sum(chosen(c["plant"]["call"]) in c["plant"]["match"] for c in digit)
        rconf = sum(chosen(c["plant"]["call"]) in c["plant"]["match"] for c in role)
        bar = {
            "a": math.floor(0.10 * len(digit)),
            "b": math.floor(0.10 * len(role)),
            "c": math.ceil(0.70 * len(m_checks)),
        }
        met = {
            "a": dconf <= bar["a"],
            "b": rconf <= bar["b"],
            "c": conf_real >= bar["c"],
        }
        passed = passed and all(met.values())
        yn = lambda k: "yes" if met[k] else "NO"
        print(
            f"\n## set {s}: {len(real_checks)} real checks, m={len(m_checks)} with the value among the options"
        )
        print("| Metric | Tool | Bar | Met |")
        print("|---|---:|---|---|")
        print(
            f"| (a) digit plants confirmed | {dconf}/{len(digit)} | <= {bar['a']} | {yn('a')} |"
        )
        print(
            f"| (b) role plants confirmed | {rconf}/{len(role)} | <= {bar['b']} | {yn('b')} |"
        )
        print(
            f"| (c) real numbers confirmed, of m | {conf_real}/{len(m_checks)} | >= {bar['c']} | {yn('c')} |"
        )
        ns = sum(chosen(k["call"]) == "not_stated" for k in m_checks)
        wrong = sum(
            chosen(k["call"]) not in k["match"]
            and chosen(k["call"]) not in (None, "not_stated")
            for k in m_checks
        )
        print(
            f"of m: chose not_stated {ns}, chose another number {wrong}, no answer {sum(chosen(k['call']) is None for k in m_checks)}"
        )
        print(
            f"all real checks confirmed (descriptive): {sum(chosen(k['call']) in k['match'] for k in real_checks)}/{len(real_checks)}"
        )
        on_opt = [c for c in digit if c["plant"]["toInOptions"]]
        print(
            f"digit plants whose new value is also an option (accidental role plants): {len(on_opt)}, confirmed {sum(chosen(c['plant']['call']) in c['plant']['match'] for c in on_opt)}"
        )
        print("\n| role plant | original -> planted | model chose | verdict |")
        print("|---|---|---|---|")
        for c in role:
            ch = chosen(c["plant"]["call"])
            v = (
                "planted CONFIRMED"
                if ch in c["plant"]["match"]
                else "original confirmed"
                if ch in c["plant"]["originalMatch"]
                else "neither"
            )
            print(
                f"| {c['key']} | {c['plant']['from']} -> {c['plant']['to']} | {ch} | {v} |"
            )
        print("\nreal numbers among options but not confirmed (read these):")
        for c in cs:
            if not c["truth"]:
                continue
            for k in c["checks"]:
                if k["inOptions"] and chosen(k["call"]) not in k["match"]:
                    ch = chosen(k["call"])
                    print(
                        f"  {c['key']}: {k['value']} [{k['masked'][:80]}] chose {ch}={k['options'].get(ch, ch) if ch else '-'}"
                    )
    print("\nPASS" if passed else "\nFAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
