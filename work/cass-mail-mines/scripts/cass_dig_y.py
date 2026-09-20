#!/usr/bin/env python3
"""Mechanical Y for cass dig-vs-invent (documented proxy, not human label).

y_dig = 1 iff at least one hit is "receipt-shaped":
  - has source_path and (line_number or line)
  - source_path does NOT look like doctrine-about-cass alone
    (AGENTS.md / dont-give-up*.md / SKILL.md basename traps)
  - OR query class is wrong-selector AND snippet matches absence language
    while also containing requireKey/keys( evidence of the G6 pattern

y_dig = 0 for empty hits, doctrine-only lexical traps, and negative control.

This Y is independent of raw count>0 so dig-iff-count>0 can LOSE (A12 RED).
"""
from __future__ import annotations

import re

DOCTRINE_BASENAME = re.compile(
    r"(^|/)(AGENTS\.md|SKILL\.md|dont-give-up[^/]*\.md)$", re.I
)
ABSENCE = re.compile(
    r"no such (field|key)|keys present|requireKey|\.distribution", re.I
)
REQUIRE_EVIDENCE = re.compile(r"requireKey|keys\(\)|Object\.keys", re.I)


def hit_receipt_shaped(h: dict) -> bool:
    sp = str(h.get("source_path") or h.get("path") or "")
    if not sp:
        return False
    if DOCTRINE_BASENAME.search(sp.replace("\\", "/")):
        return False
    ln = h.get("line_number", h.get("line"))
    if ln is None or ln == "":
        return False
    return True


def y_for_row(query: str, hits: list, hit_count: int | None = None) -> int:
    q = query or ""
    if "zzzz_cannot_exist_9c42" in q:
        return 0
    hits = hits or []
    if hit_count is None:
        hit_count = len(hits)
    if hit_count <= 0:
        return 0
    if ABSENCE.search(q):
        for h in hits:
            if not isinstance(h, dict):
                continue
            sn = str(h.get("snippet") or h.get("text") or h.get("content") or "")
            if ABSENCE.search(sn) and REQUIRE_EVIDENCE.search(sn):
                return 1
            if hit_receipt_shaped(h) and ABSENCE.search(sn):
                return 1
        return 0
    if any(isinstance(h, dict) and hit_receipt_shaped(h) for h in hits):
        return 1
    return 0
