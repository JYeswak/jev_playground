import subprocess


def run(cmd, timeout):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return (p.returncode, out + err)
    except subprocess.TimeoutExpired:
        return (124, "")
