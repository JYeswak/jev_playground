#!/usr/bin/env python3
"""Readout 3b of the gate-observe hook log (bead jev-5lgy). No key, no network, no Jev call.

Readout 3 (jev-ribc, readout3.py) left 71 of 137 live fleet rows undecidable because the hook logs
only a 200-character prefix. The three fleet sessions' omp transcripts hold every bash call's full
command. This readout recovers those commands, has two fresh labellers label them blind, and
re-scores all 137 rows with readout 3's metrics.

Rules (preregistered in docs/demos/upstream-repro/gate-observe-dogfood-3b-20260924.md):
  TARGET ROWS  the live rows whose readout 3 final label is "undecidable" (readout3.final_labels()).
  CANDIDATE    a bash toolCall in the transcript of the row's own session whose entry timestamp is at
               or before the row's ts, and whose command, after the hook's own redact() (home -> ~,
               trim, secret shapes scrubbed, 200 characters), equals the row's logged prefix.
  MATCH        the candidate with the latest timestamp. Two candidates at that same latest timestamp
               are a TIE. No candidate is a MISS. A matched command whose sha256 differs from the row's
               cmdSha is a SHA-MISMATCH. A tie, a miss or a mismatch gets no text: never a guess.
  FULL TEXT    the hook's redaction without the cut (home -> ~, trim, secret shapes scrubbed), then
               the extract's withhold rule: withheld if it matches PRIVATE or SECRET or holds the home
               path. The redaction runs in the hook's own module (node), not a copy.

Order, enforced here: `extract` writes no flag and no probability. `score` refuses until both new
label files and an adjudication of every disagreement are committed and clean.

  python3 work/gate-observe-dogfood/readout3b.py extract   # needs the transcripts; writes extract-3b.jsonl
  python3 work/gate-observe-dogfood/readout3b.py queue     # the matched rows' full text, for labelling
  python3 work/gate-observe-dogfood/readout3b.py disagreements
  python3 work/gate-observe-dogfood/readout3b.py [score]   # committed files only
"""

import glob
import hashlib
import hmac
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
import readout as R1  # noqa: E402  filters(), HOME, wilson()
import readout3 as R3  # noqa: E402  split(), final_labels(), committed(), labels_of(), report()

EXTRACT = os.path.join(HERE, "extract-3b.jsonl")
LABELS_1 = os.path.join(
    HERE, "labels-3b-full-1.jsonl"
)  # fresh labeller 1, spawned by pane 1
LABELS_2 = os.path.join(
    HERE, "labels-3b-full-2.jsonl"
)  # fresh labeller 2, spawned by pane 1
ADJUDICATED = os.path.join(
    HERE, "labels-3b-full-adjudicated.jsonl"
)  # pane 1, disagreements only
HOOK = ".omp/hooks/post/jev-gate-observe.ts"
REDACT_JS = f"""
import {{ redact, FILTERS }} from "./{HOOK}";
import {{ homedir }} from "node:os";
let s = "";
for await (const c of process.stdin) s += c;
if (!FILTERS) {{ console.error("hook filters unavailable"); process.exit(2); }}
const out = JSON.parse(s).map((c) => ({{
  prefix: redact(c),
  full: c.replaceAll(homedir(), "~").trim().replace(FILTERS.scrubRe, "[REDACTED]"),
}}));
process.stdout.write(JSON.stringify(out));
"""


def transcript(session):
    roots = [f"{R1.HOME}/.omp/agent/sessions"] + glob.glob(
        f"{R1.HOME}/.omp/profiles/*/agent/sessions"
    )
    found = [f for root in roots for f in glob.glob(f"{root}/*/*_{session}.jsonl")]
    if len(found) != 1:
        raise SystemExit(
            f"REFUSED: session {session} has {len(found)} transcript files, want 1: {found}"
        )
    return found[0]


def bash_calls(path):
    calls = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            e = json.loads(line)
            m = e.get("message")
            if not isinstance(m, dict) or m.get("role") != "assistant":
                continue
            for c in m.get("content") or []:
                if (
                    isinstance(c, dict)
                    and c.get("type") == "toolCall"
                    and c.get("name") == "bash"
                ):
                    cmd = (c.get("arguments") or {}).get("command")
                    if isinstance(cmd, str):
                        calls.append({"ts": e.get("timestamp"), "command": cmd})
    return calls


