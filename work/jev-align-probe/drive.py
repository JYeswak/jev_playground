#!/usr/bin/env python3
"""Drive `jeva optimize` with a programmatic labeler instead of a human.

jev-align's label picker falls back to line-oriented `console.input()` whenever
stdin is not a TTY (src/jev_align/cli.py:1449). This driver exploits that path:
it reads the rendered card, hands the text to an ORACLE function, and writes the
oracle's answer back on stdin. No human keystroke is involved.

The oracle is supplied by the caller. It is NOT a human label; every receipt
using this driver must say so.

Usage:
  drive.py --oracle gold --gold GOLD.json -- jeva optimize ... (args)
  drive.py --oracle aviation -- jeva optimize ... (args)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import selectors
import subprocess
import sys

AVIATION = re.compile(
    r"\b(aviation|aircraft|airplane|aeroplane|airline|airliner|airport|runway|"
    r"boeing|airbus|cessna|cockpit|pilot|flight|flying|jetliner|helicopter|"
    r"faa|ntsb|avionics|fuselage|turboprop|air traffic)\b",
    re.IGNORECASE,
)

BILLING = re.compile(
    r"\b(bill|bills|billing|invoice|invoices|refund|refunds|reimbursement|"
    r"reimbursements|payment|payments|pay|charge|charges|charged|fee|fees)\b",
    re.IGNORECASE,
)

CONTACT_HUMAN = re.compile(
    r"\b(call|calling|phone|speak|talk|contact|chat with|customer (service|support|"
    r"assistance)|live agent|human|representative|operator|reach (you|someone|"
    r"somebody))\b",
    re.IGNORECASE,
)

NORMALIZE = re.compile(r"[│┃╭╮╰╯━─┏┓┗┛┡┩╇┳┻╋]")


def make_oracle(kind: str, gold_path: str | None):
    if kind == "aviation":

        def oracle(card: str) -> str:
            return "t" if AVIATION.search(card) else "f"

        return oracle
    if kind == "billing":

        def oracle(card: str) -> str:
            return "t" if BILLING.search(card) else "f"

        return oracle
    if kind == "contact":

        def oracle(card: str) -> str:
            return "t" if CONTACT_HUMAN.search(card) else "f"

        return oracle
    if kind == "gold":
        with open(gold_path, "r", encoding="utf-8") as handle:
            gold = json.load(handle)

        # gold: [{"needle": <unique normalized substring>, "label": "<answer>"}]
        # Needles are built by export-failure-gold.mjs against the SAME
        # normalization applied here, so box glyphs and soft wrapping in the
        # rendered card cannot break the match.
        def oracle(card: str) -> str:
            flat = NORMALIZE.sub(" ", card)
            flat = re.sub(r"\s+", " ", flat).strip()
            hits = [g for g in gold if g["needle"] in flat]
            if len(hits) != 1:
                raise SystemExit(
                    f"ORACLE-AMBIGUOUS: {len(hits)} gold rows match this card:\n"
                    f"{flat[-1200:]}"
                )
            return hits[0]["label"]

        return oracle
    raise SystemExit(f"unknown oracle: {kind}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle", required=True)
    parser.add_argument("--gold")
    parser.add_argument(
        "--decision", default="a", help="answer at the GEPA proposal gate"
    )
    parser.add_argument("--max-labels", type=int, default=200)
    parser.add_argument("cmd", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd
    if not cmd:
        raise SystemExit("no command given")

    oracle = make_oracle(args.oracle, args.gold)

    env = dict(os.environ, JEVA_DISABLE_UPDATE_CHECK="1", TERM="dumb", COLUMNS="120")
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        bufsize=0,
    )
    assert proc.stdin and proc.stdout

    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)

    transcript: list[str] = []
    pending = ""  # text since the last answered prompt (the current card)
    labels_given = 0
    answers_log: list[dict] = []

    def send(text: str, why: str) -> None:
        sys.stdout.write(f"\n<<DRIVER {why}: {text!r}>>\n")
        sys.stdout.flush()
        proc.stdin.write((text + "\n").encode())
        proc.stdin.flush()

    while True:
        if proc.poll() is not None:
            rest = proc.stdout.read()
            if rest:
                chunk = rest.decode("utf-8", "replace")
                transcript.append(chunk)
                sys.stdout.write(chunk)
            break
        events = sel.select(timeout=1.0)
        if not events:
            continue
        data = os.read(proc.stdout.fileno(), 65536)
        if not data:
            continue
        chunk = data.decode("utf-8", "replace")
        transcript.append(chunk)
        pending += chunk
        sys.stdout.write(chunk)
        sys.stdout.flush()

        tail = pending[-200:]
        # Prompts are written without a trailing newline by rich's console.input.
        if re.search(r"Label \([^)]*\): $", tail):
            if labels_given >= args.max_labels:
                send("q", "label-cap-reached")
                continue
            answer = oracle(pending)
            answers_log.append({"n": labels_given + 1, "answer": answer})
            send(answer, f"label #{labels_given + 1}")
            labels_given += 1
            pending = ""
        elif re.search(r"Rationale.*: $", tail):
            send("", "rationale (blank)")
            pending = ""
        elif re.search(r"AI Function decision \([^)]*\): $", tail):
            send(args.decision, "decision gate")
            pending = ""
        elif re.search(r"Level \([^)]*\): $", tail):
            answer = oracle(pending)
            answers_log.append({"n": labels_given + 1, "answer": answer})
            send(answer, f"level #{labels_given + 1}")
            labels_given += 1
            pending = ""

    sys.stdout.write(
        f"\n<<DRIVER DONE: exit={proc.returncode} labels_fed={labels_given}>>\n"
    )
    sys.stdout.write("<<DRIVER ANSWERS: " + json.dumps(answers_log) + ">>\n")
    return proc.returncode or 0


if __name__ == "__main__":
    sys.exit(main())
