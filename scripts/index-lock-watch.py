#!/usr/bin/env python3
"""Event-driven .git/index.lock creator capture (jev-ih96).

The 60 s poller (fleet-idle-watch capture_lock_creator) sees only abandoned
locks: git exits within seconds. This watches .git/ with kqueue and captures
(pid, argv, parent chain, tmux pane) the instant index.lock appears.

LOG-ONLY: read-only probes (pgrep/lsof/ps/tmux). Never creates, moves, or
deletes the lock or any repo file. Same JSONL row schema as
fleet-idle-watch capture rows plus "trigger":"event".

Usage:
  python3 scripts/index-lock-watch.py [--repo DIR] [--once] [--log PATH] [--state PATH]
  --once exits after one scan (no kqueue); default loops on kqueue events.
"""

from __future__ import annotations

import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

LOG_REL = "state/jev/index-lock-creators.jsonl"
STATE_REL = "state/jev/index-lock-watch-event.json"
HOME = str(Path.home())


def ident_of(lock: Path):
    try:
        st = lock.stat()
    except OSError:
        return None
    return [st.st_dev, st.st_ino, st.st_mtime_ns, st.st_size]


def proc_field(pid, field, run=subprocess.run):
    try:
        out = run(
            ["ps", "-o", field + "=", "-p", str(pid)],
            capture_output=True,
            text=True,
            timeout=4,
        ).stdout.strip()
    except Exception:
        return None
    return out[:300] or None


def holders_of(lock: Path, run=subprocess.run):
    """PIDs with the lock open. Single fast `lsof -t` scan first; bounded
    targeted fallback. The old pgrep-every-git loop stalled minutes under
    fleet load (10 s timeout x 50 pids), starving the kqueue loop."""
    try:
        out = run(
            ["lsof", "-t", str(lock)], capture_output=True, text=True, timeout=15
        ).stdout.split()
        if out:
            return out
    except Exception:
        pass
    try:
        gitpids = run(
            ["pgrep", "-f", "(^|/)git( |$)"], capture_output=True, text=True, timeout=5
        ).stdout.split()
    except Exception:
        return []
    for pid in gitpids[:10]:
        try:
            out = run(
                ["lsof", "-p", str(pid)], capture_output=True, text=True, timeout=3
            ).stdout
        except Exception:
            continue
        if str(lock) in out:
            return [str(pid)]
    return []


def ancestors_of(pid, run=subprocess.run, depth=6):
    chain = []
    at, seen = str(pid), {str(pid)}
    for _ in range(depth):
        ppid = proc_field(at, "ppid", run)
        if not ppid or not ppid.strip().isdigit():
            break
        at = ppid.strip()
        if at in seen or at == "1":
            break
        seen.add(at)
        chain.append({"pid": at, "argv": proc_field(at, "command", run)})
    return chain


def pane_for_pid_tree(pids, run=subprocess.run):
    """Map any pid (or its ancestors) to its tmux pane via pane-shell ancestry."""
    try:
        out = run(
            ["tmux", "list-panes", "-s", "-F", "#{pane_pid} #{pane_id}"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except Exception:
        return None
    panes = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            panes[parts[0]] = parts[1]
    for pid in pids:
        at, seen = str(pid), set()
        for _ in range(8):
            if at in panes:
                return panes[at]
            if at in seen:
                break
            seen.add(at)
            ppid = proc_field(at, "ppid", run)
            if not ppid or not ppid.strip().isdigit():
                break
            at = ppid.strip()
    return None


def capture_once(repo, log_path=None, state_path=None, run=subprocess.run, now=None):
    """Capture the lock's holders iff its identity changed since last sight."""
    lock = Path(repo) / ".git" / "index.lock"
    log = Path(log_path) if log_path else Path(HOME) / LOG_REL
    statep = Path(state_path) if state_path else Path(HOME) / STATE_REL
    ident = ident_of(lock)
    try:
        prev = json.loads(statep.read_text()) if statep.exists() else None
    except (OSError, ValueError):
        prev = None
    if ident is None:
        if prev is not None:
            try:
                statep.write_text("null")
            except OSError:
                pass
        return None
    if prev == ident:
        return None
    pids = holders_of(lock, run)
    chain = []
    for pid in pids:
        if any(h["pid"] == pid for h in chain):
            continue
        chain.append(
            {
                "pid": pid,
                "argv": proc_field(pid, "command", run),
                "parents": ancestors_of(pid, run),
            }
        )
    allpids = list(pids) + [a["pid"] for h in chain for a in h["parents"]]
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now or time.time())),
        "lock": str(lock),
        "size": ident[3],
        "holders": chain,
        "pane": pane_for_pid_tree(allpids, run),
        "trigger": "event",
    }
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(log), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "a") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass
    try:
        statep.parent.mkdir(parents=True, exist_ok=True)
        statep.write_text(json.dumps(ident))
    except OSError:
        pass
    return row


OPS_REL = "state/jev/index-lock-watch-ops.jsonl"


def ts_now(when=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(when or time.time()))


def ops_write(ops_path, row):
    """Best-effort ops row (heartbeat / fs-event). Never throws."""
    try:
        ops_path = Path(ops_path)
        ops_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(ops_path), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "a") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass


def watch(
    repo,
    log_path=None,
    state_path=None,
    once=False,
    run=subprocess.run,
    ops_path=None,
    max_iters=None,
):
    """kqueue on .git/; capture on every directory change plus one scan now."""
    ops_path = Path(ops_path) if ops_path else Path(HOME) / OPS_REL
    ops_write(ops_path, {"ts": ts_now(), "type": "start", "pid": os.getpid()})
    row = capture_once(repo, log_path, state_path, run)
    if row:
        print(json.dumps(row), flush=True)
    if once:
        return 0
    gitdir = Path(repo) / ".git"
    fd = os.open(str(gitdir), os.O_RDONLY)
    try:
        kq = select.kqueue()
        kq.control(
            [
                select.kevent(
                    fd,
                    select.KQ_FILTER_VNODE,
                    select.KQ_EV_ADD | select.KQ_EV_CLEAR,
                    select.KQ_NOTE_WRITE | select.KQ_NOTE_EXTEND,
                )
            ],
            0,
            0,
        )
        last_hb, events, iters = 0.0, 0, 0
        while True:
            events = _poll_once(kq, repo, log_path, state_path, ops_path, run, events)
            now = time.time()
            if now - last_hb >= 60:
                ops_write(
                    ops_path,
                    {"ts": ts_now(), "type": "heartbeat", "events_seen": events},
                )
                last_hb = now
            iters += 1
            if max_iters is not None and iters >= max_iters:
                return 0
    finally:
        os.close(fd)


def _poll_once(kq, repo, log_path, state_path, ops_path, run, events):
    """One kqueue wait + capture. Returns updated events_seen. Test seam."""
    woke = kq.control(None, 1, 60)
    if woke:
        # Raw fs event BEFORE any lsof: a later miss with no fs-event
        # row means kqueue never fired; a miss WITH one means the
        # holder exited between event and capture.
        events += len(woke)
        ops_write(ops_path, {"ts": ts_now(), "type": "fs-event", "nevents": len(woke)})
    row = capture_once(repo, log_path, state_path, run)
    if row:
        print(json.dumps(row), flush=True)
    return events


def main(argv):
    repo = str(Path(argv[argv.index("--repo") + 1]) if "--repo" in argv else Path.cwd())
    log = argv[argv.index("--log") + 1] if "--log" in argv else None
    state = argv[argv.index("--state") + 1] if "--state" in argv else None
    return watch(repo, log, state, once="--once" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
