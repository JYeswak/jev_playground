#!/usr/bin/env python3
"""Arms for verify-reason-numerals.sh. Copies only — the real STATUS is never written.

  ARM 1  numeral present in receipt                      -> rc=0   (known-good pair)
  ARM 2  numeral absent from receipt                     -> rc=12  (known-bad pair)
  ARM 3  thousands separator folded (283786 ~ 283,786)   -> rc=0   (same citation, not a new claim)
  ARM 4  ROUNDING NOT folded (0.045 vs 0.0447)           -> rc=12  (the DOCUMENTED limitation is
                                                                    real, not aspirational)
  ARM 5  single digits ignored (4of5, T1)                -> rc=0   (a detector that fires on every
                                                                    row discriminates nothing)
  ARM 6  absent receipt reported ONCE, not per numeral   -> rc=12  (lane-status owns absence)

ARM 4 exists because the docstring CLAIMS rounding is not folded. A documented limitation with no
arm is a promise, and this lane has caught itself shipping those: a witness that passes by
construction, an assertion that cannot observe the next change, a guard that exists only as prose.

EXIT  0 all arms discriminate · 1 an arm failed · 2 usage/environment error
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(os.environ.get("JEV_REPO", Path(__file__).resolve().parent.parent))
GATE = REPO / "scripts" / "verify-reason-numerals.sh"

HEADER = ("candidate\trung\tscore\tverdict\tauthor\treceipt\treason\tconcurrence\tdigest\t"
          "receipt_type")


def row(cand, receipt, reason):
    return f"{cand}\t4\t500\tRULED_OUT\tpane2\t{receipt}\t{reason}\tnone\tdeadbeefdeadbeef\tmeasurement"


def run(tmp: Path, receipt_rel: str, reason: str, receipt_body):
    """Build a private repo root with one row and (optionally) its receipt, then run the gate."""
    root = Path(tempfile.mkdtemp(dir=tmp))
    (root / "docs/demos").mkdir(parents=True)
    if receipt_body is not None:
        p = root / receipt_rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(receipt_body)
    status = root / "docs/demos/STATUS.tsv"
    status.write_text(HEADER + "\n" + row("arm-candidate", receipt_rel, reason) + "\n")
    r = subprocess.run([str(GATE)], capture_output=True, text=True,
                       env=dict(os.environ, JEV_REPO=str(root), JEV_STATUS=str(status)))
    return r.returncode, r.stdout


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="jev-reason-numerals-"))
    fail = 0

    def arm(name, want_rc, receipt_rel, reason, body, want_text=None):
        nonlocal fail
        rc, out = run(tmp, receipt_rel, reason, body)
        ok = rc == want_rc and (want_text is None or want_text in out)
        tag = "PASS" if ok else "FAIL"
        note = f"rc={rc}"
        if not ok:
            note += f" want={want_rc}" + (f" missing {want_text!r}" if want_text else "")
        print(f"{tag}  {name:<52} {note}")
        if not ok:
            fail += 1

    rel = "runs/arm-receipt.json"
    arm("ARM 1 numeral present in receipt", 0, rel, "died-rung4-0.047pct",
        json.dumps({"savings_pct": 0.047}))
    arm("ARM 2 numeral absent from receipt", 12, rel, "died-rung4-0.047pct",
        json.dumps({"savings_pct": 0.999}), want_text="UNOPENABLE")
    arm("ARM 3 thousands separator folded", 0, rel, "denominator-283786-KLOC",
        json.dumps({"kloc": "283,786"}))
    arm("ARM 4 ROUNDING NOT folded", 12, rel, "lift-0.045pct",
        json.dumps({"exact": 0.0447}), want_text="UNOPENABLE")
    arm("ARM 5 single digits ignored", 0, rel, "no-jev-stage-4of5-T1-T2",
        json.dumps({"unrelated": True}))

    rc, out = run(tmp, rel, "died-0.047pct-and-283786-KLOC", None)
    hits = out.count("UNOPENABLE arm-candidate")
    if rc == 12 and hits == 1 and "<receipt absent>" in out:
        print(f"PASS  {'ARM 6 absent receipt reported once':<52} rc=12 one row, not per-numeral")
    else:
        print(f"FAIL  {'ARM 6 absent receipt reported once':<52} rc={rc} hits={hits}")
        fail += 1

    print("\n" + "-" * 70)
    print(f"fixtures under {tmp} (left in place; temp dir)")
    if fail:
        print(f"FAIL: {fail} arm(s) did not discriminate.")
        return 1
    print("OK: reason-numeral gate discriminates on all 6 arms; real STATUS never written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
