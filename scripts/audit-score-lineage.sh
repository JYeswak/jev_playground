#!/usr/bin/env python3
"""audit-score-lineage.sh — the STANDING watcher for the hold-vs-score condition.

WHY THIS EXISTS
  Pane 2 demoted "resolving a hold is not raising a score" to guidance with a return condition:
  re-promote only when a receipt or dispatch conflates a resolved prerequisite with a changed score.
  Pane 3 audited that condition and graded it CONDITION_PROSE_SHAPED, the weakest of three, because
  "nobody is tasked to scan receipts/dispatches for score-on-resolution events" — and named the
  consequence exactly: "if the condition cannot fire observably, DEMOTE-WITH-UNWATCHED-RETURN IS
  DELETE WITH EXTRA STEPS."

  Pane 3 then proved the watcher can exist: git IS the watcher, because every verdict-table score
  lives in a tracked file. It ran that check by hand over 32 commits (7 score changes, 0 trips, ALL
  DOWNWARD) and AMENDED ITS OWN MECHANICAL FORM after finding its first definition too narrow:

      "coincidence as run = same-commit HELD-exit. One real coincidence escapes that definition:
       demo-9 700->550 coincided with RECUSED->CLEARED ... the mechanical form must watch ANY
       verdict-change, not HELD-exits only."

  This implements the AMENDED form. Q63 proved the past; this checks every future edit.

WHY PYTHON AND NOT BASH
  This session produced two field-splitting bugs in the sibling bash instrument within minutes:
  tab is IFS-whitespace so `IFS=$'\t' read` collapses empty columns (integrity_checked reported 4
  instead of 17), and BSD tr has no \\x escape so the first fix silently corrupted every field.
  A 9-column TSV with optional empty middle columns is the exact shape bash splits wrong.

TRIP CONDITION (all three must hold)
  1. a score delta on some row, AND
  2. any verdict change on any row in the same commit, AND
  3. no SCORE receipt cited distinct from the hold-resolution receipt.
  An UPWARD delta under those conditions is the known-bad this exists to catch.

EXIT  0 clean · 5 trips found · 2 usage/environment error
"""
import re
import subprocess
import sys
from pathlib import Path

STATUS = "docs/demos/STATUS.tsv"
# A "score receipt" is an artifact whose job is scoring, distinct from a hold-resolution receipt.
SCORE_RECEIPT = re.compile(r"(SCORES?_|DEMAND_|HUNT_|RUNG2_|_score|-score)", re.I)


