#!/usr/bin/env python3
"""Reproduce jev-rknc: `git commit --only -- <shared JSONL>` commits the WHOLE working-tree file.

Fixture = the real incident, rebuilt from history, not typed by hand. Pane 5 committed its one new
bead row to .beads/issues.jsonl with `git commit --only` (e03ef53d) while the working-tree file also
held two peers' uncommitted row edits; all three rows landed in one commit. This script replays that
state in a throwaway repo and runs two landing arms:

  RAW      `git commit --only -- .beads/issues.jsonl`   -> must sweep the peers' rows (the defect)
  PRIVATE  row overlay on the HEAD blob through a private GIT_INDEX_FILE (the AGENTS.md pattern:
           stage your hunk as an index blob) -> must land only the owned row, worktree untouched

Exit 0: defect reproduced AND the private-index control is clean. Exit 1: either claim failed (a
RAW arm that no longer sweeps means a guard or a git change closed the gap: rerun against it and
update jev-rknc). Exit 2: refused before any git write (not a git checkout, rev unreadable, fixture
not isolated). Nothing here writes git config or touches the real repo's index, HEAD or worktree.

When LAND1 (omp-kit ompkit-rc-epic-land-fix-release-dogfood-rz5.86) or the tuxx tracker-write path
ships, put that command in the RAW arm's place: the sweep count must then be 0.

NO-CLAIM: this reproduces git's pathspec semantics on one real incident's rows. It says nothing
about br, Agent Mail, or any omp-kit guard, and a PASS here is not a fix.
"""
import json
import os
import subprocess
import sys

PATH = ".beads/issues.jsonl"
ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REV = sys.argv[1] if len(sys.argv) > 1 else "e03ef53d"

# No inherited GIT_* (a hook-run caller exports GIT_DIR/GIT_INDEX_FILE), no global/system config,
# identity by env so nothing needs `git config`.
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(
    GIT_CONFIG_GLOBAL="/dev/null",
    GIT_CONFIG_NOSYSTEM="1",
    GIT_AUTHOR_NAME="sweep-repro",
    GIT_AUTHOR_EMAIL="sweep-repro@example.invalid",
    GIT_COMMITTER_NAME="sweep-repro",
    GIT_COMMITTER_EMAIL="sweep-repro@example.invalid",
)


def git(cwd, *args, env=None, stdin=None):
    r = subprocess.run(
        ["git", *args], cwd=cwd, env={**ENV, **(env or {})}, input=stdin, capture_output=True, text=True
    )
    if r.returncode:
        raise RuntimeError(f"git {' '.join(args)} (cwd={cwd}) rc={r.returncode}: {r.stderr.strip()}")
    return r.stdout


def rows(text):
    return {json.loads(line)["id"]: line for line in text.splitlines() if line.strip()}


def overlay(base, work, owned):
    """base lines with only the `owned` rows taken from work (replace in place, or insert after the
    row that precedes them in work). Every other line stays byte-identical to base."""
    out = base.splitlines()
    prev = None
    for line in work.splitlines():
        rid = json.loads(line)["id"]
        if rid in owned:
            pos = {json.loads(x)["id"]: i for i, x in enumerate(out)}
            if rid in pos:
                out[pos[rid]] = line
            else:
                out.insert(pos[prev] + 1 if prev in pos else len(out), line)
        prev = rid
    return "\n".join(out) + "\n"


def changed(d, a, b):
    ra, rb = rows(git(d, "show", f"{a}:{PATH}")), rows(git(d, "show", f"{b}:{PATH}"))
    return {i for i in rb if ra.get(i) != rb[i]} | {i for i in ra if i not in rb}


def fixture(scratch, name, base, work):
    d = os.path.join(scratch, name)
    os.makedirs(os.path.join(d, ".beads"))
    git(d, "init", "-q", "-b", "main")
    if os.path.realpath(git(d, "rev-parse", "--show-toplevel").strip()) != os.path.realpath(d):
        sys.exit(f"REFUSED fixture {d} is not its own repo; nothing written")
    target = os.path.join(d, PATH)
    with open(target, "w") as f:
        f.write(base)
    git(d, "add", PATH)
    git(d, "commit", "-q", "-m", "baseline [test]")
    with open(target, "w") as f:  # the shared file now holds the owner's row AND the peers' edits
        f.write(work)
    return d


def main():
    try:
        git(ROOT, "rev-parse", "--git-dir")
        base = git(ROOT, "show", f"{REV}~1:{PATH}")
        work = git(ROOT, "show", f"{REV}:{PATH}")
    except RuntimeError as e:
        print(f"REFUSED {e}")
        return 2
    rb, rw = rows(base), rows(work)
    owned = {i for i in rw if i not in rb}  # rows the committer added
    foreign = {i for i in rw if i in rb and rw[i] != rb[i]}  # existing rows a peer had edited
    if not owned or not foreign:
        print(f"REFUSED rev {REV} is not a mixed-row state (owned={len(owned)} foreign={len(foreign)})")
        return 2
    scratch = os.path.join(ROOT, "var", "agent-tmp", f"commit-only-sweep.{os.getpid()}")
    os.makedirs(scratch)
    with open(os.path.join(scratch, ".owner"), "w") as f:
        f.write(f"pid={os.getpid()}\nlabel=repro-commit-only-sweep\nrepo={ROOT}\n")
    print(f"FIXTURE rev={REV} base_rows={len(rb)} owned={sorted(owned)} foreign={sorted(foreign)} scratch={scratch}")

    d = fixture(scratch, "raw", base, work)
    git(d, "commit", "-q", "--only", "-m", "own row [test]", "--", PATH)
    raw = changed(d, "HEAD~1", "HEAD")
    swept = raw & foreign
    print(f"RAW      git commit --only -- {PATH} -> changed={len(raw)} owned={len(raw & owned)} foreign={len(swept)}")

    d = fixture(scratch, "private", base, work)
    idx = {"GIT_INDEX_FILE": os.path.join(d, ".git", "private.idx")}
    git(d, "read-tree", "HEAD", env=idx)
    blob = git(d, "hash-object", "-w", "--stdin", stdin=overlay(base, work, owned)).strip()
    git(d, "update-index", "--cacheinfo", f"100644,{blob},{PATH}", env=idx)
    tree = git(d, "write-tree", env=idx).strip()
    commit = git(d, "commit-tree", tree, "-p", "HEAD", "-m", "own row [test]").strip()
    git(d, "update-ref", "refs/heads/main", commit)
    priv = changed(d, "HEAD~1", "HEAD")
    with open(os.path.join(d, PATH)) as f:
        wt_same = f.read() == work
    head_rows = rows(git(d, "show", f"HEAD:{PATH}"))
    pending = {i for i in rw if head_rows.get(i) != rw[i]}  # worktree rows still uncommitted
    print(
        f"PRIVATE  row overlay on HEAD blob -> changed={len(priv)} owned={len(priv & owned)} "
        f"foreign={len(priv & foreign)} worktree_unchanged={wt_same} pending_foreign={len(pending & foreign)}"
    )

    reproduced = raw == owned | foreign
    clean = priv == owned and wt_same and pending == foreign
    print(f"VERDICT defect={'reproduced' if reproduced else 'NOT_REPRODUCED'} control={'clean' if clean else 'DIRTY'}")
    return 0 if reproduced and clean else 1


if __name__ == "__main__":
    sys.exit(main())
