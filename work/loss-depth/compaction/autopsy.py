#!/usr/bin/env python3
"""Keyless loss-depth autopsy of the two compaction keep studies (bead jev-9gtw.5).

  python3 work/loss-depth/compaction/autopsy.py            # every count in the receipt, from committed files
  python3 work/loss-depth/compaction/autopsy.py --refresh  # first re-derive features.jsonl from the
                                                           # sha-pinned omp session files, and refuse on drift

No Jev or model call. Inputs, all committed:
- work/compaction-need (jev-x86y) and work/compaction-keep (jev-jec6): labels, calls, decisions;
- features.jsonl / sessions.json here, written by autopsy.ts: numbers, flags and ids per prefix call,
  measured on the exact request fast-jev-compaction 6e1da50 built (fitState state, batchCalls batch);
- codes.jsonl here: one row per needed unpinned call Jev did not keep verbatim, with four judged
  fields (used, reobtain, trigger, visible) and one decisive fact, written by reading the prefix and
  horizon. No session text beyond short quotes.

The cause is computed from those fields by a fixed precedence (first match wins):

1. harness_shaken  - the transcript already held omp's shake stub, not the output (mechanical);
2. unforeseeable   - the use answers a horizon prompt the prefix did not anticipate (trigger);
3. call_not_result - the later use is the call's own input, not its output (used);
4. rerun_premise   - the output is re-obtainable by re-running or re-reading, which the library's
                     state tells Jev is always possible and its question rules out (reobtain);
5. model_miss      - irreplaceable output whose need the state shows (visible goal/text);
6. evidence_absent - irreplaceable output, need not shown: the state omits every output.
"""

from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "work" / "compaction-need"))
sys.path.insert(0, str(ROOT / "work" / "compaction-keep"))
import keep as K  # noqa: E402  calls(), final() of jev-jec6
import need as N  # noqa: E402  calls(), final() of jev-x86y (A1-excluded session dropped), read_jsonl, R1.wilson

STUDIES = {"x86y": ROOT / "work/compaction-need", "jec6": ROOT / "work/compaction-keep"}
CAUSES = [
    "harness_shaken",
    "unforeseeable",
    "call_not_result",
    "rerun_premise",
    "model_miss",
    "evidence_absent",
]
HEAD = 500  # the replay's truncateHeadChars: what a drop_result keeps
BAR_RECALL_LOWER, BAR_NN_DROPPED = 0.80, 0.50  # jev-jec6's preregistered bar


def scored(study: str) -> tuple[list[dict], list[dict]]:
    """Decisions of the unpinned needed and not-needed calls, from the study's own committed files.

    This covers every session the study scored, including jev-x86y's 01a0c530, whose text this
    autopsy does not read (rider screen): its labels and scores are committed ids and numbers.
    """
    mod = N if study == "x86y" else K
    keys = mod.calls()
    got = mod.final(keys)
    if isinstance(got, str):
        sys.exit(f"REFUSED: {study} labels: {got}")
    fin = got[2]
    dec = {
        (d["session"], d["tool_use_id"]): d
        for d in N.read_jsonl(STUDIES[study] / "decisions.jsonl")
    }
    free = [k for k in keys if not keys[k]["pinned"]]
    return [dec[k] for k in free if fin[k] == "needed"], [
        dec[k] for k in free if fin[k] == "not-needed"
    ]


def cause(code: dict, feat: dict) -> str:
    if feat["result_shaken"]:
        return "harness_shaken"
    if code["trigger"] == "new-prompt":
        return "unforeseeable"
    if code["used"] == "input":
        return "call_not_result"
    if code["reobtain"] in ("rerun", "reread"):
        return "rerun_premise"
    if code["visible"] in ("goal", "text"):
        return "model_miss"
    return "evidence_absent"


def auc(pos: list[float], neg: list[float]) -> float:
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


def rate(k: int, n: int) -> str:
    lo, hi = N.R1.wilson(k, n) if n else (0.0, 0.0)
    return f"{k}/{n} (Wilson {max(0.0, lo):.3f}-{min(1.0, hi):.3f})"


def library_action(d: dict) -> str:
    """decideCall() at keepThreshold 0.5, for jev-jec6 rows that recorded scores but no action."""
    if d.get("action"):
        return d["action"]
    if d["keepResult"] >= 0.5:
        return "keep"
    return "drop_result" if d["keepCall"] >= 0.5 else "drop_call"


