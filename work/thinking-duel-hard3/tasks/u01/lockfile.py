import os


def acquire_lock(lock_path, stale_after=10):
    """Return True if the lock was acquired, False otherwise."""
    if os.path.exists(lock_path):
        return False
    with open(lock_path, "w") as f:
        f.write(str(os.getpid()))
    return True


def release_lock(lock_path):
    os.remove(lock_path)


def write_atomically(target_path, data):
    with open(target_path, "wb") as f:
        f.write(data)
