#!/usr/bin/env python3
"""selftest-other-reasons.sh — prove the sidecar verifier DISCRIMINATES.

WHY THIS FILE EXISTS, and it is the whole point: the five arms below were originally run from a
throwaway heredoc, and then DOCUMENTED IN GATES.md as though a committed suite existed. Pane 3's
registry audit (audit-gates-registry-20260918T110806Z.json, 85d75a0) caught it:

    "RED-ARM DESCRIPTION OVERSTATED — live verifier works, but the claimed '5 arms, each against
     copies via JEV_STATUS/JEV_SIDECAR' exist ONLY as pane-2 audit prose. No runnable suite, no
     --selftest mode, no arm file."

I overstated a RED arm inside the registry row I wrote to fix overstatement. An arm that ran once in
a shell and was never committed is not a witness — it is a memory of a witness, which is the exact
thing this lane replaced STATUS.tsv's prose with a machine-readable file to avoid.

EVERY ARM RUNS AGAINST COPIES via JEV_STATUS / JEV_SIDECAR. The real docs/demos/STATUS.tsv is never
written. That hook exists because an earlier attempt to prove ARM 5 briefly truncated the real file
and the SLB two-person guard refused the command — correctly, since restore-after is not safety in a
worktree three panes are reading.

  ARM 1  sidecar entry missing its own receipt_digest   -> DIGEST      rc=1
  ARM 2  sidecar digest disagrees with live bytes       -> DIGEST      rc=1  (names both values)
  ARM 3  entry missing per-entry assigned_by            -> PROVENANCE  rc=1
  ARM 4  CORROBORATING quote does not match its line    -> QUOTE       rc=1  (the field that had
                                                                              been carried unchecked)
  ARM 5  short STATUS row (7 cols)                      -> SCHEMA      rc=1  (failed, never skipped)
  ARM 6  untouched real files                           -> clean       rc=0

EXIT  0 all arms discriminate · 1 an arm failed · 2 usage/environment error
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(os.environ.get("JEV_REPO", Path(__file__).resolve().parent.parent))
VERIFIER = REPO / "scripts" / "verify-other-reasons.sh"
REAL_SIDE = REPO / "docs/demos/duel-2/runs/receipt-other-reasons.json"
REAL_STATUS = REPO / "docs/demos/STATUS.tsv"


def run(side=None, status=None):
    env = dict(os.environ)
    if side:
        env["JEV_SIDECAR"] = str(side)
    if status:
        env["JEV_STATUS"] = str(status)
    r = subprocess.run([str(VERIFIER)], capture_output=True, text=True, cwd=REPO, env=env)
    fails = [ln.strip()[5:] for ln in r.stdout.splitlines() if "FAIL " in ln]
    return r.returncode, fails


def main() -> int:
    if not VERIFIER.is_file() or not REAL_SIDE.is_file() or not REAL_STATUS.is_file():
        print("selftest-other-reasons: verifier or inputs missing", file=sys.stderr)
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="jev-other-reasons-"))
    base = REAL_SIDE.read_text()
    fail = 0

    def arm(label, want_rc, want_prefix, side=None, status=None):
        nonlocal fail
        rc, fails = run(side=side, status=status)
        hit = next((f for f in fails if f.startswith(want_prefix)), None)
        if rc == want_rc and hit:
            print(f"PASS  {label:<46} rc={rc} {hit[:72]}")
        else:
            print(f"FAIL  {label:<46} rc={rc}(want {want_rc}) "
                  f"{'no ' + want_prefix + ' failure' if not hit else ''}")
            fail += 1

    def side_with(mut):
        d = json.loads(base)
        mut(d)
        p = tmp / "side.json"
        p.write_text(json.dumps(d, indent=2))
        return p

    arm("ARM 1 entry lacks its own receipt_digest", 1, "DIGEST",
        side=side_with(lambda d: d["rows"][0].pop("receipt_digest", None)))
    arm("ARM 2 sidecar digest != live bytes", 1, "DIGEST",
        side=side_with(lambda d: d["rows"][0].update(receipt_digest="0" * 16)))
    arm("ARM 3 entry lacks assigned_by", 1, "PROVENANCE",
        side=side_with(lambda d: d["rows"][1].pop("assigned_by", None)))
    arm("ARM 4 corroborating quote does not match", 1, "QUOTE",
        side=side_with(lambda d: d["rows"][0].update(corroborating_quote="not the line")))

    lines = REAL_STATUS.read_text().splitlines()
    for i, ln in enumerate(lines):
        if ln.split("\t")[0].startswith("demo-3"):
            lines[i] = "\t".join(ln.split("\t")[:7])
            break
    short = tmp / "status.tsv"
    short.write_text("\n".join(lines) + "\n")
    arm("ARM 5 short STATUS row (7 cols)", 1, "SCHEMA", status=short)

    rc, fails = run()
    if rc == 0 and not fails:
        print(f"PASS  {'ARM 6 untouched real files':<46} rc=0 clean")
    else:
        print(f"FAIL  {'ARM 6 untouched real files':<46} rc={rc} {fails[:1]}")
        fail += 1

    print("\n" + "-" * 70)
    print(f"fixtures under {tmp} (left in place; temp dir)")
    if fail:
        print(f"FAIL: {fail} arm(s) did not discriminate.")
        return 1
    print("OK: sidecar verifier discriminates on all 6 arms; real files never written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
