#!/usr/bin/env python3
"""jev-ygl7: would any committed incumbent answer have raised under system-one-adapter v0.2.1?

v0.2.1 (e1d4cc9) makes providers raise when a completion did not finish normally: openai.py on
finish_reason != "stop", anthropic.py on stop_reason not in {end_turn, stop_sequence, None}.
Nothing else changes how a completed answer is parsed or scored. So the only committed rows whose
verdict could move are ANSWERED rows whose recorded finish/stop reason is outside that set.

Reads every tracked work/**/*.jsonl (keyless, offline). Prints, per file that records a reason
field (any of four spellings), the answered-row count, the reason distribution and how many would
raise. Exit 0 if none would raise, 1 otherwise, 2 if no file records a reason (an empty scan set
is not a pass). Files that record no reason are listed as UNMEASURED by this probe.

    python3 work/adapter-pin/finish-audit.py
"""

import collections
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYS = ("finishReason", "finish_reason", "stopReason", "stop_reason")
OK = {"stop", "end_turn", "stop_sequence", None}
INCUMBENT = ("grok", "haiku", "claude", "xai/", "anthropic", "openrouter")


def main():
    files = subprocess.run(
        ["git", "ls-files", "work/**/*.jsonl"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    measured = unmeasured = answered_total = raise_total = 0
    for f in files:
        dist = collections.Counter()
        answered = 0
        has_reason = mentions_incumbent = False
        with open(os.path.join(ROOT, f), encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(r, dict):
                    continue
                if any(
                    t in json.dumps(r.get("model", "")).lower() for t in INCUMBENT
                ) or any(t in f.lower() for t in INCUMBENT):
                    mentions_incumbent = True
                key = next((k for k in KEYS if k in r), None)
                if key is None:
                    continue
                has_reason = True
                if r.get("error"):
                    continue
                answered += 1
                dist[r.get(key)] += 1
        if has_reason:
            bad = sum(v for k, v in dist.items() if k not in OK)
            measured += 1
            answered_total += answered
            raise_total += bad
            print(
                f"MEASURED   {f}  answered={answered} reasons={dict(dist)} would_raise={bad}"
            )
        elif mentions_incumbent:
            unmeasured += 1
            print(f"UNMEASURED {f}  (no finish/stop reason recorded)")
    print(
        f"files measured={measured} unmeasured_incumbent_files={unmeasured} "
        f"answered_rows={answered_total} would_raise_under_0.2.1={raise_total}"
    )
    if measured == 0:
        return 2
    return 1 if raise_total else 0


if __name__ == "__main__":
    sys.exit(main())
