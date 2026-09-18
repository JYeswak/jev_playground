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
def snapshot(paths, root: Path):
    """Copy each path into root/files/<original relative path>. Returns {original: snapshot}."""
    mapped = {}
    for p in paths:
        src = Path(p)
        if not src.is_file():
            continue
        dst = root / "files" / src
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        mapped[str(src)] = dst
    return mapped


def manifest_for(mapped, pre, post, attempts, head):
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
        })
    payload = {
        "schema": "jev.snapshot-manifest.v1",
        "spec": "docs/demos/duel-2/SPEC_snapshot_manifest_COD.md (44feaf2)",
        "source_head": head,
        "capture_attempts": attempts,
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
        inputs = [str(STATUS), str(SIDECAR)]
        for line in STATUS.read_text().splitlines():
            f = line.split("\t")
            if line and not line.startswith("#") and f[0] != "candidate" and len(f) >= 10:
                inputs.append(f[5])
        pre = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]
               for p in inputs if Path(p).is_file()}
        root = Path(tempfile.mkdtemp(prefix="jev-snap-"))
        mapped = snapshot(inputs, root)
        # NEVER FALL BACK TO A LIVE PATH. Found by reading pane 2's OWN re-open condition — "no live
        # shared path is read after the snapshot is declared complete" — against my implementation:
        # `mapped.get(str(p), Path(p))` returned the LIVE path for anything not copied, and
        # `snapshot()` skips paths absent at capture. So a receipt that did not exist at capture but
        # APPEARED MID-RUN would have been read live and verified — bytes that were never
        # snapshotted, passing a check the manifest cannot account for. Unmapped paths now resolve
        # INTO the snapshot root, where they are absent, so "absent at capture" stays absent.
        def resolve(p, _m=mapped, _r=root):
            return _m.get(str(p)) or (_r / "files" / p)
        rc, report = _verify(resolve(STATUS), resolve(SIDECAR), resolve)
        post = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]
                for p in inputs if Path(p).is_file()}
        man = manifest_for(mapped, pre, post, attempt, head)
        (root / "manifest.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n")
        moved = sorted(p for p in pre if pre[p] != post.get(p))
        # DETERMINISTIC KNOWN-BAD HOOK, same pattern and same reason as lane-status's
        # JEV_SELF_DIGEST_OVERRIDE: racing a mid-run mutation against a ~0.3s verify produced an arm
        # that proved nothing THREE times in this session, and tuning the sleep until it passed would
        # be a witness that passes by construction. FAIL-SAFE BY CONSTRUCTION — it can only
        # manufacture a FALSE TRANSIENT (no verdict), never a false pass.
        if os.environ.get("JEV_FORCE_MOVED"):
            moved = sorted(set(moved) | {os.environ["JEV_FORCE_MOVED"]})
        if not moved:
            print(report, end="")
            print(f"  snapshot: {root}  manifest_digest: {man['manifest_digest']}")
            print(f"  source HEAD {head[:7]}, capture attempt {attempt} of max 2, inputs {len(pre)}")
            return rc
        if attempt == 2:
            print("TRANSIENT_UNSTABLE: source inputs moved during BOTH captures. NO VERDICT.")
            for p in moved:
                print(f"  moved: {p}  {pre[p]} -> {post.get(p)}")
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
