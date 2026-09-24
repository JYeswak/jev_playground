#!/usr/bin/env python3
"""Row sets for beads jev-k3k (10 intents) and jev-4jf (all 77) on Banking77.

Source: PolyAI-LDN/task-specific-datasets @ 9d081458ff52e53cf7e848f414e6e9344e4e6696,
banking_data/test.csv (CC-BY-4.0). This is the file the Hugging Face loader
PolyAI/banking77 (revision 90d4e2ee5521c04fc1488f065b8b083658768c57, banking77.py) downloads;
the HF datasets-server cannot serve it because the dataset is script-based.

Rules (preregistered in docs/demos/upstream-repro/choice-banking77-20260924.md and
choice-banking77-full-20260924.md): the K intents with the most test rows, ties broken
alphabetically by intent name, and every test row of those intents, in file order.
  --set subset  K=10 -> subset.jsonl  (jev-k3k, the default)
  --set full    K=77 -> full.jsonl    (jev-4jf: every intent, every test row)
One row per line: i, text, intent.

Run: python3 work/choice-banking77/sample.py [--set full]           (fetch, check sha256, write)
     python3 work/choice-banking77/sample.py [--set full] --check   (rebuild, diff vs committed)
Stdlib only. No model call.
"""

import csv
import hashlib
import io
import json
import os
import sys
import urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SETS = {"subset": (10, "subset.jsonl"), "full": (77, "full.jsonl")}
SHA = "9d081458ff52e53cf7e848f414e6e9344e4e6696"
URL = (
    "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/"
    f"{SHA}/banking_data/test.csv"
)
SHA256 = "d12d6e3bc4c3103966ae786dc435913c0c563dfa328f5a3646d0e62cfeeb474d"

UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    raw = urllib.request.urlopen(req, timeout=60).read()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"sha256 mismatch: got {digest}, pinned {SHA256}")
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))


def build(rows, k):
    counts = Counter(r["category"] for r in rows)
    # Ties broken alphabetically, case-insensitive: the source spells one intent
    # "Refund_not_showing_up", which a byte sort would put ahead of every lowercase name.
    ranked = sorted(counts, key=lambda c: (-counts[c], c.casefold(), c))
    chosen = ranked[:k]
    keep = set(chosen)
    subset = [r for r in rows if r["category"] in keep]
    out = [
        {"i": i, "text": r["text"], "intent": r["category"]}
        for i, r in enumerate(subset)
    ]
    return counts, chosen, out


def render(out):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out)


def main(argv):
    name = argv[argv.index("--set") + 1] if "--set" in argv else "subset"
    k, fname = SETS[name]
    out_path = os.path.join(HERE, fname)
    rows = fetch()
    counts, chosen, out = build(rows, k)
    print(
        f"source rows={len(rows)} intents={len(counts)} "
        f"per-intent counts={sorted(set(counts.values()))}",
        file=sys.stderr,
    )
    print(f"chosen ({k}): {chosen}", file=sys.stderr)
    print(f"subset rows={len(out)}", file=sys.stderr)
    text = render(out)
    if "--check" in argv:
        same = (
            os.path.exists(out_path) and open(out_path, encoding="utf-8").read() == text
        )
        print("check: identical" if same else "check: DIFFERS", file=sys.stderr)
        return 0 if same else 1
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
