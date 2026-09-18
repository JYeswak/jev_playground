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
  ARM 7  forced input movement                          -> TRANSIENT   rc=10 (and NO verdict text)
  ARM 8  manifest self-digest                           -> recompute   third party re-derives it
  ARM 9  snapshot copies re-hashed OFF DISK             -> fidelity    not the field claiming it

EXIT  0 all arms discriminate · 1 an arm failed · 2 usage/environment error
"""
import json
import os
import subprocess
import hashlib
import re
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

    # ---------------------------------------------- SNAPSHOT ARMS (pane 2 Q99 spec, 44feaf2)
    # Pane 2's Q97 promotion ledger listed FOUR preconditions; these arms are the witnesses for the
    # three it said were unmet or partial. A precondition with no arm is a claim, not a promotion.
    env = dict(os.environ, JEV_FORCE_MOVED="docs/demos/STATUS.tsv")
    r = subprocess.run([str(VERIFIER)], capture_output=True, text=True, env=env)
    leaked = ("OK: exact coverage" in r.stdout) or ("FAIL:" in r.stdout)
    if r.returncode == 10 and "TRANSIENT_UNSTABLE" in r.stdout and not leaked:
        print(f"PASS  {'ARM 7 verifier-owned TRANSIENT_UNSTABLE':<46} rc=10 no verdict leaked")
    else:
        # A verdict printed alongside a transient is the defect, not just the wrong code: it is what
        # let lane-status emit a full table for a run it had already decided was unjudgeable.
        print(f"FAIL  {'ARM 7 verifier-owned TRANSIENT_UNSTABLE':<46} rc={r.returncode} leaked={leaked}")
        fail += 1

    r = subprocess.run([str(VERIFIER)], capture_output=True, text=True)
    m = re.search(r"snapshot: (\S+)", r.stdout)
    if not m:
        print(f"FAIL  {'ARM 8 manifest self-digest recomputes':<46} no snapshot path emitted")
        print(f"FAIL  {'ARM 9 snapshot copy fidelity':<46} no snapshot path emitted")
        fail += 2
    else:
        man = json.loads((Path(m.group(1)) / "manifest.json").read_text())
        recorded = man.pop("manifest_digest", None)
        canon = json.dumps(man, sort_keys=True, separators=(",", ":")).encode()
        recomputed = hashlib.sha256(canon).hexdigest()[:16]
        if recorded and recorded == recomputed:
            print(f"PASS  {'ARM 8 manifest self-digest recomputes':<46} {recorded} third-party checkable")
        else:
            print(f"FAIL  {'ARM 8 manifest self-digest recomputes':<46} {recorded} != {recomputed}")
            fail += 1
        # COPY FIDELITY, not copy EXISTENCE. The manifest could record a path it never wrote, or
        # record a digest of the source while the copy diverged — so this reads the COPIED BYTES off
        # disk and re-hashes them, rather than trusting the field that claims they match.
        bad = []
        for f in man["files"]:
            sp = Path(f["snapshot_path"])
            if not sp.is_file():
                bad.append(f"{f['source_path']}: copy absent")
            elif hashlib.sha256(sp.read_bytes()).hexdigest()[:16] != f["source_pre_raw"]:
                bad.append(f"{f['source_path']}: copy bytes != source_pre_raw")
        if man["files"] and not bad:
            print(f"PASS  {'ARM 9 snapshot copy fidelity':<46} {len(man['files'])} copies re-hashed off disk")
        else:
            print(f"FAIL  {'ARM 9 snapshot copy fidelity':<46} {bad[:2]}")
            fail += 1

    # ------------------------------- ARMS FOR PANE 2'S Q100 FINDINGS (c9ddb0f, 4ceec76)
    # Both of these were DEFECTS I SHIPPED and pane 2 found by attacking claims I asked it to attack.
    # An arm for each, so neither can return silently.

    # ARM 10 — absolute inputs must not escape the private snapshot root. Pane 2: "absolute env
    # inputs escape private root". Mechanism: Path("/a")/"/tmp/x" == "/tmp/x", so the copy mapped the
    # source ONTO ITSELF and the verifier read live while reporting a snapshot.
    abs_side = Path(tempfile.mkdtemp()) / "abs-sidecar.json"
    abs_side.write_text(REAL_SIDE.read_text())
    r = subprocess.run([str(VERIFIER)], capture_output=True, text=True,
                       env=dict(os.environ, JEV_SIDECAR=str(abs_side)))
    m = re.search(r"snapshot: (\S+)", r.stdout)
    if m:
        man = json.loads((Path(m.group(1)) / "manifest.json").read_text())
        escaped = [f["source_path"] for f in man["files"]
                   if not f["snapshot_path"].startswith(m.group(1))
                   or f["snapshot_path"] == f["source_path"]]
        if not escaped:
            print(f"PASS  {'ARM 10 absolute input contained in root':<46} 0 of {len(man['files'])} escaped")
        else:
            print(f"FAIL  {'ARM 10 absolute input contained in root':<46} escaped: {escaped[:2]}")
            fail += 1
    else:
        print(f"FAIL  {'ARM 10 absolute input contained in root':<46} no snapshot path emitted")
        fail += 1

    # ARM 11 — the test hook must NOT be able to mask a durable RED. Pane 2: "JEV_FORCE_MOVED cannot
    # create PASS but CAN SUPPRESS DURABLE RED into TRANSIENT_UNSTABLE". I had committed the claim
    # that it was fail-safe by construction TWICE. It is now refused on a dirty verdict, and this arm
    # is the witness: a known-bad sidecar plus the hook must stay rc=1, never rc=10.
    bad_side = Path(tempfile.mkdtemp()) / "dirty-sidecar.json"
    d = json.loads(REAL_SIDE.read_text())
    d["rows"][0].pop("assigned_by", None)
    bad_side.write_text(json.dumps(d, indent=2))
    r = subprocess.run([str(VERIFIER)], capture_output=True, text=True,
                       env=dict(os.environ, JEV_SIDECAR=str(bad_side),
                                JEV_FORCE_MOVED="docs/demos/STATUS.tsv"))
    if r.returncode == 1 and "REFUSED" in r.stdout and "TRANSIENT_UNSTABLE" not in r.stdout:
        print(f"PASS  {'ARM 11 hook cannot mask a durable RED':<46} rc=1 refused, not laundered to 10")
    else:
        print(f"FAIL  {'ARM 11 hook cannot mask a durable RED':<46} rc={r.returncode} "
              f"refused={'REFUSED' in r.stdout} transient={'TRANSIENT_UNSTABLE' in r.stdout}")
        fail += 1

    # ------------------- ARMS FOR PANE 2'S Q103 FINDINGS (audit-q103-fixes, audit-q103-promotion)
    # Pane 2 DEFERRED PROMOTION A THIRD TIME on exactly these two gaps. Each gets a witness.

    # ARM 12 — an outward-pointing symlink must be REJECTED, not followed. Pane 2:
    # "Path.is_file() FOLLOWS a symlink and read_bytes() COPIES THE TARGET BYTES ... the snapshot then
    # contains OUTWARD-TARGET BYTES UNDER AN APPARENTLY IN-ROOT source_path." `contained()` was
    # lexical: it fixed where bytes LAND, not where they COME FROM.
    sym_root = Path(tempfile.mkdtemp())
    (sym_root / "docs/demos").mkdir(parents=True)
    (sym_root / "runs").mkdir(parents=True)
    outside = Path(tempfile.mkdtemp()) / "external.json"
    outside.write_text(json.dumps({"other_reason": "design"}))
    (sym_root / "runs/link.json").symlink_to(outside)
    hdr = "\t".join(["candidate", "rung", "score", "verdict", "author", "receipt", "reason",
                     "concurrence", "digest", "receipt_type"])
    srow = "\t".join(["sym-cand", "4", "500", "RULED_OUT", "pane2", "runs/link.json", "died",
                      "none", "deadbeefdeadbeef", "other"])
    sstat = sym_root / "docs/demos/STATUS.tsv"
    sstat.write_text(hdr + "\n" + srow + "\n")
    sside = sym_root / "side.json"
    sside.write_text(json.dumps({"rows": []}))
    r = subprocess.run([str(VERIFIER)], capture_output=True, text=True, cwd=str(sym_root),
                       env=dict(os.environ, JEV_REPO=str(sym_root), JEV_STATUS=str(sstat),
                                JEV_SIDECAR=str(sside)))
    if r.returncode == 13 and "SYMLINK ESCAPE" in r.stdout:
        print(f"PASS  {'ARM 12 outward symlink rejected':<46} rc=13 not followed, not snapshotted")
    else:
        print(f"FAIL  {'ARM 12 outward symlink rejected':<46} rc={r.returncode} "
              f"escape_named={'SYMLINK ESCAPE' in r.stdout}")
        fail += 1

    # ARM 13 — forced movement must be recorded IN THE MANIFEST, not only on stdout. Pane 2: "a SAVED
    # MANIFEST ALONE CANNOT DISTINGUISH AN OBSERVED MOVEMENT FROM A FORCED TEST CLASSIFICATION ...
    # transparent during execution but NOT FULLY EVIDENCE-CARRYING AFTER THE RUN."
    r = subprocess.run([str(VERIFIER)], capture_output=True, text=True,
                       env=dict(os.environ, JEV_FORCE_MOVED="docs/demos/STATUS.tsv"))
    mm = re.search(r"manifest: (\S+)/manifest\.json", r.stdout)
    if mm:
        mv = json.loads((Path(mm.group(1)) / "manifest.json").read_text())["movement"]
        if mv.get("forced") is True and mv.get("forced_reason") and mv.get("moved_paths"):
            print(f"PASS  {'ARM 13 manifest carries forced provenance':<46} forced=True + reason + paths")
        else:
            print(f"FAIL  {'ARM 13 manifest carries forced provenance':<46} {mv}")
            fail += 1
    else:
        print(f"FAIL  {'ARM 13 manifest carries forced provenance':<46} no manifest path emitted")
        fail += 1

    # ARM 14 — is_symlink must not fire on ordinary relative paths. The FIRST predicate here was
    # `realpath != source_path`, true for EVERY relative path, so it reported is_symlink on all 19
    # inputs. Caught by opening the manifest rather than trusting the field.
    r = subprocess.run([str(VERIFIER)], capture_output=True, text=True)
    m3 = re.search(r"snapshot: (\S+)", r.stdout)
    if m3:
        fs = json.loads((Path(m3.group(1)) / "manifest.json").read_text())["files"]
        bogus = [f["source_path"] for f in fs if f["is_symlink"]]
        if not bogus:
            print(f"PASS  {'ARM 14 is_symlink does not fire on relatives':<46} 0 of {len(fs)} flagged")
        else:
            print(f"FAIL  {'ARM 14 is_symlink does not fire on relatives':<46} {bogus[:2]}")
            fail += 1
    else:
        print(f"FAIL  {'ARM 14 is_symlink does not fire on relatives':<46} no snapshot path emitted")
        fail += 1

    print("\n" + "-" * 70)
    print(f"fixtures under {tmp} (left in place; temp dir)")
    if fail:
        print(f"FAIL: {fail} arm(s) did not discriminate.")
        return 1
    print("OK: sidecar verifier discriminates on all 14 arms; real files never written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
