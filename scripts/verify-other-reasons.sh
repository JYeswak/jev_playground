#!/usr/bin/env python3
"""verify-other-reasons.sh — verifier for the `other_reason` sidecar.

SPEC: docs/demos/duel-2/SPEC_other_reason_COD.md (047fed2), pane 2 as the enum's author.

WHAT THE SPEC REQUIRES, and each is checked below:
  - EXACT coverage of the `other` rows in STATUS.tsv — not "at least", not "non-empty"
  - binding by candidate + receipt path + NORMALISED DIGEST
  - reason drawn from {design, mapping, unresolved, mixed}
  - an opened-content evidence locator, resolvable by a third party
  - assigner and time recorded

WHAT IT MUST NOT DO, quoted from the spec: "enables audit/vocabulary review but NO GATE BEHAVIOR."
So this script is a STANDALONE verifier. `lane-status.sh` does not read the sidecar, and nothing in
the lane's exit codes depends on it. That separation is the ruling, not an implementation detail —
pane 2 declined a schema column precisely so this data could not leak into gate behaviour.

DIGEST CONVENTION is deliberately the SAME as STATUS.tsv column 9: strip the final run of terminal
whitespace, then sha256, first 16 hex. The spec warned against inventing a second identity, and the
lane already learned from `command_sha256` that a second key is a defect, not a convenience.

EXIT  0 clean · 1 verification failure · 2 usage/environment error
"""
import hashlib
import json
import re
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# TEST HOOKS. `lane-status.sh` already carries a JEV_STATUS hook, and its comment says why: so the
# RED arms can be proven to DISCRIMINATE "without mutating the shared worktree, which three panes are
# reading." This verifier shipped without one, and the omission was caught the hard way — an arm
# script that briefly truncated the real docs/demos/STATUS.tsv to test the short-row path was
# REFUSED by the SLB two-person guard. The guard was right: restore-after is not safety in a shared
# tree, because another pane can read or commit inside the window. A verifier whose known-bad arms
# require mutating production state is a verifier that will not be tested.
STATUS = Path(os.environ.get("JEV_STATUS", "docs/demos/STATUS.tsv"))
SIDECAR = Path(os.environ.get("JEV_SIDECAR", "docs/demos/duel-2/runs/receipt-other-reasons.json"))
# The containment boundary for snapshot copies. Same JEV_REPO hook the sibling instruments use, so
# arms can point it at a private root instead of mutating the real tree.
REPO = Path(os.environ.get("JEV_REPO", Path(__file__).resolve().parent.parent))
ALLOWED = {"design", "mapping", "unresolved", "mixed"}


def norm_digest(path: Path) -> str:
    data = path.read_bytes()
    stripped = re.sub(rb"\s+\Z", b"", data)
    return hashlib.sha256(stripped).hexdigest()[:16]

# ------------------------------------------------ SNAPSHOT + MANIFEST (pane 2 Q99 spec, 44feaf2)
# Pane 2's Q97 ledger blocked promotion of this verifier on four preconditions; copy/snapshot and the
# revision/hash pair were the unmet ones it could specify, and Q99 specified them. The design decision
# I could not duck — STATUS references receipts BY PATH, so copying STATUS without rewriting paths
# leaves the verifier reading LIVE receipts and the snapshot cosmetic — was ruled:
#
#   "PRESERVE original STATUS/sidecar bytes and receipt paths; copy into private SNAPSHOT_ROOT/files;
#    RESOLVER maps original relative paths to snapshot paths WITHOUT REWRITING EVIDENCE."
#
# So the evidence bytes are never altered: a third party recomputes the same digests over the same
# bytes. Only the READ is redirected.
def contained(root: Path, p) -> Path:
    """Map any path INTO root/files, so nothing can escape the private snapshot root.

    PANE 2 FOUND THIS, Q100 clause audit (audit-q100-contract-20260918T131500Z.json, 4ceec76):
    "preserved MET for relative production paths but ABSOLUTE ENV INPUTS ESCAPE PRIVATE ROOT."

    The mechanism is a Python join rule I did not check: `Path("/a/b") / "/tmp/x"` is `/tmp/x` — an
    absolute right operand DISCARDS the left. So `root/"files"/Path("/tmp/st.tsv")` was `/tmp/st.tsv`:
    the copy wrote the source back onto itself, `mapped` recorded the LIVE path, and the verifier read
    live inputs while reporting a snapshot. With JEV_STATUS pointed at an absolute fixture — which is
    exactly how I tested the transient class — THE SNAPSHOT SILENTLY DID NOT HAPPEN.

    `..` escapes too (`root/"files"/"../../etc/x"`), which pane 2's own spec had listed under
    "re-examine on path expansion, traversal/symlink". Both are dropped here, anchor and all.
    """
    parts = [x for x in Path(p).parts if x not in (os.sep, "/", "..", "")]
    return root / "files" / Path(*parts) if parts else root / "files"


