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
# THE REGEX IS RETIRED AS A GATE INPUT. Measured against pane 3's opened-receipt typing
# (receipt-type-proposal-20260918T102335Z.tsv) on all 17 rows:
#
#   regex-matched but NOT a score receipt (false GREEN) ... 5
#   score receipt the regex MISSED        (false RED)  ... 0
#   correct                                            ... 1
#
# It was right once in six. R17 claimed "permissive, never falsely accuses"; pane 2 falsified that as
# a general statement by construction; measured on the real file the exposure is asymmetric — 5
# permissive errors, 0 strict ones. BOTH MY CLAIM AND ITS CORRECTION WERE HALF-RIGHT, and only the
# DECLARED type settles it. Kept below only to describe history, never to judge it.
LEGACY_REGEX_FOR_HISTORY_ONLY = re.compile(r"(SCORES?_|DEMAND_|HUNT_|RUNG2_|_score|-score)", re.I)
SCORE_TYPE = "score"


def rows(text):
    """candidate -> (score, verdict, receipt, receipt_type|None). Empty fields preserved.

    receipt_type is None for PRE-MIGRATION rows (9 columns). Per pane 2's Q19 ruling it is NEVER
    inferred — not from the filename, not from the regex above. An untyped row is untyped, and the
    caller must report it as such rather than judging it.
    """
    out = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) < 6 or f[0] == "candidate":
            continue
        out[f[0]] = (f[2], f[3], f[5], f[9] if len(f) >= 10 else None)
    return out


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def compare(before, after, msg, sha="(pair)"):
    """Return (score_events, verdict_changed, trips, untyped).

    `untyped` is True when a coincidence exists but the changed rows carry no declared type, i.e. a
    PRE-MIGRATION commit. Such a commit is reported as UNTYPED, never as clean — the retry condition
    R17 named has been met going forward, and it cannot be applied backwards.
    """
    b, a = rows(before), rows(after)
    score_events, verdict_changed = [], []
    for cand, (score, verdict, receipt, rtype) in a.items():
        if cand not in b:
            continue
        old_score, old_verdict, _, _ = b[cand]
        if score != old_score:
            direction = "?"
            try:
                direction = "UP" if int(score) > int(old_score) else "down"
            except ValueError:
                pass
            score_events.append((cand, old_score, score, direction, receipt, rtype))
        if verdict != old_verdict:
            verdict_changed.append((cand, old_verdict, verdict))
    trips, untyped = [], False
    if score_events and verdict_changed:
        # THE GATE NOW READS THE DECLARED TYPE, which is the R17 retry condition met. Two things the
        # earlier versions got wrong are both closed here:
        #   1. the commit-message branch (a gate the gated party could satisfy by typing "RUNG2_" into
        #      its own message) is gone — a gate reads STATE, never prose written by the constrained
        #      party;
        #   2. the filename regex is gone — it was right 1 time in 6 against opened-receipt typing.
        #
        # AND THE HONEST CONSEQUENCE, which retires a number I reported repeatedly: the declared type
        # exists only from the migration commit forward. Pre-migration coincidences are UNTYPED, and
        # per Q19 an untyped row is NEVER inferred — so the historical "0 trips" is downgraded to
        # "0 trips among TYPED coincidences", with the pre-migration ones reported as untyped rather
        # than clean. The old result rested on the regex, and the regex was wrong 5 times in 6.
        if all(rt is None for *_, rt in score_events):
            untyped = True
        elif not any(rt == SCORE_TYPE for *_, rt in score_events):
            trips.append((sha, score_events, verdict_changed))
    return score_events, verdict_changed, trips, untyped


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "--pair":
        if len(argv) != 3:
            print("usage: --pair BEFORE.tsv AFTER.tsv", file=sys.stderr)
            return 2
        before, after = Path(argv[1]).read_text(), Path(argv[2]).read_text()
        msg = ""
        se, vc, tr, unt = compare(before, after, msg)
        print(f"score_changes: {len(se)}  verdict_changes: {len(vc)}  trips: {len(tr)}"
              f"  untyped: {1 if unt else 0}")
        for cand, o, n, d, _, rt in se:
            print(f"  score {cand}: {o} -> {n} ({d})  declared_type={rt or 'UNTYPED'}")
        for sha, se2, vc2 in tr:
            print(f"  TRIP {sha}: score moved with a verdict change and NO changed row is type 'score'")
        if unt:
            print("  UNTYPED: coincidence on pre-migration rows; never inferred, never called clean")
            return 6
        return 5 if tr else 0

    shas = git("log", "--format=%H", "--reverse", "--", STATUS).split()
    if not shas:
        print(f"audit-score-lineage: no history for {STATUS}", file=sys.stderr)
        return 2
    verbose = "--verbose" in argv
    total_score, total_coin, all_trips, ups = 0, 0, [], 0
    coin_rows, held_exit_rows, untyped_coin = 0, 0, 0
    prev = ""
    for sha in shas:
        cur = git("show", f"{sha}:{STATUS}")
        msg = git("log", "-1", "--format=%B", sha)
        se, vc, tr, unt = compare(prev, cur, msg, sha[:7])
        total_score += len(se)
        if se and vc:
            total_coin += 1
            coin_rows += len(se)
            if unt:
                untyped_coin += 1
            # Pane 3's ORIGINAL (too-narrow) definition, kept so the two denominators stay
            # comparable: it counted only HELD->non-HELD exits, which missed demo-9's
            # RECUSED->CLEARED. Reporting both is how "3" and "6" stop looking like a disagreement.
            if any(o == "HELD" for _, o, _ in vc):
                held_exit_rows += len(se)
            if verbose:
                print(f"  COINCIDENCE {sha[:7]}  score_rows={len(se)} verdict_rows={len(vc)}"
                      f"  {'UNTYPED (pre-migration)' if unt else 'typed'}")
                for c, o, n, d, r, rt in se:
                    print(f"      score   {c}: {o} -> {n} ({d})  declared_type={rt or 'UNTYPED'}")
                    print(f"              receipt {r}  legacy-regex-would-have-said="
                          f"{'score' if LEGACY_REGEX_FOR_HISTORY_ONLY.search(r) else 'not-score'}")
                for c, o, n in vc:
                    flag = "" if o == "HELD" else "   <- escapes HELD-exit definition"
                    print(f"      verdict {c}: {o} -> {n}{flag}")
        ups += sum(1 for *_, d, _, _ in se if d == "UP")
        all_trips += tr
        prev = cur

    print(f"SCORE LINEAGE (amended form: ANY verdict-change, not HELD-exits only)")
    print(f"  commits touching {STATUS}: {len(shas)}")
    print(f"  score changes: {total_score}   upward: {ups}")
    print(f"  coincidences: {total_coin} COMMITS / {coin_rows} ROWS"
          f"   (pane 3's HELD-exit-only definition would see {held_exit_rows} rows)")
    print(f"  coincidences UNTYPED (pre-migration rows): {untyped_coin}"
          f"   <- never inferred, never counted clean")
    print(f"  trips among TYPED coincidences: {len(all_trips)}")
    for sha, se, vc in all_trips:
        print(f"  TRIP {sha}:")
        for cand, o, n, d, _, rt in se:
            print(f"      score {cand}: {o} -> {n} ({d})  declared_type={rt or 'UNTYPED'}")
        for cand, o, n in vc:
            print(f"      verdict {cand}: {o} -> {n}")
    if all_trips:
        print("FAIL: a score moved with a verdict change and no changed row is declared type 'score'.")
        return 5
    if untyped_coin:
        # This is the honest downgrade of a number I reported repeatedly. The old "0 trips" was
        # derived from the filename regex, which opened-receipt typing later showed to be right 1
        # time in 6. The declared type exists only from the migration commit forward, so the
        # historical coincidences are UNTYPED — not clean, not tripped, UNJUDGED.
        print(f"UNTYPED: {untyped_coin} coincidence(s) predate the receipt_type migration.")
        print("The earlier '0 trips' rested on a filename regex that was right 1 time in 6.")
        print("Typed coincidences: 0 trips. Untyped ones are not claimed either way.")
        return 6
    print("OK: no typed coincidence lacked a declared score receipt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
