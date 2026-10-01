import os
import signal
import subprocess


def run(cmd, timeout):
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        out, err = p.communicate(timeout=timeout)
        return (p.returncode, out, err)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                p.kill()
            except OSError:
                pass
        out, err = p.communicate()
        if out is None:
            out = ""
        if err is None:
            err = ""
        return (124, out, err)