def snapshot(paths, root: Path, boundary: Path):
    """Copy each path into root/files/<original path>. Returns (mapped, rejected, realpaths).

    SYMLINK ESCAPE, found by pane 2 (audit-q103-fixes-20260918T134500Z.json):
    "LEXICAL_CONTAINMENT_MET_SYMLINK_CONTAINMENT_NOT_MET ... Path.is_file() FOLLOWS a symlink and
    read_bytes() COPIES THE TARGET BYTES. An inward-looking path inside the repository can point
    outside it; the implementation does not reject symlinks or verify realpath containment. The
    snapshot then contains OUTWARD-TARGET BYTES UNDER AN APPARENTLY IN-ROOT source_path."

    `contained()` was lexical only — it fixed where bytes LAND, not where they COME FROM. I had told
    pane 2 I expected this gap was live and had not handled it; it confirmed with the mechanism.

    `boundary` is the repo root. A path that RESOLVES outside it is rejected rather than copied, so
    the snapshot cannot carry an unapproved external object behind an in-repo-looking name. Paths
    supplied directly by JEV_STATUS/JEV_SIDECAR/__file__ are exempt: they are the caller's declared
    inputs, not receipt references discovered inside evidence.
    """
    mapped, rejected, realpaths = {}, [], {}
    bound = boundary.resolve()
    for p in paths:
        src = Path(p)
        if not src.is_file():
            continue
        real = src.resolve()
        realpaths[str(src)] = {"realpath": str(real), "is_symlink": src.is_symlink()}
        declared = str(src) in {str(STATUS), str(SIDECAR), str(Path(__file__).resolve())}
        escapes = bound not in real.parents and real != bound
        if not declared and escapes:
            rejected.append((str(src), str(real)))
            continue
        dst = contained(root, src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        mapped[str(src)] = dst
    return mapped, rejected, realpaths


def manifest_for(mapped, pre, post, attempts, head, realpaths=None, moved=(), forced=False):
    """Everything a third party needs to re-derive that the snapshot matched the source."""
    files = []
    for orig, snap in sorted(mapped.items()):
        b = snap.read_bytes()
        files.append({
            "source_path": orig,
            "snapshot_path": str(snap),
            "bytes": len(b),
            "source_pre_raw": pre.get(orig),
            "source_post_raw": post.get(orig),
            "copy_raw": hashlib.sha256(b).hexdigest()[:16],
            "norm": norm_digest(snap),
            # REALPATH IS EVIDENCE. Pane 2's symlink finding means source_path alone can look in-root
            # while the bytes came from outside; recording where each path actually resolved lets a
            # third party check containment instead of trusting that it was checked.
            # `realpath != source_path` was the FIRST predicate here and it was WRONG: it is true
            # for EVERY relative path, so it reported is_symlink on all 19 inputs. Caught by opening
            # the manifest instead of trusting the field — a predicate satisfiable by an unrelated
            # condition, which is the defect class this lane has now caught six times in its own
            # instruments. `Path.is_symlink()` is asked at capture time, where the answer exists.
            "source_realpath": (realpaths or {}).get(orig, {}).get("realpath"),
            "is_symlink": (realpaths or {}).get(orig, {}).get("is_symlink", False),
        })
    # THE INSTRUMENT, CALLED OUT BY NAME. It is already in `files` because it is an input now, but an
    # outsider should not have to know which of 19 rows is the executable. Pane 2's ledger graded this
    # PARTIALLY_BOUND: "records source HEAD and spec references, but does not contain the verifier
    # source or a content digest of the verifier itself."
    me = str(Path(__file__).resolve())
    mine = next((f for f in files if f["source_path"] == me), None)
    payload = {
        "schema": "jev.snapshot-manifest.v1",
        "spec": "docs/demos/duel-2/SPEC_snapshot_manifest_COD.md (44feaf2)",
        # PANE 2 ANSWERED THE QUESTION I ASKED IT (audit-q103-source-head-20260918T135500Z.json,
        # 1ea965e). I had offered to DELETE this field: its outsider rerun reached the verdict with
        # source_head=no-head, so what is it load-bearing for? Its ruling: "NOT required for
        # data-level evidence verdict ... but IS load-bearing provenance: pins intended repository
        # revision and SEPARATES IDENTICAL EVIDENCE CAPTURED UNDER DIFFERENT CODE. HEAD alone is not
        # working-tree identity; per-file hashes cover dirty inputs. Keep source_head, LABEL
        # PROVENANCE NOT VERDICT INPUT." Labelled, so the next reader cannot mistake it for one.
        "source_head": head,
        "source_head_role": ("provenance only — NOT a verdict input; per-file hashes cover dirty "
                             "inputs, and a no-head capture still yields a valid evidence verdict"),
        "capture_attempts": attempts,
        # MOVEMENT PROVENANCE, IN THE ARTIFACT THAT OUTLIVES THE RUN. Pane 2, audit-q103-fixes
        # (c9ddb0f): "the manifest records movement and hashes but does not record forced=true/reason.
        # A SAVED MANIFEST ALONE CANNOT DISTINGUISH AN OBSERVED MOVEMENT FROM A FORCED TEST
        # CLASSIFICATION ... transparent during execution but NOT FULLY EVIDENCE-CARRYING AFTER THE
        # RUN." That last phrase is the whole standard this verifier exists to meet.
        "movement": {
            "moved_paths": list(moved),
            "forced": bool(forced),
            "forced_reason": "JEV_FORCE_MOVED test hook" if forced else None,
            "note": ("at least one movement was FORCED by a test hook, not observed; equal "
                     "source_pre_raw/source_post_raw on a moved path is the signature")
            if forced else "all movements, if any, were observed",
        },
        "verifier": {
            "source_path": me,
            "snapshot_path": mine["snapshot_path"] if mine else None,
            "digest": mine["copy_raw"] if mine else None,
            "bundled": bool(mine),
            "note": "execute THIS copy, not the live checkout, to reproduce the verdict",
        },
        "files": files,
    }
    # SELF-DIGEST over the canonical payload EXCLUDING the digest field, per the spec. A manifest
    # nobody can check is the same as a receipt nobody can check.
    canon = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["manifest_digest"] = hashlib.sha256(canon).hexdigest()[:16]
    return payload

def run_once(status_p: Path, sidecar_p: Path, resolve):
    """The verification body. Reads ONLY through `resolve`, so it is snapshot-agnostic."""
    return _verify(status_p, sidecar_p, resolve)


def main() -> int:
    if not STATUS.exists() or not SIDECAR.exists():
        print(f"verify-other-reasons: missing {STATUS if not STATUS.exists() else SIDECAR}",
              file=sys.stderr)
        return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True
                          ).stdout.strip() or "no-head"

    # BOUNDED AT TWO CAPTURES, the same contract lane-status uses. A first source change triggers one
    # recapture; a stable second capture is verified EVEN IF RED; a second change is TRANSIENT_UNSTABLE
    # at exit 10 with NO VERDICT. Pane 2's Q97 named a verifier-owned transient class as the fourth
    # unmet precondition, and "lane-status rc10 DOES NOT TRANSFER" — so this one is its own.
    for attempt in (1, 2):
        # THE INSTRUMENT IS AN INPUT. Pane 2's outsider rerun (audit-q100-outsider-20260918T132000Z
        # .json, 86420cb) proved the snapshot is NOT cosmetic — it reached the evidence verdict from
        # the copies alone, with source_head=no-head — and then named the one live dependency left:
        # "the snapshot does not bundle or hash verify-other-reasons.sh, so exact automatic rerun
        # needs that code at source revision or a bundled artifact." Its ledger graded the
        # verifier/spec binding PARTIALLY_BOUND for exactly that reason.
        #
        # Binding it buys a second thing for free: the verifier is now covered by its OWN movement
        # check, so editing this file mid-run is a TRANSIENT rather than a silent splice — which is
        # the protection lane-status.sh gained at exit 11 and this verifier did not have.
        inputs = [str(STATUS), str(SIDECAR), str(Path(__file__).resolve())]
        for line in STATUS.read_text().splitlines():
            f = line.split("\t")
            if line and not line.startswith("#") and f[0] != "candidate" and len(f) >= 10:
                inputs.append(f[5])
        pre = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]
               for p in inputs if Path(p).is_file()}
        root = Path(tempfile.mkdtemp(prefix="jev-snap-"))
        mapped, rejected, realpaths = snapshot(inputs, root, REPO)
        if rejected:
            # A REJECTED SYMLINK IS A DURABLE FAILURE, NOT A TRANSIENT. Pane 2: the snapshot would
            # otherwise "admit an unapproved external source object" behind an in-root-looking
            # source_path. That is a defect in the evidence, so it gets a verdict — not "no verdict".
            print("SYMLINK ESCAPE: cited evidence resolves outside the repository boundary.")
            for src, real in rejected:
                print(f"  rejected: {src}  ->  {real}")
            print(f"  boundary: {REPO.resolve()}")
            print(f"REJECTED: {len(rejected)} path(s) not snapshotted; no verdict is issued on them.")
            return 13
        # NEVER FALL BACK TO A LIVE PATH. Found by reading pane 2's OWN re-open condition — "no live
        # shared path is read after the snapshot is declared complete" — against my implementation:
        # `mapped.get(str(p), Path(p))` returned the LIVE path for anything not copied, and
        # `snapshot()` skips paths absent at capture. So a receipt that did not exist at capture but
        # APPEARED MID-RUN would have been read live and verified — bytes that were never
        # snapshotted, passing a check the manifest cannot account for. Unmapped paths now resolve
        # INTO the snapshot root, where they are absent, so "absent at capture" stays absent.
        def resolve(p, _m=mapped, _r=root):
            return _m.get(str(p)) or contained(_r, p)
        rc, report = _verify(resolve(STATUS), resolve(SIDECAR), resolve)
        post = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]
                for p in inputs if Path(p).is_file()}
        moved = sorted(p for p in pre if pre[p] != post.get(p))
        # DETERMINISTIC KNOWN-BAD HOOK, same pattern as lane-status's JEV_SELF_DIGEST_OVERRIDE:
        # racing a mid-run mutation against a ~0.3s verify proved nothing THREE times, and tuning the
        # sleep until it passed would be a witness that passes by construction. It cannot manufacture
        # a PASS. It COULD mask a RED — pane 2 falsified my "fail-safe by construction" claim below —
        # so that hole is now closed structurally rather than asserted. TEST-ONLY either way.
        forced = False
        if os.environ.get("JEV_FORCE_MOVED"):
            # PANE 2 FALSIFIED MY CLAIM, Q100-U2 (audit-q100-arms-20260918T130000Z.json, c9ddb0f):
            # "JEV_FORCE_MOVED cannot create PASS but CAN SUPPRESS DURABLE RED into
            # TRANSIENT_UNSTABLE, so test-only." I had committed "fail-safe by construction: it can
            # only manufacture a false TRANSIENT, never a false pass" TWICE — and a hook that can
            # convert a real FAIL into "no verdict" is not fail-safe, it is a RED-masking hook. I
            # asked pane 2 to falsify that claim and it did.
            #
            # So the guarantee is now STRUCTURAL rather than asserted: the hook is REFUSED whenever
            # the underlying verdict is not clean. It cannot suppress what it cannot reach.
            if rc != 0:
                print(f"JEV_FORCE_MOVED REFUSED: underlying verdict is rc={rc}, not clean. "
                      f"The hook may not convert a durable failure into a transient.")
            else:
                moved = sorted(set(moved) | {os.environ["JEV_FORCE_MOVED"]})
                forced = True
        # MANIFEST IS GENERATED HERE, AFTER `forced` IS KNOWN. Pane 2 (audit-q103-fixes, c9ddb0f):
        # "forced=true disclosure is STDOUT-ONLY, NOT MANIFEST-BOUND ... a saved manifest alone
        # cannot distinguish an observed movement from a forced test classification." It was written
        # before the classification existed, so it could not have carried it. The manifest is the
        # artifact that outlives the run, so the run's provenance has to be IN it, not beside it.
        man = manifest_for(mapped, pre, post, attempt, head, realpaths, moved, forced)
        (root / "manifest.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n")
        if not moved:
            print(report, end="")
            print(f"  snapshot: {root}  manifest_digest: {man['manifest_digest']}")
            print(f"  source HEAD {head[:7]}, capture attempt {attempt} of max 2, inputs {len(pre)}")
            return rc
        if attempt == 2:
            print("TRANSIENT_UNSTABLE: source inputs moved during BOTH captures. NO VERDICT.")
            for p in moved:
                # PANE 2 RULED AGAINST MY OTHER CLAIM, same receipt: "moved equal-digest line is NOT
                # self-disclosing; add forced=true/reason." I had argued that printing identical
                # pre/post digests self-discloses a forced classification. It does not — it requires
                # the reader to notice two hex strings are equal AND to know what that implies, which
                # is an inference, not a disclosure. Marked explicitly now.
                mark = ""
                if forced and p == os.environ.get("JEV_FORCE_MOVED"):
                    mark = "   forced=true reason=JEV_FORCE_MOVED (test hook; digests are EQUAL)"
                print(f"  moved: {p}  {pre[p]} -> {post.get(p)}{mark}")
            if forced:
                print("  NOTE: at least one movement was FORCED by a test hook, not observed.")
            print(f"  manifest: {root}/manifest.json (records both source_pre and source_post)")
            return 10
        print(f"SNAPSHOT MOVED during capture 1 ({len(moved)} input(s)) — recapturing once, bounded.")
    return 2


