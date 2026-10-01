import os
import signal
import subprocess


def run(cmd, timeout):
    # Single merged pipe => stdout+stderr interleaved in arrival order,
    # and only one pipe to drain so no deadlock when either side floods.
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        start_new_session=True,
    )
    try:
        out, _ = p.communicate(timeout=timeout)
        return (p.returncode, out if out is not None else "")
    except subprocess.TimeoutExpired:
        # Kill the whole process tree (children + grandchildren): the
        # child is a session/group leader via start_new_session, so
        # killpg reaches every descendant in the group.
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        try:
            out, _ = p.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                p.kill()
            except OSError:
                pass
            out, _ = p.communicate()
        return (124, out if out else "")
