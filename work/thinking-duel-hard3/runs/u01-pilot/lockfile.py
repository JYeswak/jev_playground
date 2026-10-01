import os
import tempfile
import time


def acquire_lock(lock_path, stale_after=10):
    """Return True if the lock was acquired, False otherwise."""
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            try:
                os.write(fd, str(os.getpid()).encode())
            finally:
                os.close(fd)
            return True
        except FileExistsError:
            pass
        try:
            mtime = os.stat(lock_path).st_mtime
        except FileNotFoundError:
            continue
        if time.time() - mtime > stale_after:
            try:
                os.remove(lock_path)
            except FileNotFoundError:
                pass
            continue
        return False


def release_lock(lock_path):
    try:
        os.remove(lock_path)
    except FileNotFoundError:
        pass


def write_atomically(target_path, data):
    directory = os.path.dirname(os.path.abspath(target_path))
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, target_path)
    except BaseException:
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass
        raise
