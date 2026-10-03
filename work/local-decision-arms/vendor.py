"""Vendored-code recognition: local System One servers vs committed jev-1.13.0 rows (jev-576e).

Bar: BAR-vendor.md. Data: work/vendor-paste/sample.json (windows of third-party and first-party
code with labels, committed for jev-30hi); jev answers: work/vendor-paste/vendor-rows.jsonl.

  python3 work/local-decision-arms/vendor.py --inspect
  python3 work/local-decision-arms/vendor.py ARM URL
  python3 work/local-decision-arms/vendor.py --score ARM [ARM ...]
"""

import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VP = os.path.join(HERE, "..", "vendor-paste")
Q = (
    "This pasted code is vendored third-party code, not code written for this repository. "
    "Judge only the code text, not any file path."
)
SAMPLE = json.load(open(os.path.join(VP, "sample.json"), encoding="utf-8"))
HELD = SAMPLE["held"]
DEV = SAMPLE["dev"]


def positive(row):
    return str(row.get("label")).lower() in ("1", "true", "vendored", "pos", "yes")


def ask(url, row):
    body = {
        "model": "kev-latest",
        "state": {"code": row["window"][:4000]},
        "questions": {"vendored": {"type": "noul", "instructions": Q}},
    }
    req = urllib.request.Request(
        url, json.dumps(body).encode(), {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.load(resp)["answers"]["vendored"]


def run(arm, url, split="held"):
    path = os.path.join(
        HERE, "vendor-rows-%s%s.jsonl" % (arm, "" if split == "held" else "-dev")
    )
    done = set()
    if os.path.exists(path):
        done = {json.loads(line)["sample_id"] for line in open(path) if line.strip()}
    with open(path, "a", encoding="utf-8") as out:
        for row in HELD if split == "held" else DEV:
            if row["sample_id"] in done:
                continue
            start = time.time()
            try:
                ans = ask(url, row)
                noul = ans.get("noul") if isinstance(ans, dict) else ans
                rec = {
                    "sample_id": row["sample_id"],
                    "arm": arm,
                    "noul": float(noul),
                    "ms": round((time.time() - start) * 1000),
                }
            except Exception as err:  # recorded per row; the run goes on
                rec = {
                    "sample_id": row["sample_id"],
                    "arm": arm,
                    "error": type(err).__name__,
                }
            out.write(json.dumps(rec) + "\n")
            out.flush()


def auc(pairs):
    pos = [s for s, y in pairs if y]
    neg = [s for s, y in pairs if not y]
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def ece(pairs):
    bins = [[] for _ in range(10)]
    for s, y in pairs:
        bins[min(int(s * 10), 9)].append((s, y))
    return sum(
        len(b)
        / len(pairs)
        * abs(sum(s for s, _ in b) / len(b) - sum(y for _, y in b) / len(b))
        for b in bins
        if b
    )


def stats(by_id):
    label = {r["sample_id"]: positive(r) for r in HELD}
    pairs = [(by_id[i], label[i]) for i in label if i in by_id]
    return {
        "n": len(pairs),
        "pos": sum(y for _, y in pairs),
        "auc": auc(pairs),
        "ece": ece(pairs),
    }


def score(arms):
    jev = {}
    for line in open(os.path.join(VP, "vendor-rows.jsonl")):
        r = json.loads(line)
        if r.get("status") == "scored":
            jev[r["sample_id"]] = float(r["noul"])
    js = stats(jev)
    print("jev-1.13.0", json.dumps(js))
    for arm in arms:
        rows = [
            json.loads(l)
            for l in open(os.path.join(HERE, "vendor-rows-%s.jsonl" % arm))
            if l.strip()
        ]
        got = {r["sample_id"]: r["noul"] for r in rows if "noul" in r}
        s = stats(got)
        errors = len(rows) - len(got)
        verdict = (
            "FAILED-RUN"
            if errors > 2 or s["n"] < len(HELD) - 2
            else "PASS"
            if s["auc"] >= js["auc"] - 0.02 and s["ece"] <= js["ece"]
            else "FAIL"
        )
        ms = sorted(r["ms"] for r in rows if "ms" in r)
        print(
            arm,
            json.dumps(s),
            "errors",
            errors,
            "median_ms",
            ms[len(ms) // 2] if ms else None,
            verdict,
        )


def platt(arm):
    """BAR-vendor-platt.md: fit logistic(a*logit(p)+b) on dev rows, apply to held rows."""
    import math

    def logit(p):
        p = min(max(p, 1e-4), 1 - 1e-4)
        return math.log(p / (1 - p))

    lab = {r["sample_id"]: positive(r) for r in DEV + HELD}
    dev = [
        json.loads(l)
        for l in open(os.path.join(HERE, "vendor-rows-%s-dev.jsonl" % arm))
        if l.strip()
    ]
    xs = [(logit(r["noul"]), lab[r["sample_id"]]) for r in dev if "noul" in r]
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
        json.loads(l)
        for l in open(os.path.join(HERE, "vendor-rows-%s.jsonl" % arm))
        if l.strip()
    ]
    got = {
        r["sample_id"]: 1 / (1 + math.exp(-(a * logit(r["noul"]) + b)))
        for r in held
        if "noul" in r
    }
    s = stats(got)
    print(
        arm + "+platt",
        "a=%.3f b=%.3f dev_n=%d" % (a, b, len(xs)),
        json.dumps(s),
        "PASS" if s["auc"] >= 0.807 and s["ece"] <= 0.185 else "FAIL",
    )


if __name__ == "__main__":
    if sys.argv[1] == "--inspect":
        print(
            sorted({k for r in HELD for k in r}),
            {str(r.get("label")) for r in HELD},
            sum(positive(r) for r in HELD),
            len(HELD),
        )
    elif sys.argv[1] == "--score":
        score(sys.argv[2:])
    elif sys.argv[1] == "--platt":
        platt(sys.argv[2])
    elif sys.argv[1] == "--dev":
        run(sys.argv[2], sys.argv[3], "dev")
    else:
        run(sys.argv[1], sys.argv[2])
