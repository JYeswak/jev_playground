#!/usr/bin/env python3
"""Will each Jev request fit the documented input limit? Keyless, run before the first call.

jev-1.13 accepts at most 32k tokens for the `state` plus the longest question
(docs-mirror/typesafe/llms-full.txt:13008, the Models page). A request over it returns
HTTP 400 `max_tokens_exceeded`. On 2026-09-25 the OSWorld Best-of-N run (jev-9gtw.2) sent 12
such states; they were scored as wrong answers and were 71% of that run's measured loss.

Tokens cannot be counted here (no tokenizer ships with the SDK), so the estimate comes from bytes,
with the bytes-per-token band taken from real calls rather than a guess: every answered row of
work/jev-state-size/calibration-osworld-r3.tsv gives compact request bytes (state + question)
and the input_tokens the API billed. The lowest and highest ratios bound the estimate:

  FITS  bytes / lowest ratio  <= LIMIT   (even the most token-dense case fits)
  OVER  bytes / highest ratio >  LIMIT   (even the least token-dense case does not)
  NEAR  otherwise                        (decide in the prereg: exclude, or truncate by a stated rule)

LIMIT is 32,768: the docs say "32k", and one answered request billed 32,234 input tokens, so the
limit is not 32,000. On the calibration table no refused request is FITS and every FITS request
was answered (work/jev-state-size/test_state_size.py).

Bytes are counted on compact JSON (no spaces), which is what the JS client sends.

    python3 scripts/jev-state-size.py STATES.jsonl [--field state] [--question-bytes N]

Each line is one request's state, or an object holding it under --field. The key printed per
item is its `task` or `id` value, else its line number. Exit 0 all FITS, 1 any NEAR or OVER,
2 usage error or NOT_RUN (calibration table missing or has no answered rows).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

LIMIT = 32_768
ROOT = Path(__file__).resolve().parents[1]
CALIBRATION = ROOT / "work" / "jev-state-size" / "calibration-osworld-r3.tsv"


def compact_bytes(value) -> int:
    return len(
        json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )


def ratio_band(calibration: Path) -> tuple[float, float]:
    """(lowest, highest) bytes per billed input token over the answered calibration rows."""
    ratios = []
    with calibration.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row.get("outcome") != "answered" or not row.get("input_tokens"):
                continue
            total = int(row["state_bytes"]) + int(row["question_bytes"])
            ratios.append(total / int(row["input_tokens"]))
    if not ratios:
        raise ValueError(f"no answered rows in {calibration}")
    return min(ratios), max(ratios)


def classify(total_bytes: int, band: tuple[float, float], limit: int = LIMIT) -> str:
    low, high = band
    if total_bytes / low <= limit:
        return "FITS"
    if total_bytes / high > limit:
        return "OVER"
    return "NEAR"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("states")
    parser.add_argument("--field", help="read the state from this key of each line")
    parser.add_argument(
        "--question-bytes",
        type=int,
        default=0,
        help="compact bytes of the longest question sent with each state",
    )
    parser.add_argument("--calibration", type=Path, default=CALIBRATION)
    args = parser.parse_args(argv)

    try:
        band = ratio_band(args.calibration)
    except (OSError, ValueError, KeyError) as err:
        print(f"NOT_RUN calibration unusable: {err}")
        return 2
    try:
        lines = Path(args.states).read_text(encoding="utf-8").splitlines()
    except OSError as err:
        print(f"NOT_RUN cannot read {args.states}: {err}")
        return 2

    counts = {"FITS": 0, "NEAR": 0, "OVER": 0}
    flagged = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as err:
            print(f"NOT_RUN line {number} is not JSON: {err}")
            return 2
        state = item.get(args.field) if args.field and isinstance(item, dict) else item
        if args.field and (not isinstance(item, dict) or args.field not in item):
            print(f"NOT_RUN line {number} has no field {args.field!r}")
            return 2
        total = compact_bytes(state) + args.question_bytes
        verdict = classify(total, band)
        counts[verdict] += 1
        if verdict != "FITS":
            key = item.get("task") or item.get("id") if isinstance(item, dict) else None
            flagged.append((verdict, key or f"line {number}", total))

    low, high = band
    print(
        f"limit {LIMIT} tokens; bytes/token band {low:.3f}-{high:.3f} from "
        f"{args.calibration.name}; FITS {counts['FITS']}, NEAR {counts['NEAR']}, OVER {counts['OVER']}"
    )
    for verdict, key, total in sorted(flagged, key=lambda f: -f[2]):
        print(
            f"{verdict}\t{key}\t{total} bytes\t~{round(total / high)}-{round(total / low)} tokens"
        )
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
