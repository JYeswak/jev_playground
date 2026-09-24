#!/usr/bin/env python3
"""Live arms for jev-t2u. Bar: bicameral-gate-hard-cases-prereg-20260924.md, committed before any call.

Questions come from questions.mjs at HEAD (read through node), not a Python copy. The call path is
run-b.py's: Jev criteria via the vendored SDK (jev-1.13.0), Haiku criteria via system-one-adapter.
Resumes rows that already have scores. Does not print a key.

Run: infisical run --silent --projectId=<id> -- \
  upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/bicameral-gate/run-hard.py
"""

import importlib.util
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

_spec = importlib.util.spec_from_file_location("run_b", os.path.join(HERE, "run-b.py"))
rb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rb)


def load_questions():
    out = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            "const m = await import(process.argv[1]); "
            "console.log(JSON.stringify({RISK: m.RISK, STATE_CONTEXT: m.STATE_CONTEXT, CUT: m.CUT}))",
            os.path.join(HERE, "questions.mjs"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)


Q = load_questions()
if (
    list(Q["RISK"]) != rb.RISK
    or Q["STATE_CONTEXT"] != rb.STATE_CONTEXT
    or Q["CUT"] != rb.CUT
):
    raise SystemExit(
        "questions.mjs names, context or cut differ from run-b.py's call path"
    )


def questions(_variant):
    out = {
        name: rb.Noul(instructions=q["instructions"], criteria=q["criteria"])
        for name, q in Q["RISK"].items()
    }
    out["mentions_git"] = rb.Noul(
        instructions="Does this command text contain the word git?"
    )
    return out


rb.questions = questions  # jev_one and run_haiku look this up at call time


def load_rows():
    sample = {
        r["i"]: r["command"]
        for r in json.load(open(os.path.join(HERE, "hard-cases-sample.json")))["rows"]
    }
    labels = json.load(open(os.path.join(HERE, "hard-cases-labels.json")))["rows"]
    return [
        {"i": r["i"], "label": r["label"], "command": sample[r["i"]]} for r in labels
    ]


def main():
    rows = load_rows()
    code = rb.run_jev("criteria", rows, os.path.join(HERE, "hard-rows-jev.jsonl"))
    if code:
        return code
    return rb.run_haiku(rows, os.path.join(HERE, "hard-rows-haiku.jsonl"))


if __name__ == "__main__":
    raise SystemExit(main())
