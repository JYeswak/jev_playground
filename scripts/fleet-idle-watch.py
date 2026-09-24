#!/usr/bin/env python3
"""Tell pane 1 when a jev worker pane sits idle.

Worker = tmux pane index >= 2 in the jev session (0 is Joshua's shell, 1 is the conductor).
Idle   = the omp status line has no working spinner, for POLLS consecutive polls.
Alert  = `ntm send jev --pane=1 "IDLE pane N ..."`, then again every REALERT seconds while idle.

Why: 2026-09-24, 4 of 6 worker panes sat at their prompts for most of an hour and the
conductor only looked when a callback arrived. Joshua: "dont let that happen again."

  python3 scripts/fleet-idle-watch.py            # run forever (start it under hub)
  python3 scripts/fleet-idle-watch.py --once     # one poll, then the CI-on-main line from
                                                 # scripts/ci-main-status.py (informational);
                                                 # exit 1 if any worker is idle
  python3 scripts/fleet-idle-watch.py --selftest # classifier on real status lines
"""

import os
import re
import subprocess
import sys
import time

SESSION = os.environ.get("JEV_SESSION", "jev")
INTERVAL = int(os.environ.get("IDLE_INTERVAL", "60"))
POLLS = int(os.environ.get("IDLE_POLLS", "2"))
REALERT = int(os.environ.get("IDLE_REALERT", "600"))
SPINNER = re.compile(r"^\s*[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]")
# Comma list of pane indexes to watch; empty = every worker (index >= 2). Set it when some panes
# are down for a known reason (2026-09-24: the five Muse panes hit a quota that resets 09-28).
WATCH = {
    int(p)
    for p in os.environ.get("JEV_WATCH_PANES", "").split(",")
    if p.strip().isdigit()
}
STATUS = re.compile(r"[◒◕]")  # the omp status line carries the model marker


def classify(command: str, screen: str) -> str:
    """working | idle | no-agent, from the pane's foreground command and its visible screen."""
    if command in ("zsh", "bash", "sh", "fish"):
        return "no-agent"
    lines = [line for line in screen.splitlines() if STATUS.search(line)]
    if not lines:
        return "no-agent"
    return "working" if SPINNER.match(lines[-1]) else "idle"


def last_words(screen: str) -> str:
    stripped = [
        line.strip(" │╰╭─") for line in screen.splitlines() if not STATUS.search(line)
    ]
    keep = [line for line in stripped if line]
    return keep[-1][:140] if keep else ""


def poll() -> dict[int, tuple[str, str]]:
    out = subprocess.run(
        [
            "tmux",
            "list-panes",
            "-t",
            SESSION,
            "-F",
            "#{pane_index} #{pane_current_command}",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout
    states = {}
    for row in out.splitlines():
        index, _, command = row.partition(" ")
        if not index.isdigit() or int(index) < 2 or (WATCH and int(index) not in WATCH):
            continue
        screen = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", f"{SESSION}:0.{index}"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
        states[int(index)] = (classify(command, screen), last_words(screen))
    return states


def alert(index: int, since: float, words: str) -> None:
    stamp = time.strftime("%H:%MZ", time.gmtime(since))
    message = f"IDLE pane {index} (since {stamp}), last line: {words}"
    subprocess.run(
        ["ntm", "send", SESSION, "--pane=1", message], capture_output=True, timeout=60
    )
    print(f"{time.strftime('%H:%M:%SZ', time.gmtime())} alerted: {message}", flush=True)


def ci_lines() -> list[str]:
    """scripts/ci-main-status.py's output (bead jev-bfku). Informational: never sets our exit code."""
    script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ci-main-status.py"
    )
    try:
        done = subprocess.run(
            [sys.executable, script], capture_output=True, text=True, timeout=90
        )
    except subprocess.TimeoutExpired:
        return ["CI main NOT_RUN scripts/ci-main-status.py timed out after 90s"]
    lines = done.stdout.splitlines()
    return lines or [
        f"CI main NOT_RUN scripts/ci-main-status.py printed nothing (exit {done.returncode})"
    ]


def selftest() -> int:
    # Status lines captured from the jev session, 2026-09-24T02:0xZ.
    cases = [
        ("bun", " π > ◒ Grok 4.7 > 📁 …/jev > ⑂ main *9 ?121 > S30.63", "idle"),
        (
            "bun",
            " π · ◕ Muse Spark 1.3 · 📁 …/jev · ⑂ main *13 ?122 · ◫ 67.2%/1M ⟲",
            "idle",
        ),
        ("bun", " ⠋ 14m > ◒ Muse Spark 1.3 Contributor > 📁 …/jev", "working"),
        ("bun", " ⠇ 8m · ◕ Muse Spark 1.3 · 📁 ~/Developer/jev", "working"),
        ("zsh", "josh@studio jev %", "no-agent"),
        ("bun", "loading...", "no-agent"),
        # the spinner line wins over an older idle line higher on the screen
        (
            "bun",
            " π · ◕ Muse Spark 1.3\n some output\n ⠙ 2s · ◕ Muse Spark 1.3",
            "working",
        ),
    ]
    bad = [
        (c, s, want, classify(c, s)) for c, s, want in cases if classify(c, s) != want
    ]
    for case in bad:
        print("FAIL", case)
    print(f"selftest: {len(cases) - len(bad)}/{len(cases)} classifications correct")
    return 1 if bad else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    if "--once" in sys.argv:
        states = poll()
        for index, (state, words) in sorted(states.items()):
            print(f"pane {index}: {state}  {words}")
        for line in ci_lines():
            print(line)
        return 1 if any(state != "working" for state, _ in states.values()) else 0
    streak: dict[int, int] = {}
    idle_since: dict[int, float] = {}
    alerted_at: dict[int, float] = {}
    print(f"watching {SESSION} worker panes every {INTERVAL}s", flush=True)
    while True:
        now = time.time()
        for index, (state, words) in poll().items():
            if state == "working":
                streak.pop(index, None)
                idle_since.pop(index, None)
                alerted_at.pop(index, None)
                continue
            streak[index] = streak.get(index, 0) + 1
            idle_since.setdefault(index, now)
            due = now - alerted_at.get(index, 0) >= REALERT
            if streak[index] >= POLLS and due:
                alert(index, idle_since[index], f"[{state}] {words}")
                alerted_at[index] = now
        time.sleep(INTERVAL)


if __name__ == "__main__":
    sys.exit(main())
