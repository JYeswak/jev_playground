#!/usr/bin/env python3
"""Does any number in a receipt map to a cited numeral by rounding and/or a power of ten?

Used by foundation/gates.d/95-numerals-ratchet.sh to check that a register row's CLASS does not
contradict the evidence file STATUS cites for it.

WHY THIS IS A SEPARATE FILE. The check was first written inline as a heredoc inside the stage. It is
called once per register row inside a `while read` loop, and an inline heredoc there is both harder to
test alone and blocked by this fleet's command guard as process substitution. A file can be run
directly against any receipt, which is what made the next paragraph possible.

WHAT IT ANSWERS, and nothing more:

  MAPS         some literal number in the file equals the target after rounding to the target's
               decimal places, optionally scaled by 10^k for k in -6..6
  NO_MAP       no single number does — consistent with a value DERIVED from several parts
  UNPARSEABLE  the cited numeral is not a number

IT DOES NOT answer whether a derivation is correct. 283.786 is the sum of sixteen per-repo kloc
floats; this script can only say that no single number in the receipt is 283 — it cannot know the
right sixteen fields were summed. I summed thirty-two of them earlier today and got 284.359, so that
judgment stays with a human and the gate says so out loud.

Env: JEV_N (cited numeral, as written), JEV_F (path to the evidence receipt).
"""

import os
import re
import sys

RE_NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def main() -> int:
    n = os.environ.get("JEV_N", "")
    path = os.environ.get("JEV_F", "")
    try:
        target = float(n)
    except ValueError:
        print("UNPARSEABLE")
        return 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            raw = fh.read()
    except OSError as exc:
        print("UNPARSEABLE")
        print(f"# {exc}", file=sys.stderr)
        return 0

    # Decimals of the CITED form, not of the stored value: "76.25" is two, so 0.7624955... scaled by
    # 100 rounds to 76.25 and maps, while a value that only agrees at one decimal does not.
    dec = len(n.split(".", 1)[1]) if "." in n else 0
    want = round(target, dec)

    for m in RE_NUM.finditer(raw):
        try:
            v = float(m.group(0))
        except ValueError:
            continue
        for k in range(-6, 7):
            if round(v * (10.0**k), dec) == want:
                print("MAPS")
                return 0
    print("NO_MAP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
