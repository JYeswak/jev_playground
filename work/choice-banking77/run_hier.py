#!/usr/bin/env python3
"""Hierarchical Choice on the full Banking77 test split, bead jev-5fm.

Bar: docs/demos/upstream-repro/choice-banking77-hier-20260924.md (committed before any call).

Grouping: GROUP_RULES below, a fixed ordered keyword rule over the dataset's own intent names
(first match wins, unmatched -> "account and other"). `--dump` writes hierarchy.json from it.

Per query, pinned jev-1.13.0, following docs-mirror/typesafe/cookbooks/hierarchical_classification.md
at depth 2 with beam width K=3:
  1. root Choice over the 8 parents (each parent described by its member intent names);
  2. child Choice inside each of the root's top-3 parents, the three sent in parallel.
The runner only collects these four distributions. Greedy and beam search are computed from them
offline by score_hier.py, so every routing decision is re-scorable without a key.

Run:
  python3 work/choice-banking77/run_hier.py --dump      (no key: writes hierarchy.json)
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/choice-banking77/run_hier.py
Rows: rows-hier-jev.jsonl. Resumes ids that already have a complete row.
"""

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "upstream/typesafe-ai/typesafe-sdk-python/src"))

JEV_MODEL = "jev-1.13.0"
INSTRUCTIONS = "The primary intent of this customer banking message"
BEAM = 3
CONCURRENCY = 8
OUT = os.path.join(HERE, "rows-hier-jev.jsonl")
HIERARCHY = os.path.join(HERE, "hierarchy.json")
FALLBACK_PARENT = "account and other"
# Ordered: the first pattern that matches an intent name (case-insensitive) assigns its parent.
GROUP_RULES = [
    ("top ups", r"top_?up|topping_up"),
    ("cash and atm", r"cash|atm"),
    ("transfers", r"transfer|beneficiary|receiving_money"),
    ("exchange and currencies", r"exchange|currenc|fiat"),
    ("payments charges and refunds", r"payment|refund|charge|transaction|direct_debit"),
    (
        "identity and security",
        r"identity|verify|source_of_funds|pin|passcode|compromised|lost_or_stolen",
    ),
    ("cards", r"card"),
]


def humanize(intent):
    return intent.replace("_", " ").lower()


def load_rows():
    with open(os.path.join(HERE, "full.jsonl"), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def build_hierarchy(rows):
    intents = sorted({r["intent"] for r in rows}, key=lambda c: (c.casefold(), c))
    parents = {name: [] for name, _ in GROUP_RULES}
    parents[FALLBACK_PARENT] = []
    for intent in intents:
        parent = next(
            (n for n, pat in GROUP_RULES if re.search(pat, intent, re.I)),
            FALLBACK_PARENT,
        )
        parents[parent].append(intent)
    return {"parents": {p: kids for p, kids in parents.items() if kids}}


def root_question(hier):
    from typesafe_sdk import Choice

    return Choice(
        instructions=INSTRUCTIONS,
        criteria={
            p: ", ".join(humanize(c) for c in kids)
            for p, kids in hier["parents"].items()
        },
    )


def child_question(kids):
    from typesafe_sdk import Choice

    return Choice(instructions=INSTRUCTIONS, criteria={humanize(c): None for c in kids})


def ask(client, text, question, back):
    t0 = time.perf_counter()
    resp = client.system_one(
        {"customer_message": text}, {"q": question}, model=JEV_MODEL
    )
    ans = resp.answers["q"]
    return {
        "model": resp.model,
        "choice": back.get(ans.choice, ans.choice),
        "confidence": float(ans.confidence),
        "probabilities": {
            back.get(k, k): float(v) for k, v in ans.probabilities.items()
        },
        "ms": int((time.perf_counter() - t0) * 1000),
        "usage": {
            "input_tokens": int(resp.usage.input_tokens),
            "output_tokens": int(resp.usage.output_tokens),
        },
    }


def one(client, hier, rq, item, inner):
    t0 = time.perf_counter()
    root = ask(client, item["text"], rq, {p: p for p in hier["parents"]})
    top = sorted(root["probabilities"], key=lambda p: -root["probabilities"][p])[:BEAM]
    futs = {
        p: inner.submit(
            ask,
            client,
            item["text"],
            child_question(hier["parents"][p]),
            {humanize(c): c for c in hier["parents"][p]},
        )
        for p in top
    }
    children = {p: f.result() for p, f in futs.items()}
    return {
        "i": item["i"],
        "intent": item["intent"],
        "root": root,
        "children": children,
        "wallMs": int((time.perf_counter() - t0) * 1000),
    }


def done_ids():
    ids = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    if "root" in r:
                        ids.add(r["i"])
    return ids


def main(argv):
    rows = load_rows()
    hier = build_hierarchy(rows)
    if "--dump" in argv:
        with open(HIERARCHY, "w", encoding="utf-8") as fh:
            json.dump(hier, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        sizes = {p: len(k) for p, k in hier["parents"].items()}
        print(f"parents={len(sizes)} sizes={sizes}", file=sys.stderr)
        return 0
    with open(HIERARCHY, encoding="utf-8") as fh:
        if json.load(fh) != hier:
            print("hierarchy.json differs from GROUP_RULES; refusing", file=sys.stderr)
            return 1
    if not os.environ.get("TYPESAFE_API_KEY"):
        print("unconfigured: TYPESAFE_API_KEY unset, no call made", file=sys.stderr)
        return 2
    from typesafe_sdk import TypeSafeClient

    client = TypeSafeClient(timeout=30.0)
    rq = root_question(hier)
    have = done_ids()
    todo = [r for r in rows if r["i"] not in have]
    print(f"hier: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    ok = failed = 0
    with (
        ThreadPoolExecutor(max_workers=CONCURRENCY * BEAM) as inner,
        ThreadPoolExecutor(max_workers=CONCURRENCY) as outer,
    ):
        futs = {outer.submit(one, client, hier, rq, item, inner): item for item in todo}
        for fut in as_completed(futs):
            item = futs[fut]
            try:
                row = fut.result()
                ok += 1
            except Exception as exc:  # noqa: BLE001 - recorded, scored as wrong
                row = {
                    "i": item["i"],
                    "intent": item["intent"],
                    "error": f"{type(exc).__name__}: {str(exc)[:1000]}",
                }
                failed += 1
            with open(OUT, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            if (ok + failed) % 200 == 0:
                print(
                    f"  hier {ok + failed}/{len(todo)} failed={failed}", file=sys.stderr
                )
    print(f"hier done ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed > len(rows) // 100 else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