def hook_redact(commands):
    proc = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--no-warnings",
            "--input-type=module",
            "-e",
            REDACT_JS,
        ],
        input=json.dumps(commands),
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(
            f"REFUSED: the hook's redact failed: {proc.stderr.strip()[:300]}"
        )
    return json.loads(proc.stdout)


def targets():
    rows = R3.read_jsonl(R3.EXTRACT)
    _, _, live = R3.split(rows)
    got = R3.final_labels(live)
    if isinstance(got, str):
        raise SystemExit(got)
    final = got[4]
    return [r for r in live if final[r["i"]] == "undecidable"], live, final


def extract():
    rows, _, _ = targets()
    private, secret = R1.filters()
    out = []
    for session in sorted({r["session"] for r in rows}):
        calls = bash_calls(transcript(session))
        red = hook_redact([c["command"] for c in calls])
        for c, x in zip(calls, red):
            c.update(x)
        for r in (r for r in rows if r["session"] == session):
            cands = [
                c
                for c in calls
                if c["ts"] and c["ts"] <= r["ts"] and c["prefix"] == r["cmd"]
            ]
            rec = {
                "i": r["i"],
                "session": session,
                "ts": r["ts"],
                "cmdSha": r["cmdSha"],
                "candidates": len(cands),
            }
            if not cands:
                rec.update(status="miss", match_ts=None, full=None, withheld=False)
            else:
                latest = max(c["ts"] for c in cands)
                best = [c for c in cands if c["ts"] == latest]
                if len(best) > 1:
                    rec.update(status="tie", match_ts=latest, full=None, withheld=False)
                elif not hmac.compare_digest(
                    hashlib.sha256(best[0]["command"].encode("utf-8")).hexdigest(),
                    str(r["cmdSha"]),
                ):
                    rec.update(
                        status="sha-mismatch",
                        match_ts=latest,
                        full=None,
                        withheld=False,
                    )
                else:
                    full = best[0]["full"]
                    withheld = bool(
                        private.search(full) or secret.search(full) or R1.HOME in full
                    )
                    rec.update(
                        status="matched",
                        match_ts=latest,
                        full=None if withheld else full,
                        withheld=withheld,
                        fullLen=len(full),
                    )
            out.append(rec)
    out.sort(key=lambda x: x["i"])
    with open(EXTRACT, "w", encoding="utf-8") as fh:
        for rec in out:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    counts = {
        s: sum(r["status"] == s for r in out)
        for s in ("matched", "miss", "tie", "sha-mismatch")
    }
    print(
        json.dumps(
            {
                "extract": EXTRACT,
                "rows": len(out),
                **counts,
                "withheld": sum(r["withheld"] for r in out),
            }
        )
    )


def queue():
    for r in R3.read_jsonl(EXTRACT):
        if r["status"] == "matched":
            text = "(withheld)" if r["withheld"] else r["full"].replace("\n", " ⏎ ")
            print(f"{r['i']:3d} {r['session'][:8]} | {text}")


def label_rows():
    """Rows the new labellers label: matched rows of extract-3b (withheld ones take 'withheld')."""
    return [r for r in R3.read_jsonl(EXTRACT) if r["status"] == "matched"]


def check_labels(path, rows):
    labels = {x["i"]: x["label"] for x in R3.read_jsonl(path)}
    ids = {r["i"] for r in rows}
    bad = sorted(i for i, lab in labels.items() if lab not in R3.LABELS_ALLOWED)
    extra = sorted(set(labels) - ids)
    missing = sorted(ids - set(labels))
    wrong = sorted(
        r["i"]
        for r in rows
        if r["i"] in labels and (labels[r["i"]] == "withheld") != r["withheld"]
    )
    for what, found in (
        ("labels outside the allowed set", bad),
        ("labels for rows not in the label set", extra),
        ("rows without a label", missing),
        ("withheld labels that disagree with the extract", wrong),
    ):
        if found:
            return (
                f"REFUSED: {os.path.basename(path)}: {len(found)} {what}: {found[:20]}"
            )
    return labels


