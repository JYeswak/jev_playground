#!/usr/bin/env python3
"""Row sets for beads jev-qw8 (one domain of 15 intents) and jev-pm3 (all 150) on CLINC150.

Source: clinc/oos-eval @ 828f8093932c8fe6ca7936c3d2e52903b1c523de (Larson et al. 2019, CC-BY-3.0),
data/data_full.json (test: 4,500 in-scope rows, 30 per intent; oos_test: 1,000 out-of-scope rows)
and data/domains.json (10 domains x 15 intents), both sha256-pinned below.

Rule (preregistered in docs/demos/upstream-repro/choice-clinc150-20260924.md):
  rng = random.Random(20260924)
  domain  = rng.choice(sorted domain names)          -> its 15 intents are the in-scope set
  in-scope rows = every test row of those 15 intents, in file order (15 x 30 = 450)
  oos rows      = oos_test rows at sorted(rng.sample(range(1000), 300)), in file order (300)
One row per line: i, text, intent (an intent name, or "oos"). 750 rows.

--set full (jev-pm3, preregistered in choice-clinc150-full-20260924.md): every test row (4,500, 150
intents x 30) then every oos_test row (1,000), in file order, no sampling; each row also carries
its domain from domains.json ("oos" for out-of-scope). 5,500 rows -> full.jsonl.

Run: python3 work/choice-clinc150/sample.py [--set full]           (fetch, check sha256, write)
     python3 work/choice-clinc150/sample.py [--set full] --check   (rebuild, diff vs committed)
Stdlib only. No model call.
"""

import hashlib
import json
import os
import random
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SHA = "828f8093932c8fe6ca7936c3d2e52903b1c523de"
BASE = f"https://raw.githubusercontent.com/clinc/oos-eval/{SHA}/data/"
PINS = {
    "data_full.json": "36923c3705a59e08fe9c3883d8bc2dd966ef93e22cb78ac41171782a698d56e0",
    "domains.json": "b947b579d3b8e74b06f93b01083d8efaff2888b43a3e362533bd88a6e1211b3a",
}
SEED = 20260924
N_OOS = 300


def fetch(name):
    raw = urllib.request.urlopen(BASE + name, timeout=60).read()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != PINS[name]:
        raise SystemExit(f"{name}: sha256 mismatch: got {digest}, pinned {PINS[name]}")
    return json.loads(raw)


def build(data, domains):
    rng = random.Random(SEED)
    domain = rng.choice(sorted(domains))
    intents = domains[domain]
    keep = set(intents)
    inscope = [(t, lab) for t, lab in data["test"] if lab in keep]
    picks = sorted(rng.sample(range(len(data["oos_test"])), N_OOS))
    oos = [data["oos_test"][j] for j in picks]
    rows = [
        {"i": i, "text": t, "intent": lab} for i, (t, lab) in enumerate(inscope + oos)
    ]
    return domain, intents, rows


def build_full(data, domains):
    domain_of = {c: d for d, cs in domains.items() for c in cs}
    rows = [
        {"i": i, "text": t, "intent": lab, "domain": domain_of.get(lab, "oos")}
        for i, (t, lab) in enumerate(data["test"] + data["oos_test"])
    ]
    return "all", sorted(domain_of), rows


def main(argv):
    full = "--set" in argv and argv[argv.index("--set") + 1] == "full"
    out_path = os.path.join(HERE, "full.jsonl" if full else "subset.jsonl")
    builder = build_full if full else build
    domain, intents, rows = builder(fetch("data_full.json"), fetch("domains.json"))
    n_oos = sum(1 for r in rows if r["intent"] == "oos")
    print(
        f"domain: {domain}; intents ({len(intents)}): {sorted(intents)}",
        file=sys.stderr,
    )
    print(
        f"rows: {len(rows)} ({len(rows) - n_oos} in-scope, {n_oos} oos)",
        file=sys.stderr,
    )
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    if "--check" in argv:
        same = False
        if os.path.exists(out_path):
            with open(out_path, encoding="utf-8") as fh:
                same = fh.read() == text
        print("check: identical" if same else "check: DIFFERS", file=sys.stderr)
        return 0 if same else 1
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"sha256 {hashlib.sha256(text.encode()).hexdigest()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
