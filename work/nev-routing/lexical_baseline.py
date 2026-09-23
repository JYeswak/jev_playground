#!/usr/bin/env python3
"""B5 lexical baseline over skillranker synthetic skill-selection corpus.

Reads skillranker/tests/eval/synthetic_cases.v1.jsonl (12 cases, labels in
acceptable_additional_invocations_y). Baseline: content-token overlap between
(prompt_summary + constraints) and roster skill_id words; pick max; ABSTAIN
iff best score is 0 (fixed naive rule, no tuning — tuning on n=12 would be
fitting the test set).

Question answered: is in-distribution skill selection lexically decidable?
If yes -> B5 bit 1 YES -> NO SEAT for this shape.

Offline. No key. No network. Persists pairs.jsonl + lexical-receipt.json.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "/Users/josh/Developer/jev/skillranker/tests/eval/synthetic_cases.v1.jsonl"
STOP = set("a an the and or of to in on for with is are was were be by as at "
           "it its this that these those what which who whom whose how when "
           "from into over under again then than so such no not only own same "
           "too very can will just don should now agent ask asks helping helps "
           "procedure".split())


def toks(s):
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP]


def main():
    try:
        rows = [json.loads(l) for l in open(SRC) if l.strip()]
    except Exception as exc:
        print(f"NOT_RUN corpus unreadable: {exc}")
        return 2

    pairs = []
    for r in rows:
        y = list(r["acceptable_additional_invocations_y"])
        pairs.append({"id": r["case_id"], "kind": r["case_kind"],
                      "prompt": r["prompt_summary"],
                      "roster": [s["skill_id"] for s in (r.get("visible_roster") or [])],
                      "y": y})
    with open(os.path.join(HERE, "pairs.jsonl"), "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p) + "\n")

    res = []
    for p in rows:
        pt = set(toks(p["prompt_summary"] + " " + " ".join(p.get("current_constraints", []))))
        scored = []
        for s in p["visible_roster"]:
            st = set(toks(s["skill_id"].replace("-", " ") + " " + s.get("invocation_name", "").replace("-", " ")))
            scored.append((len(pt & st), s["skill_id"]))
        scored.sort(reverse=True)
        pick = None if scored[0][0] == 0 else scored[0][0] and scored[0][1]
        y = list(p["acceptable_additional_invocations_y"])
        if p["case_kind"].startswith("no_match"):
            ok = pick is None
        else:
            ok = pick in y
        res.append({"id": p["case_id"], "kind": p["case_kind"], "pick": pick,
                    "y": y, "ok": ok, "scores": scored})

    n = len(res)
    acc = sum(1 for r in res if r["ok"]) / n
    receipt = {"n": n, "lex_acc": round(acc, 4),
               "rows": [{k: r[k] for k in ("id", "kind", "pick", "y", "ok")} for r in res],
               "no_claim": ("n=12 synthetic, repo forbids holdout claims; "
                            "lexical-vs-labels only, says nothing about live Jev")}
    with open(os.path.join(HERE, "lexical-receipt.json"), "w") as fh:
        json.dump(receipt, fh, indent=2)
    for r in res:
        print(f"{r['id'][:44]:44s} pick={str(r['pick']):28s} y={r['y']} {'OK' if r['ok'] else 'MISS'}")
    print(f"lex_acc={acc:.4f} n={n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
