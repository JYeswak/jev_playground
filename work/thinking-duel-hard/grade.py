#!/usr/bin/env python3
"""Grade one task copy: overlay hidden tests with SYS_PATH/SYSCWD bound, run, report PASS/FAIL."""

import shutil, subprocess, sys, tempfile, os


def grade(task_id, srcdir):
    tmp = tempfile.mkdtemp(prefix=f"duel-{task_id}-")
    for f in os.listdir(srcdir):
        s = os.path.join(srcdir, f)
        if os.path.isfile(s):
            shutil.copy(s, tmp)
    test = open(f"work/thinking-duel-hard/grading/{task_id}.py").read()
    test = test.replace("SYS_PATH", repr(tmp)).replace("SYSCWD", repr(tmp))
    tp = os.path.join(tmp, "test_hidden.py")
    open(tp, "w").write(test)
    t0 = __import__("time").time()
    p = subprocess.run(
        [sys.executable, tp], capture_output=True, text=True, timeout=120, cwd=tmp
    )
    dt = __import__("time").time() - t0
    ok = p.returncode == 0
    tail = (p.stdout + p.stderr).strip().splitlines()
    return ok, dt, tail[-1][:160] if tail else ""


if __name__ == "__main__":
    tid = sys.argv[1]
    src = sys.argv[2] if len(sys.argv) > 2 else f"work/thinking-duel-hard/tasks/{tid}"
    ok, dt, tail = grade(tid, src)
    print(f'{tid}: {"PASS" if ok else "FAIL"} ({dt:.1f}s) {tail}')
    sys.exit(0 if ok else 1)
