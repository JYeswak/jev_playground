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
import sys
from pathlib import Path

STATUS = Path("docs/demos/STATUS.tsv")
SIDECAR = Path("docs/demos/duel-2/runs/receipt-other-reasons.json")
ALLOWED = {"design", "mapping", "unresolved", "mixed"}


def norm_digest(path: Path) -> str:
    data = path.read_bytes()
    stripped = re.sub(rb"\s+\Z", b"", data)
    return hashlib.sha256(stripped).hexdigest()[:16]


def main() -> int:
    if not STATUS.exists() or not SIDECAR.exists():
        print(f"verify-other-reasons: missing {STATUS if not STATUS.exists() else SIDECAR}",
              file=sys.stderr)
        return 2

    other_rows = {}
    for line in STATUS.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) < 10 or f[0] == "candidate":
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
        p = Path(row.get("receipt", ""))
        if not p.is_file():
            fails.append(f"ABSENT: {cand} receipt {p} does not exist")
        else:
            live = norm_digest(p)
            if status_digest and live != status_digest:
                fails.append(f"DIGEST: {cand} live {live} != STATUS pin {status_digest}")
        # A locator a third party cannot resolve is a citation only its author can check — the
        # defect this lane has recorded eight times under "open the cited control".
        loc, quote = row.get("evidence_locator", ""), row.get("evidence_quote", "")
        if not loc or not quote:
            fails.append(f"LOCATOR: {cand} lacks an evidence locator or quote")
        elif p.is_file() and p.suffix == ".md":
            m = re.search(r":(\d+)$", loc)
            if not m:
                fails.append(f"LOCATOR: {cand} markdown locator '{loc}' has no line number")
            else:
                lines = p.read_text().splitlines()
                n = int(m.group(1))
                if not (1 <= n <= len(lines)):
                    fails.append(f"LOCATOR: {cand} line {n} out of range (file has {len(lines)})")
                elif quote.strip() not in lines[n - 1]:
                    fails.append(f"QUOTE: {cand} line {n} does not contain the cited quote")
        elif p.is_file() and p.suffix == ".json":
            field = loc.split("$.")[-1] if "$." in loc else None
            blob = json.loads(p.read_text())
            if field is None or field not in blob:
                fails.append(f"LOCATOR: {cand} json locator '{loc}' names no present field")
            elif quote.strip() not in str(blob[field]):
                fails.append(f"QUOTE: {cand} field {field} does not contain the cited quote")

    for key in ("assigner", "generated_at", "gate_behavior", "digest_convention"):
        if not side.get(key):
            fails.append(f"PROVENANCE: sidecar lacks '{key}'")

    print(f"OTHER_REASON SIDECAR  (documentation only — no gate reads this file)")
    print(f"  STATUS rows typed `other`: {len(other_rows)}   sidecar entries: {len(rows)}")
    print(f"  allowed reasons: {'|'.join(sorted(ALLOWED))}")
    used = sorted({r.get('other_reason') for r in rows.values()})
    print(f"  reasons used: {'|'.join(x for x in used if x)}   unused: "
          f"{'|'.join(sorted(ALLOWED - set(used)))}")
    if fails:
        for f in fails:
            print(f"  FAIL {f}")
        print(f"FAIL: {len(fails)} verification failure(s).")
        return 1
    print("OK: exact coverage, bindings match STATUS pins, every locator resolves to its quote.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