def new_labels():
    rows = label_rows()
    for path in (LABELS_1, LABELS_2):
        if not os.path.exists(path) or not R3.committed(path):
            return f"REFUSED: {os.path.basename(path)} is not committed and clean"
    one, two = check_labels(LABELS_1, rows), check_labels(LABELS_2, rows)
    for got in (one, two):
        if isinstance(got, str):
            return got
    split_ids = [r["i"] for r in rows if one[r["i"]] != two[r["i"]]]
    adj = {}
    if split_ids:
        if not os.path.exists(ADJUDICATED) or not R3.committed(ADJUDICATED):
            return f"REFUSED: {len(split_ids)} disagreements and {os.path.basename(ADJUDICATED)} is not committed and clean"
        adj = {x["i"]: x["label"] for x in R3.read_jsonl(ADJUDICATED)}
        missing = [
            i for i in split_ids if i not in adj or adj[i] not in R3.LABELS_ALLOWED
        ]
        if missing:
            return f"REFUSED: {len(missing)} disagreements have no valid adjudicated label: {missing[:20]}"
    final = {
        r["i"]: (one[r["i"]] if one[r["i"]] == two[r["i"]] else adj[r["i"]])
        for r in rows
    }
    return one, two, adj, split_ids, final


def disagreements():
    if not os.path.exists(EXTRACT):
        print("REFUSED: no extract-3b.jsonl")
        return 1
    rows = label_rows()
    for path in (LABELS_1, LABELS_2):
        if not os.path.exists(path) or not R3.committed(path):
            print(f"REFUSED: {os.path.basename(path)} is not committed and clean")
            return 1
    one, two = check_labels(LABELS_1, rows), check_labels(LABELS_2, rows)
    for x in (one, two):
        if isinstance(x, str):
            print(x)
            return 1
    split = [r for r in rows if one[r["i"]] != two[r["i"]]]
    print(
        f"# {len(split)} disagreements of {len(rows)} matched rows (flags not joined)"
    )
    for r in split:
        text = "(withheld)" if r["withheld"] else r["full"].replace("\n", " ⏎ ")
        print(f"{r['i']:3d} L1={one[r['i']]} L2={two[r['i']]} | {text}")
    return 0


def score():
    if not os.path.exists(EXTRACT) or not os.path.exists(R3.FLAGS):
        print("REFUSED: extract-3b.jsonl and readout 3's flags-3.jsonl are both needed")
        return 1
    got = new_labels()
    if isinstance(got, str):
        print(got)
        return 1
    one, two, adj, split_ids, new = got
    _, live, final3 = targets()
    rows3b = {r["i"]: r for r in R3.read_jsonl(EXTRACT)}
    flag = {x["i"]: x for x in R3.read_jsonl(R3.FLAGS)}
    final = {i: new.get(i, lab) for i, lab in final3.items()}
    status = {
        s: sum(r["status"] == s for r in rows3b.values())
        for s in ("matched", "miss", "tie", "sha-mismatch")
    }
    print(
        f"readout 3 undecidable rows: {len(rows3b)}; match: {status}; withheld {sum(r['withheld'] for r in rows3b.values())}"
    )
    for r in rows3b.values():
        if r["status"] != "matched":
            print(
                f"  not matched: i={r['i']} {r['status']} (candidates {r['candidates']})"
            )
    ids = [r["i"] for r in label_rows()]
    n, po, k = R3.kappa(one, two, ids)
    kt = "undefined" if k is None else f"{k:.3f}"
    print(
        f"\nnew labellers on {len(ids)} matched rows: exact agreement {len(ids) - len(split_ids)}/{len(ids)}; "
        f"Cohen's kappa harm vs no-harm over {n} rows both found decidable: {kt}"
        + (f" (observed {po:.3f})" if po is not None else "")
    )
    print(f"disagreements adjudicated: {len(split_ids)}")
    moved = {c: sum(R3.klass(new[i]) == c for i in new) for c in R3.CLASSES}
    print(f"readout 3 undecidable rows, relabelled from full text: {moved}")
    R3.report(
        live,
        final,
        flag,
        "HEADLINE: all 137 live rows, readout 3 labels with the 3b labels on matched rows",
    )
    R3.report(
        [r for r in live if r["i"] in new], new, flag, "the relabelled rows alone"
    )
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "score"
    if mode == "extract":
        extract()
    elif mode == "queue":
        queue()
    elif mode == "disagreements":
        sys.exit(disagreements())
    elif mode == "score":
        sys.exit(score())
    else:
        print(__doc__)
        sys.exit(64)
