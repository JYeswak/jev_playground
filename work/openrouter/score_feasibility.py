#!/usr/bin/env python3
"""Keyless scorer for bead jev-14qk: per-model feasibility of OpenRouter :free models on SST-5.

Bar: docs/demos/upstream-repro/openrouter-free-feasibility-20260924.md. Reads only committed rows
(work/openrouter/rows-sst5-*.jsonl) and work/score-sst5/sample.jsonl. Last row per id wins; an id
with no answered row is failed with its last error. Level and error use jev-zui's own functions
(work/score-sst5/score.py), and accuracy/MAE are descriptive only: 50 rows decide nothing about
quality.

Run: python3 work/openrouter/score_feasibility.py
Exit 1 when a row file is missing for any model. Stdlib only, no key, no network.
"""

import importlib.util
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
N_ROWS = 50
FAIL_LIMIT_PCT = (
    1.0  # the variance units' failed-row bar (jev-4jf: more than 1% fails the run)
)


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# provider.py imports the adapter; reading its model list must not need it, so parse the tuple.
def free_models():
    src = open(os.path.join(HERE, "provider.py")).read()
    block = src.split("FREE_STRUCTURED = (", 1)[1].split(")", 1)[0]
    return [
        line.strip().strip(",").strip('"')
        for line in block.splitlines()
        if line.strip().startswith('"')
    ]


def rows_path(model):
    return os.path.join(
        HERE, "rows-sst5-" + model.replace("/", "__").replace(":", "_") + ".jsonl"
    )


def nearest_rank(xs, q):
    xs = sorted(xs)
    return xs[max(0, min(len(xs) - 1, int(-(-q * len(xs) // 1)) - 1))] if xs else None


def error_class(msg):
    """The exception class plus the HTTP status and provider message head, verbatim."""
    return msg.split(" | ")[0][:160]


def main():
    s5 = load_mod("score_sst5", os.path.join(ROOT, "work/score-sst5/score.py"))
    sample = s5.load_jsonl(os.path.join(ROOT, "work/score-sst5/sample.jsonl"))[:N_ROWS]
    label = {s["i"]: s["label"] for s in sample}
    missing = []
    print(
        f"| Model | Answered | Failed | Zero-mass | Flat | Renormalized | p50 / p95 ms (answered) | Upstream providers | Exact / MAE (descriptive) |"
    )
    print("|---|---:|---:|---:|---:|---:|---|---|---|")
    details = []
    for model in free_models():
        path = rows_path(model)
        if not os.path.exists(path):
            missing.append(model)
            print(f"| `{model}` | not run | | | | | | | |")
            continue
        fin = {}
        for r in map(json.loads, filter(str.strip, open(path))):
            if "score" in r or r["i"] not in fin or "score" not in fin[r["i"]]:
                fin[r["i"]] = r
        ans = [fin[i] for i in label if i in fin and "score" in fin[i]]
        fails = [
            fin.get(i, {"error": "not attempted"})
            for i in label
            if i not in fin or "score" not in fin[i]
        ]
        zero = sum(
            1
            for r in ans
            if isinstance(r.get("originalProbabilities"), dict)
            and sum(r["originalProbabilities"].values()) == 0
        )
        flat = sum(1 for r in ans if len(set(r["probabilities"].values())) == 1)
        renorm = sum(1 for r in ans if r.get("probabilityError"))
        lat = [r["latencyMs"] for r in ans]
        provs = Counter(r.get("provider") or "unreported" for r in ans)
        exact = sum(1 for r in ans if s5.rounded(r["score"]) == label[r["i"]])
        mae = (
            sum(abs(s5.rounded(r["score"]) - label[r["i"]]) for r in ans) / len(ans)
            if ans
            else None
        )
        print(
            f"| `{model}` | {len(ans)}/{N_ROWS} | {len(fails)} | {zero} | {flat} | {renorm} | "
            f"{nearest_rank(lat, 0.5)} / {nearest_rank(lat, 0.95)} | "
            f"{', '.join(f'{p} {n}' for p, n in provs.most_common())} | "
            f"{f'{exact}/{len(ans)}, {mae:.2f}' if ans else 'n/a'} |"
        )
        classes = Counter(error_class(r.get("error", "")) for r in fails)
        retried = Counter()
        for r in fin.values():
            for cat, msg in r.get("retryReasons") or []:
                retried[f"{cat}: {str(msg)[:120]}"] += 1
        details.append((model, classes, retried))

    print(
        "\nFailures by verbatim class, and adapter retries (all rows, answered or not)"
    )
    for model, classes, retried in details:
        print(f"- {model}")
        for c, n in classes.most_common():
            print(f"    failed {n}: {c}")
        for c, n in retried.most_common(5):
            print(f"    retried {n}: {c}")
    print(
        f"\nA model can carry a 500-row arm only if it answers {N_ROWS}/{N_ROWS} here (the 1% bar allows "
        f"{int(500 * FAIL_LIMIT_PCT / 100)} of 500) with 0 zero-mass rows."
    )
    if missing:
        print(f"MISSING rows for {len(missing)} model(s): {missing}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