def _verify(STATUS: Path, SIDECAR: Path, resolve) -> int:

    # GAP 4 REPAIRED — pane 2, audit-other-reasons-impl-20260918T110000Z.json (c2ae376):
    # "malformed STATUS rows <10 silently skipped". `continue` on a short row made it DISAPPEAR from
    # the `other` census instead of failing, so a truncated row could hide an uncovered `other`. That
    # is the same MASKING defect pane 2 caught in lane-status's exit chain — reproduced inside a
    # verifier written to catch defects. Short rows are now a failure, not a skip.
    other_rows, malformed = {}, []
    for lineno, line in enumerate(STATUS.read_text().splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if f[0] == "candidate":
            continue
        if len(f) < 10:
            malformed.append((lineno, f[0], len(f)))
            continue
        if f[9] == "other":
            other_rows[f[0]] = (f[5], f[8])  # receipt path, pinned digest

    side = json.loads(SIDECAR.read_text())
    rows = {r["candidate"]: r for r in side.get("rows", [])}
    fails = []

    # EXACT coverage, both directions. "At least" is not what the spec says.
    missing = sorted(set(other_rows) - set(rows))
    extra = sorted(set(rows) - set(other_rows))
    for c in missing:
        fails.append(f"UNCOVERED: STATUS row {c} is type `other` with no sidecar entry")
    for c in extra:
        fails.append(f"SPURIOUS: sidecar entry {c} is not a type-`other` STATUS row")

    for cand, row in sorted(rows.items()):
        if cand not in other_rows:
            continue
        status_receipt, status_digest = other_rows[cand]
        if row.get("receipt") != status_receipt:
            fails.append(f"BINDING: {cand} receipt {row.get('receipt')} != STATUS {status_receipt}")
        reason = row.get("other_reason")
        if reason not in ALLOWED:
            fails.append(f"REASON: {cand} has '{reason}', not in {sorted(ALLOWED)}")
        # READ THROUGH THE RESOLVER, so the bytes verified are the SNAPSHOT copy while the recorded
        # path stays the ORIGINAL — "resolver maps original relative paths to snapshot paths WITHOUT
        # REWRITING EVIDENCE" (Q99). A third party recomputes the same digest over the same bytes.
        p = resolve(Path(row.get("receipt", "")))
        if not p.is_file():
            fails.append(f"ABSENT: {cand} receipt {p} does not exist")
        else:
            live = norm_digest(p)
            if status_digest and live != status_digest:
                fails.append(f"DIGEST: {cand} live {live} != STATUS pin {status_digest}")
        # GAP 1 REPAIRED: the entry must carry its OWN digest, not borrow STATUS's. Pane 2: "sidecar
        # entries omit their own receipt_digest (bind via STATUS only)." Without it the sidecar has no
        # independent record, so a silently re-pinned STATUS would drag the sidecar along with it.
        # Now a THREE-WAY check: sidecar == live == STATUS pin.
        side_digest = row.get("receipt_digest")
        if not side_digest:
            fails.append(f"DIGEST: {cand} sidecar entry carries no receipt_digest of its own")
        elif p.is_file():
            if side_digest != norm_digest(p):
                fails.append(f"DIGEST: {cand} sidecar {side_digest} != live {norm_digest(p)}")
            elif status_digest and side_digest != status_digest:
                fails.append(f"DIGEST: {cand} sidecar {side_digest} != STATUS pin {status_digest}")
        # GAP 2 REPAIRED: per-entry provenance, not only file-level. Pane 2: "per-entry
        # assigned_by/assigned_at absent (top-level only)."
        for k in ("assigned_by", "assigned_at"):
            if not row.get(k):
                fails.append(f"PROVENANCE: {cand} entry lacks '{k}'")
        # A locator a third party cannot resolve is a citation only its author can check — the
        # defect this lane has recorded eight times under "open the cited control".
        #
        # GAP 3 REPAIRED: the corroborating locator is now checked too. Pane 2: "corroborating
        # locators/quotes unchecked." I had SHIPPED A FIELD THE VERIFIER IGNORED, which is the
        # data-shaped form of a guard that exists only as prose — the defect that made COD-H2's rung 4
        # UNASKABLE, committed inside the verifier built to enforce evidence.
        def check_locator(kind, loc, quote):
            if not loc or not quote:
                fails.append(f"LOCATOR: {cand} lacks a {kind} locator or quote")
                return
            if not p.is_file():
                return
            if p.suffix == ".md":
                m = re.search(r":(\d+)$", loc)
                if not m:
                    fails.append(f"LOCATOR: {cand} {kind} markdown locator '{loc}' has no line number")
                    return
                lines = p.read_text().splitlines()
                n = int(m.group(1))
                if not (1 <= n <= len(lines)):
                    fails.append(f"LOCATOR: {cand} {kind} line {n} out of range ({len(lines)} lines)")
                elif quote.strip() not in lines[n - 1]:
                    fails.append(f"QUOTE: {cand} {kind} line {n} does not contain the cited quote")
            elif p.suffix == ".json":
                field = loc.split("$.")[-1] if "$." in loc else None
                blob = json.loads(p.read_text())
                if field is None or field not in blob:
                    fails.append(f"LOCATOR: {cand} {kind} json locator '{loc}' names no present field")
                elif quote.strip() not in str(blob[field]):
                    fails.append(f"QUOTE: {cand} {kind} field {field} lacks the cited quote")

        check_locator("primary", row.get("evidence_locator", ""), row.get("evidence_quote", ""))
        if row.get("corroborating_locator") or row.get("corroborating_quote"):
            check_locator("corroborating", row.get("corroborating_locator", ""),
                          row.get("corroborating_quote", ""))

    for key in ("assigner", "generated_at", "gate_behavior", "digest_convention"):
        if not side.get(key):
            fails.append(f"PROVENANCE: sidecar lacks '{key}'")
    for lineno, cand, n in malformed:
        fails.append(f"SCHEMA: STATUS line {lineno} ({cand}) has {n} columns, want >=10 — "
                     f"a short row cannot be censused and must not be skipped")

    # The report is RETURNED, not printed, so main() can withhold it when a capture was unstable.
    # Printing mid-verification is what made lane-status emit a full table before deciding the run
    # was unjudgeable; here the verdict text never escapes an unstable capture.
    out = ["OTHER_REASON SIDECAR  (documentation only — no gate reads this file)\n"]
    out.append(f"  STATUS rows typed `other`: {len(other_rows)}   sidecar entries: {len(rows)}\n")
    out.append(f"  allowed reasons: {'|'.join(sorted(ALLOWED))}\n")
    used = sorted({r.get('other_reason') for r in rows.values()})
    out.append(f"  reasons used: {'|'.join(x for x in used if x)}   unused: "
               f"{'|'.join(sorted(ALLOWED - set(used)))}\n")
    if fails:
        for f in fails:
            out.append(f"  FAIL {f}\n")
        out.append(f"FAIL: {len(fails)} verification failure(s).\n")
        return 1, "".join(out)
    out.append("OK: exact coverage, bindings match STATUS pins, every locator resolves to its quote.\n")
    return 0, "".join(out)


if __name__ == "__main__":
    sys.exit(main())
