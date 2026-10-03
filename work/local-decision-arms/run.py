"""Replay Banking77 through a local System One server (bead jev-576e). Bar: BAR.md.

python3 work/local-decision-arms/run.py ARM URL    # resumes rows-ARM.jsonl
python3 work/local-decision-arms/run.py --score ARM [ARM ...]
"""

import json
import os
import random
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
B77 = os.path.join(HERE, "..", "choice-banking77")
INSTRUCTIONS = "The primary intent of this customer banking message"


def load(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


ROWS = load(os.path.join(B77, "full.jsonl"))
SAMPLE = sorted(random.Random(7).sample(range(len(ROWS)), 600))
DEV = sorted(random.Random(8).sample(sorted(set(range(len(ROWS))) - set(SAMPLE)), 200))
INTENTS = sorted({r["intent"] for r in ROWS}, key=lambda c: (c.casefold(), c))
LABELS = {c.replace("_", " ").lower(): c for c in INTENTS}


def ask(url, row):
    body = {
        "model": "kev-latest",
        "state": {"customer_message": row["text"]},
        "questions": {
            "intent": {
                "type": "choice",
                "instructions": INSTRUCTIONS,
                "criteria": {label: None for label in LABELS},
            }
        },
    }
    req = urllib.request.Request(
        url, json.dumps(body).encode(), {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.load(resp)["answers"]["intent"]


def run(arm, url, split="held"):
    path = os.path.join(
        HERE, "rows-%s%s.jsonl" % (arm, "" if split == "held" else "-dev")
    )
    done = {r["i"] for r in load(path)} if os.path.exists(path) else set()
    with open(path, "a", encoding="utf-8") as out:
        for i in SAMPLE if split == "held" else DEV:
            if i in done:
                continue
            row = ROWS[i]
            start = time.time()
            try:
                ans = ask(url, row)
                rec = {
                    "i": i,
                    "intent": row["intent"],
                    "arm": arm,
                    "choice": LABELS.get(ans.get("choice"), ans.get("choice")),
                    "p_choice": (ans.get("probabilities") or {}).get(ans.get("choice")),
                    "confidence": ans.get("confidence"),
                    "ms": round((time.time() - start) * 1000),
                }
            except Exception as err:  # one row's failure is recorded, the run goes on
                rec = {
                    "i": i,
                    "intent": row["intent"],
                    "arm": arm,
                    "error": type(err).__name__,
                }
            out.write(json.dumps(rec) + "\n")
            out.flush()


def ece(pairs):
    bins = [[] for _ in range(10)]
    for p, ok in pairs:
        bins[min(int(p * 10), 9)].append((p, ok))
    n = len(pairs)
    return sum(
        len(b)
        / n
        * abs(sum(p for p, _ in b) / len(b) - sum(ok for _, ok in b) / len(b))
        for b in bins
        if b
    )


def stats(rows):
    ok = [r for r in rows if "error" not in r]
    pairs = [(float(r["p_choice"] or 0.0), r["choice"] == r["intent"]) for r in ok]
    ms = sorted(r["ms"] for r in ok if "ms" in r)
    return {
        "n": len(ok),
        "errors": len(rows) - len(ok),
        "acc": sum(c for _, c in pairs) / len(pairs),
        "ece": ece(pairs),
        "median_ms": ms[len(ms) // 2] if ms else None,
    }


def jev_rows():
    keep = set(SAMPLE)
    out = []
    for r in load(os.path.join(B77, "rows-full-jev.jsonl")):
        if r["i"] in keep and r.get("choice"):
            choice = LABELS.get(r["choice"], r["choice"])
            out.append(
                {
                    "i": r["i"],
                    "intent": r["intent"],
                    "choice": choice,
                    "p_choice": (r.get("probabilities") or {}).get(r["choice"]),
                }
            )
    return out


def score(arms):
    jev = jev_rows()
    jstat = stats(jev)
    print(
        "jev-1.13.0",
        json.dumps(
            {k: round(v, 4) if isinstance(v, float) else v for k, v in jstat.items()}
        ),
    )
    jok = {r["i"]: r["choice"] == r["intent"] for r in jev}
    for arm in arms:
        rows = load(os.path.join(HERE, "rows-%s.jsonl" % arm))
        s = stats(rows)
        good = {r["i"]: r["choice"] == r["intent"] for r in rows if "error" not in r}
        both = [i for i in good if i in jok]
        b = sum(1 for i in both if good[i] and not jok[i])
        c = sum(1 for i in both if jok[i] and not good[i])
        verdict = (
            "FAILED-RUN"
            if s["errors"] > 6 or s["n"] < 600 - 6
            else "PASS"
            if s["acc"] >= jstat["acc"] - 0.02 and s["ece"] <= jstat["ece"]
            else "FAIL"
        )
        print(
            arm,
            json.dumps(
                {k: round(v, 4) if isinstance(v, float) else v for k, v in s.items()}
            ),
            "discordant arm-only %d jev-only %d" % (b, c),
            verdict,
        )


def platt(arm):
    """BAR-b77-platt.md: Platt on chosen-option probability, fit on dev, apply to held."""
    import math

    def logit(p):
        p = min(max(float(p or 0.0), 1e-4), 1 - 1e-4)
        return math.log(p / (1 - p))

    dev = [
        r
        for r in load(os.path.join(HERE, "rows-%s-dev.jsonl" % arm))
        if "error" not in r
    ]
    xs = [(logit(r["p_choice"]), r["choice"] == r["intent"]) for r in dev]
    a, b = 1.0, 0.0
    for _ in range(2000):
        ga = gb = 0.0
        for x, y in xs:
            p = 1 / (1 + math.exp(-(a * x + b)))
            ga += (p - y) * x
            gb += p - y
        a -= 0.1 * ga / len(xs)
        b -= 0.1 * gb / len(xs)
    held = [
        r for r in load(os.path.join(HERE, "rows-%s.jsonl" % arm)) if "error" not in r
    ]
    for r in held:
        r["p_choice"] = 1 / (1 + math.exp(-(a * logit(r["p_choice"]) + b)))
    s = stats(held)
    print(
        arm + "+platt",
        "a=%.3f b=%.3f dev_n=%d" % (a, b, len(xs)),
        json.dumps(s),
        "PASS" if s["acc"] >= 0.7867 - 0.02 and s["ece"] <= 0.1017 else "FAIL",
    )


if __name__ == "__main__":
    if sys.argv[1] == "--score":
        score(sys.argv[2:])
    elif sys.argv[1] == "--platt":
        platt(sys.argv[2])
    elif sys.argv[1] == "--dev":
        run(sys.argv[2], sys.argv[3], "dev")
    else:
        run(sys.argv[1], sys.argv[2])
