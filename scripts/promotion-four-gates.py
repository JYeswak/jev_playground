#!/usr/bin/env python3
"""Four-gate VIEW over existing receipts. Does not write STATUS.tsv.

Franken promotion is AND of equivalence / capability / performance / adversarial,
and empty evidence fails the gate (promotion_gate_runner.rs). This is a *view*:
it reads receipts already on disk and prints four bits. It does not add columns,
does not change lane-status.sh, and does not promote anyone.

ACCEPTANCE:
  python3 scripts/promotion-four-gates.py UP-R5-jev-toolcall-gate
  # exits 0 only if all four bits are pass; otherwise prints which gate is empty/fail
  # planted: a candidate with no adversarial receipt must FAIL (empty ≠ pass)
  # STATUS.tsv is not written

NO-CLAIM: bits are a view, not a new score. promoted=0 untouched.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "demos" / "STATUS.tsv"

GATES = ("equivalence", "capability", "performance", "adversarial")

# Extra receipts already on disk that the STATUS row does not name, but that
# the math receipt cites as the oracles for each gate. Paths only — no new
# measurements. A missing file is empty evidence, not a pass.
CANDIDATE_RECEIPTS = {
    "UP-R5-jev-toolcall-gate": (
        "docs/demos/upstream-repro/bicameral-gate-adoption-20260919.md",
        "docs/demos/upstream-repro/harm-rule-claim-repro-20260919.md",
        "docs/demos/upstream-repro/dcg-block-rate-prior-20260919.md",
        "docs/demos/upstream-repro/math-and-next-level-20260919.md",
        "docs/demos/upstream-repro/harm-rule-shipped-20260919.md",
    ),
    "UP-R4-jev-judged-compaction": (
        "docs/demos/upstream-repro/compaction-retention-oracle-20260919.md",
        "docs/demos/upstream-repro/compaction-threshold-curve-20260919.md",
        "docs/demos/upstream-repro/compaction-positive-control-20260919.md",
        "docs/demos/upstream-repro/math-and-next-level-20260919.md",
    ),
}

# Phrases that count as *presence* of evidence for a gate. Absence → empty → fail.
PRESENCE = {
    "equivalence": (
        r"12/12",
        r"11/12",
        r"keep-everything",
        r"same decision",
        r"regex",
    ),
    "capability": (
        r"observe-only",
        r"block:true",
        r"\{block:true\}",
        r"allow\|confirm\|block",
        r"return undefined",
        r"never blocks",
    ),
    "performance": (
        r"0\.97%",
        r"15%",
        r"p99",
        r"keep-everything is free",
        r"latency",
        r"fire rate",
    ),
    "adversarial": (
        r"0/200",
        r"planted negative",
        r"planted-bad",
        r"random-judge",
        r"known-bad still refuse",
        r"adversarial survival",
        r"adversarial robustness",
    ),
}

# Pass predicates, applied only when presence is non-empty.
# Equivalence: deterministic baseline and Jev must agree on the quoted identities.
# Capability: observe-only surfaces must not request {block:true}.
# Performance: Jev fire/cost must not exceed the cheap baseline when both are quoted.
# Adversarial: a quote that the surface is *not* adversarially tested is a fail,
#              as is a held-out FP rate that the receipt itself calls a reject.


def read_status_row(candidate: str) -> dict | None:
    if not STATUS.is_file():
        return None
    for raw in STATUS.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#"):
            continue
        cols = raw.split("\t")
        if cols[0] == "candidate":
            continue
        if cols[0] == candidate:
            receipt = cols[5] if len(cols) > 5 else ""
            return {"candidate": cols[0], "receipt": receipt, "ncols": len(cols)}
    return None


def load_text(rel: str) -> str | None:
    path = ROOT / rel
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def collect_texts(candidate: str) -> tuple[list[str], list[str], str]:
    """Return (relpaths, texts, empty_reason)."""
    rels: list[str] = []
    row = read_status_row(candidate)
    if row and row["receipt"]:
        rels.append(row["receipt"])
    rels.extend(CANDIDATE_RECEIPTS.get(candidate, ()))
    # de-dupe, keep order
    seen: set[str] = set()
    ordered: list[str] = []
    for r in rels:
        if r not in seen:
            seen.add(r)
            ordered.append(r)
    texts: list[str] = []
    missing: list[str] = []
    for r in ordered:
        t = load_text(r)
        if t is None:
            missing.append(r)
        else:
            texts.append(t)
    if not texts:
        return ordered, [], "no readable receipts"
    return ordered, texts, (f"missing {missing}" if missing else "")


def presence(gate: str, blob: str) -> list[str]:
    hits = []
    for pat in PRESENCE[gate]:
        if re.search(pat, blob, flags=re.IGNORECASE):
            hits.append(pat)
    return hits


def decide(gate: str, blob: str, hits: list[str]) -> tuple[str, str]:
    """Return (status, reason) where status is pass|fail|empty."""
    if not hits:
        return "empty", "no receipt quote for this gate (empty ≠ pass)"
    if gate == "equivalence":
        has_regex_12 = bool(re.search(r"12/12", blob))
        has_jev_11 = bool(re.search(r"11/12", blob))
        keep_wins = bool(re.search(r"keep-everything wins", blob, re.I))
        if has_regex_12 and has_jev_11:
            return "fail", "regex 12/12 vs Jev 11/12 — not the same decision"
        if keep_wins:
            return "fail", "keep-everything beats Jev on the same cases"
        return "fail", "evidence names a comparison but does not show identity"
    if gate == "capability":
        observe = bool(re.search(r"observe-only|never blocks", blob, re.I))
        blocking = bool(re.search(r"allow\|confirm\|block|\{block:true\}", blob, re.I))
        hook = ROOT / "work" / "omp-harm-rule" / "harm-rule.ts"
        hook_blocks = False
        if hook.is_file():
            hook_blocks = bool(re.search(r"block\s*:\s*true", hook.read_text(encoding="utf-8")))
        if observe and hook_blocks:
            return "fail", "observe-only design but hook source can return {block:true}"
        if observe and blocking:
            return "fail", "requested block sits outside the shipped observe-only envelope"
        if observe and not hook_blocks:
            return "pass", "observe-only; harm-rule.ts has no block:true"
        return "fail", "capability evidence present but envelope/action set disagree"
    if gate == "performance":
        dcg = bool(re.search(r"0\.97%", blob))
        jev15 = bool(re.search(r"15%", blob))
        if dcg and jev15:
            return "fail", "Jev fire 15% vs dcg 0.97% — worse than the cheap baseline"
        if re.search(r"keep-everything is free", blob, re.I):
            return "fail", "Jev is paid; keep-everything is free"
        return "fail", "performance evidence present; Jev does not dominate the cheap baseline"
    if gate == "adversarial":
        if re.search(r"not (calibration and not )?adversarial robustness", blob, re.I):
            return "fail", "receipt states adversarial robustness was not measured"
        if re.search(r"0/200", blob):
            return "pass", "compaction planted noise 0/200 is on disk"
        if re.search(r"3/20", blob) and re.search(r"false positive", blob, re.I):
            return "fail", "held-out 3/20 FP — known-looking-benign still fire"
        return "fail", "adversarial quote present; survival not shown"
    return "empty", "unknown gate"


def evaluate(candidate: str) -> dict:
    rels, texts, note = collect_texts(candidate)
    blob = "\n".join(texts)
    bits = {}
    for gate in GATES:
        hits = presence(gate, blob)
        status, reason = decide(gate, blob, hits)
        bits[gate] = {
            "status": status,
            "reason": reason,
            "hits": hits,
        }
    return {
        "candidate": candidate,
        "receipts": rels,
        "note": note,
        "bits": bits,
        "all_pass": all(bits[g]["status"] == "pass" for g in GATES),
    }


def render(result: dict) -> str:
    lines = [
        f"four-gate VIEW  candidate={result['candidate']}",
        f"receipts: {', '.join(result['receipts']) or '(none)'}",
    ]
    if result["note"]:
        lines.append(f"note: {result['note']}")
    for gate in GATES:
        b = result["bits"][gate]
        lines.append(f"  {gate:<13} {b['status']:<5}  {b['reason']}")
    lines.append("STATUS.tsv not written")
    lines.append("NO-CLAIM: view over existing receipts; not a promotion; promoted=0.")
    if result["all_pass"]:
        lines.append("VERDICT: all four pass")
    else:
        failed = [g for g in GATES if result["bits"][g]["status"] != "pass"]
        lines.append(f"VERDICT: FAIL gates={','.join(failed)} (empty ≠ pass)")
    return "\n".join(lines)


def status_digest() -> str:
    return hashlib.sha256(STATUS.read_bytes()).hexdigest() if STATUS.is_file() else "ABSENT"


def selftest() -> int:
    before = status_digest()
    errors: list[str] = []

    # Planted: a name with no receipts → every gate empty → must FAIL, not pass.
    planted = evaluate("PLANTED-NO-ADVERSARIAL-RECEIPT")
    if planted["all_pass"]:
        errors.append("empty-evidence candidate passed")
    if planted["bits"]["adversarial"]["status"] != "empty":
        errors.append(f"planted adversarial status={planted['bits']['adversarial']['status']} want empty")
    print(render(planted))
    print()

    # Real candidate: must not silently pass, and must not write STATUS.
    real = evaluate("UP-R5-jev-toolcall-gate")
    print(render(real))
    if real["all_pass"]:
        errors.append("UP-R5 unexpectedly all-pass — check extractors, do not weaken")
    if real["bits"]["adversarial"]["status"] == "pass":
        errors.append("UP-R5 adversarial cannot pass: receipt says robustness was not measured")

    after = status_digest()
    if after != before:
        errors.append("STATUS.tsv digest changed — the view must not write the ledger")

    print()
    if errors:
        print("four-gate --selftest FAIL: " + "; ".join(errors), file=sys.stderr)
        return 2
    print("four-gate --selftest: PASS (empty ≠ pass; STATUS unread-write)")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    if not argv or argv[0].startswith("-"):
        print("usage: python3 scripts/promotion-four-gates.py <candidate>|--selftest", file=sys.stderr)
        return 2
    result = evaluate(argv[0])
    print(render(result))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