def rows(text):
    """candidate -> (score, verdict, receipt). Split on literal tab; empty fields preserved."""
    out = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) < 6 or f[0] == "candidate":
            continue
        out[f[0]] = (f[2], f[3], f[5])
    return out


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def compare(before, after, msg, sha="(pair)"):
    """Return (score_events, verdict_changed, trips)."""
    b, a = rows(before), rows(after)
    score_events, verdict_changed = [], []
    for cand, (score, verdict, receipt) in a.items():
        if cand not in b:
            continue
        old_score, old_verdict, _ = b[cand]
        if score != old_score:
            direction = "?"
            try:
                direction = "UP" if int(score) > int(old_score) else "down"
            except ValueError:
                pass
            score_events.append((cand, old_score, score, direction, receipt))
        if verdict != old_verdict:
            verdict_changed.append((cand, old_verdict, verdict))
    trips = []
    if score_events and verdict_changed:
        # THE COMMIT-MESSAGE BRANCH WAS REMOVED, and this is the reason it is worth a paragraph.
        # The first version read `SCORE_RECEIPT.search(msg) or <row receipts>`. A gate that can be
        # satisfied by typing "RUNG2_" into your own commit message is not a gate — and the party
        # writing those messages is the conductor, i.e. the party this gate exists to constrain.
        # I built myself an escape hatch. Measured on real history: 7622790 passed via BOTH branches,
        # 1bb9a4b and 1ccddf9 passed on row receipts ALONE, so removing the message branch changes no
        # historical verdict — it only closes the hole. A gate reads STATE, never prose written by
        # the gated party.
        #
        # KNOWN LIMITATION, not fixed here: SCORE_RECEIPT is still a PATTERN RULE over filenames, and
        # it matches 17 of the 48 top-level duel-2 documents. That is the same label-defining-regex
        # defect this lane ruled COD-H2's rung 4 UNASKABLE over, now inside one of its own gates. The
        # direction is permissive — it under-fires (missed trips), it never falsely accuses — and all
        # three historical passes cite receipts that are genuinely scoring artifacts
        # (HUNT_SCORES_COD_ON_MU.md, HUNT_SCORES_MU_ON_COD.md, RUNG2_demo9_MU.md), so the clean
        # result stands on the merits. RETRY CONDITION: replace the regex with a DECLARED receipt
        # type in STATUS.tsv, so "is this a score receipt" is stated by the row rather than inferred
        # from its filename. Until then this gate's `0 trips` carries a weaker claim than it looks.
        if not any(SCORE_RECEIPT.search(r) for *_, r in score_events):
            trips.append((sha, score_events, verdict_changed))
    return score_events, verdict_changed, trips


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "--pair":
        if len(argv) != 3:
            print("usage: --pair BEFORE.tsv AFTER.tsv", file=sys.stderr)
            return 2
        before, after = Path(argv[1]).read_text(), Path(argv[2]).read_text()
        msg = ""
        se, vc, tr = compare(before, after, msg)
        print(f"score_changes: {len(se)}  verdict_changes: {len(vc)}  trips: {len(tr)}")
        for cand, o, n, d, _ in se:
            print(f"  score {cand}: {o} -> {n} ({d})")
        for sha, se2, vc2 in tr:
            print(f"  TRIP {sha}: {se2} coincides with {vc2}, no score receipt cited")
        return 5 if tr else 0

    shas = git("log", "--format=%H", "--reverse", "--", STATUS).split()
    if not shas:
        print(f"audit-score-lineage: no history for {STATUS}", file=sys.stderr)
        return 2
    verbose = "--verbose" in argv
    total_score, total_coin, all_trips, ups = 0, 0, [], 0
    coin_rows, held_exit_rows = 0, 0
    prev = ""
    for sha in shas:
        cur = git("show", f"{sha}:{STATUS}")
        msg = git("log", "-1", "--format=%B", sha)
        se, vc, tr = compare(prev, cur, msg, sha[:7])
        total_score += len(se)
        if se and vc:
            total_coin += 1
            coin_rows += len(se)
            # Pane 3's ORIGINAL (too-narrow) definition, kept so the two denominators stay
            # comparable: it counted only HELD->non-HELD exits, which missed demo-9's
            # RECUSED->CLEARED. Reporting both is how "3" and "6" stop looking like a disagreement.
            if any(o == "HELD" for _, o, _ in vc):
                held_exit_rows += len(se)
            if verbose:
                print(f"  COINCIDENCE {sha[:7]}  score_rows={len(se)} verdict_rows={len(vc)}")
                for c, o, n, d, _ in se:
                    print(f"      score   {c}: {o} -> {n} ({d})")
                for c, o, n in vc:
                    flag = "" if o == "HELD" else "   <- escapes HELD-exit definition"
                    print(f"      verdict {c}: {o} -> {n}{flag}")
        ups += sum(1 for *_, d, _ in se if d == "UP")
        all_trips += tr
        prev = cur

    print(f"SCORE LINEAGE (amended form: ANY verdict-change, not HELD-exits only)")
    print(f"  commits touching {STATUS}: {len(shas)}")
    print(f"  score changes: {total_score}   upward: {ups}")
    print(f"  coincidences: {total_coin} COMMITS / {coin_rows} ROWS"
          f"   (pane 3's HELD-exit-only definition would see {held_exit_rows} rows)")
    print(f"  trips (coincidence with no distinct score receipt): {len(all_trips)}")
    for sha, se, vc in all_trips:
        print(f"  TRIP {sha}:")
        for cand, o, n, d, _ in se:
            print(f"      score {cand}: {o} -> {n} ({d})")
        for cand, o, n in vc:
            print(f"      verdict {cand}: {o} -> {n}")
    if all_trips:
        print("FAIL: a score moved alongside a verdict change with no separate score receipt.")
        return 5
    print("OK: no score change coincided with a verdict change without its own score receipt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