def refresh() -> None:
    before = (HERE / "features.jsonl").read_bytes()
    out = subprocess.run(
        ["node", "--experimental-strip-types", str(HERE / "autopsy.ts"), "features"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if out.returncode != 0:
        sys.exit(f"REFUSED: autopsy.ts features failed: {out.stderr.strip()[-400:]}")
    if (HERE / "features.jsonl").read_bytes() != before:
        sys.exit(
            "REFUSED: features.jsonl re-derived differently from the committed copy"
        )
    print(
        "refresh: features.jsonl re-derived from the sha-pinned session files, byte-identical"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    if ap.parse_args().refresh:
        refresh()

    feats = N.read_jsonl(HERE / "features.jsonl")
    sessions = json.loads((HERE / "sessions.json").read_text())
    codes = {
        (c["session"], c["tool_use_id"]): c for c in N.read_jsonl(HERE / "codes.jsonl")
    }
    key = lambda r: (r["session"], r["tool_use_id"])  # noqa: E731
    free = [f for f in feats if not f["pinned"]]

    print(
        "# 1. The request each study sent (rebuilt keylessly, fast-jev-compaction 6e1da50)\n"
    )
    print(
        "| study | session | prefix msgs | candidates | state stage | state tokens (est) | batches | goal chars | latest prompt in goal |"
    )
    print("|---|---|---:|---:|---|---:|---:|---:|---|")
    for s in sessions:
        if "skipped" in s:
            print(f"| {s['study']} | {s['session']} | skipped: {s['skipped']} |||||||")
            continue
        print(
            f"| {s['study']} | {s['session']} | {s['prefix_messages']} | {s['candidates']} | {s['state_stage']} | "
            f"{s['state_tokens_est']} | {s['batches']} | {s['goal_chars']} | {'yes' if s['last_user_in_goal'] else 'NO (a tool result is attached to it)'} |"
        )
    jec = [s for s in sessions if s["study"] == "jec6" and "skipped" not in s]
    est = sum(
        s["state_tokens_est"] * 2
        + s["lib_question_tokens_est"]
        + s["need_question_tokens_est"]
        for s in jec
    )
    got = json.loads((STUDIES["jec6"] / "decisions-pass.json").read_text())[
        "input_tokens"
    ]
    print(
        f"\nReconstruction check (jev-jec6, all 4 sessions, 8 requests): estimated {est} input tokens vs {got} "
        f"recorded by the live run, {100 * (est - got) / got:+.1f}% (the library's estimator is calibrated 2-18% high)."
    )
    measurable = [f for f in feats if f["result_in_state"] is not None]
    print(
        f"Output head (first 40 chars) found in the request state: {sum(f['result_in_state'] for f in measurable)} of "
        f"{len(measurable)} prefix calls with an output of 40+ chars; every call reached Jev as `result: \"ok|error, N chars (omitted)\"`."
    )

    print(
        "\n# 2. Reproduction of the published scores (unpinned calls, final labels, all scored sessions)\n"
    )
    for study in STUDIES:
        pos, neg = scored(study)
        for field in ("keepCall", "keepResult", "need"):
            if pos[0].get(field) is None:
                continue
            kept = sum(d[field] >= 0.5 for d in pos)
            print(
                f"{study} {field}: needed {len(pos)}, >= 0.5 on {kept}; not-needed {len(neg)}; "
                f"AUC needed vs not-needed {auc([d[field] for d in pos], [d[field] for d in neg]):.3f}"
            )

    print("\n# 3. Causes of the needed calls Jev did not keep verbatim\n")
    misses = []
    for study in STUDIES:
        dec = {key(d): d for d in N.read_jsonl(STUDIES[study] / "decisions.jsonl")}
        for f in free:
            if (
                f["study"] == study
                and f["label"] == "needed"
                and dec[key(f)]["keepResult"] < 0.5
            ):
                misses.append((f, dec[key(f)]))
    missing = [key(f) for f, _ in misses if key(f) not in codes]
    extra = set(codes) - {key(f) for f, _ in misses}
    if missing or extra:
        print(
            f"REFUSED: codes.jsonl does not cover the misses exactly (missing {len(missing)}, extra {len(extra)})"
        )
        return 1
    bad = [
        key(f)
        for f, _ in misses
        if (codes[key(f)]["reobtain"] == "stub") != f["result_shaken"]
    ]
    if bad:
        print(f"REFUSED: {len(bad)} codes disagree with the shaken flag, e.g. {bad[0]}")
        return 1
    bad = [
        key(f)
        for f, _ in misses
        if codes[key(f)]["reobtain"] == "rerun" and f["written_later_in_prefix"]
    ]
    if bad:
        print(
            f"REFUSED: {len(bad)} codes say a re-run returns the output, but a later prefix call wrote that file, e.g. {bad[0]}"
        )
        return 1
    table = collections.Counter(
        (f["study"], cause(codes[key(f)], f)) for f, _ in misses
    )
    totals = collections.Counter(f["study"] for f, _ in misses)
    print("| cause | x86y | jec6 | both |")
    print("|---|---:|---:|---:|")
    for c in CAUSES:
        print(
            f"| {c} | {table[('x86y', c)]} | {table[('jec6', c)]} | {table[('x86y', c)] + table[('jec6', c)]} |"
        )
    print(f"| total | {totals['x86y']} | {totals['jec6']} | {len(misses)} |")

    print("\nMean scores by cause (keepCall / keepResult):")
    for c in CAUSES:
        xs = [d for f, d in misses if cause(codes[key(f)], f) == c]
        if xs:
            print(
                f"  {c}: n={len(xs)} keepCall {sum(d['keepCall'] for d in xs) / len(xs):.3f} keepResult {sum(d['keepResult'] for d in xs) / len(xs):.3f}"
            )

    print(
        "\n# 4. Contributing factors on the same misses (not exclusive, mechanical unless noted)\n"
    )
    live = [(f, d) for f, d in misses if not f["result_shaken"]]
    with_tok = [f for f, _ in live if f["use_min_offset"] is not None]
    print(
        f"- output head present in the request state: {sum(bool(f['result_in_state']) for f, _ in misses)}/{len(misses)} "
        "(the state holds the input, capped at 1,000 chars, and `ok, N chars (omitted)`)"
    )
    print(
        f"- need visible in the goal (coded): {sum(codes[key(f)]['visible'] == 'goal' for f, _ in live)}/{len(live)} non-stub misses; "
        f"goal names the call's file (mechanical): {sum(f['goal_names_target'] for f, _ in live)}"
    )
    print(
        f"- output re-obtainable by re-run or re-read (coded): {sum(codes[key(f)]['reobtain'] in ('rerun', 'reread') for f, _ in live)}/{len(live)}"
    )
    print(
        f"- file written again later in the prefix, so a re-read differs (mechanical): {sum(f['written_later_in_prefix'] for f, _ in live)}/{len(live)}"
    )
    print(
        f"- use triggered by a new horizon prompt (coded): {sum(codes[key(f)]['trigger'] == 'new-prompt' for f, _ in live)}/{len(live)}; "
        f"a horizon prompt came before the use (mechanical): {sum(f['user_prompt_in_horizon_before_use'] for f, _ in live)}"
    )
    print(
        f"- used tokens located in the output: {len(with_tok)}/{len(live)}; earliest one inside the first {HEAD} chars on "
        f"{sum(f['use_min_offset'] < HEAD for f in with_tok)}, all of them inside on {sum(f['use_max_offset'] < HEAD for f in with_tok)}"
    )
    acts = collections.Counter(library_action(d) for _, d in misses)
    print(f"- the library's action on these misses: {dict(sorted(acts.items()))}")
    heads = [
        f
        for f, d in live
        if library_action(d) == "drop_result"
        and f["use_max_offset"] is not None
        and f["use_max_offset"] < HEAD
    ]
    print(
        f"- drop_result whose kept {HEAD}-char head holds every used token: {len(heads)} ({', '.join(f['session'] + ' ' + f['id'] for f in heads) or 'none'})"
    )
    clipped = [s for s in sessions if "skipped" not in s and s["last_user_chars"] > 500]
    print(
        f"- sessions whose latest prompt is clipped to 500 chars in the goal: {len(clipped)}/{sum('skipped' not in s for s in sessions)} "
        "(the full prompt stays verbatim in the history)"
    )
    pointer = sorted(
        {f["session"] for f in feats if f["goal_names_target"] and f["tool"] == "read"}
    )
    print(
        f"- sessions whose goal points at a file the prefix read (the task body is an omitted output): {len(pointer)} ({', '.join(pointer)})"
    )

    print("\n# 5. Keyless checks behind the hypotheses\n")
    for study in STUDIES:
        pos, neg = scored(study)
        fields = [
            x for x in ("keepCall", "keepResult", "need") if pos[0].get(x) is not None
        ]
        for field in [*fields, "max"]:
            val = (
                (lambda d: max(d[x] for x in fields))
                if field == "max"
                else (lambda d, fld=field: d[fld])
            )
            best = None
            for cut in sorted({val(d) for d in pos + neg}):
                lo, _ = N.R1.wilson(sum(val(d) >= cut for d in pos), len(pos))
                if (
                    lo >= BAR_RECALL_LOWER
                    and sum(val(d) < cut for d in neg) / len(neg) >= BAR_NN_DROPPED
                ):
                    best = cut
                    break
            print(
                f"{study} {field}: a cut meeting the jev-jec6 bar {'EXISTS at ' + str(best) if best is not None else 'does not exist'}"
            )
    dec = {key(d): d for d in N.read_jsonl(STUDIES["jec6"] / "decisions.jsonl")}
    rows = [f for f in free if f["study"] == "jec6" and not f["result_shaken"]]
    pos = [f for f in rows if f["label"] == "needed"]
    neg = [f for f in rows if f["label"] == "not-needed"]
    print(f"\njec6 without shaken outputs: needed {len(pos)}, not-needed {len(neg)}")
    for name, field, cut in (
        ("C0", "keepResult", 0.5),
        ("C1", "keepResult", 0.15),
        ("C2", "need", 0.5),
    ):
        k = sum(dec[key(f)][field] >= cut for f in pos)
        dropped = sum(dec[key(f)][field] < cut for f in neg)
        print(
            f"  {name}: needed kept {rate(k, len(pos))}; not-needed dropped {dropped}/{len(neg)}; "
            f"AUC {auc([dec[key(f)][field] for f in pos], [dec[key(f)][field] for f in neg]):.3f}"
        )

    shown = [(f, d) for f, d in live if codes[key(f)]["visible"] == "goal"]
    rest = [
        (f, d)
        for f, d in live
        if codes[key(f)]["visible"] != "goal"
        and cause(codes[key(f)], f) == "rerun_premise"
    ]
    for name, xs in (
        ("need shown in the goal", shown),
        ("other rerun_premise misses", rest),
    ):
        kr = [d["keepResult"] for _, d in xs]
        nd = [d["need"] for _, d in xs if d.get("need") is not None]
        print(
            f"{name}: n={len(xs)}, keepResult mean {sum(kr) / len(kr):.3f} max {max(kr)}"
            + (
                f"; C2 need mean {sum(nd) / len(nd):.3f} max {max(nd)} (n={len(nd)})"
                if nd
                else ""
            )
        )
    stub_sessions = {f["session"] for f in feats if f["result_shaken"]}
    slice_sessions = sorted({f["session"] for f in feats} - stub_sessions)
    dev = [f for f in free if f["session"] in slice_sessions]
    print(
        f"\nDev slice for the replay loop (no stub outputs, never a held-out set): {len(slice_sessions)} sessions "
        f"({', '.join(slice_sessions)}), unpinned needed {sum(f['label'] == 'needed' for f in dev)}, "
        f"not-needed {sum(f['label'] == 'not-needed' for f in dev)}, undecidable {sum(f['label'] == 'undecidable' for f in dev)}"
    )

    print("\n# 6. Every miss\n")
    print(
        "| study | session | call | tool | cause | used | reobtain | visible | keepCall | keepResult | decisive fact |"
    )
    print("|---|---|---|---|---|---|---|---|---:|---:|---|")
    for f, d in sorted(
        misses,
        key=lambda x: (
            CAUSES.index(cause(codes[key(x[0])], x[0])),
            x[0]["study"],
            x[0]["session"],
            int(x[0]["id"][1:]),
        ),
    ):
        c = codes[key(f)]
        print(
            f"| {f['study']} | {f['session']} | {f['id']} | {f['tool']} | {cause(c, f)} | {c['used']} | {c['reobtain']} | {c['visible']} | {d['keepCall']} | {d['keepResult']} | {c['fact']} |"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
