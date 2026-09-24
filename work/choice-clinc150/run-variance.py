#!/usr/bin/env python3
"""Extra runs for bead jev-kvw: the jev-qw8 subset arms again, through run.py's own code unchanged.

run.py is imported, not edited: its load_rows, labels, question, run_jev and run_haiku (structured
outputs) are called with the subset set's rows, question and concurrency, and only the output path
differs. Arms: jev-run2, jev-run3 -> rows-jev-run{2,3}.jsonl; haiku-run2, haiku-run3 ->
rows-haiku-run{2,3}.jsonl. Resumes rows that already have a choice. Never prints a key.
Bar: docs/demos/upstream-repro/choice-clinc150-variance-20260924.md (committed before any call).

Run:
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \
    work/choice-clinc150/run-variance.py jev-run2 jev-run3 haiku-run2 haiku-run3
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "clinc_run", os.path.join(HERE, "run.py")
)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

ARMS = ("jev-run2", "jev-run3", "haiku-run2", "haiku-run3")


def main(argv, bar_path=None, repo=None):
    root = os.path.dirname(os.path.dirname(HERE))
    sys.path.insert(0, os.path.join(root, "work/sr-adopt"))
    from phase_gate import call_after_bar

    bar = bar_path or os.path.join(
        root, "docs/demos/upstream-repro/choice-clinc150-full-20260924.md"
    )
    call_after_bar(bar, lambda: None, repo=repo or root)
    if not argv or any(a not in ARMS for a in argv):
        print("usage: run-variance.py " + " ".join(ARMS), file=sys.stderr)
        return 64
    fname, pattern, instructions, concurrency = R.SETS["subset"]
    rows = R.load_rows(fname)
    label_map = R.labels(rows)
    q = R.question(label_map, instructions)
    code = 0
    for arm in argv:
        path = os.path.join(HERE, pattern.format(arm=arm))
        if arm.startswith("jev"):
            code = R.run_jev(rows, label_map, path, q, concurrency) or code
        else:
            code = R.run_haiku(rows, label_map, path, q, concurrency) or code
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
