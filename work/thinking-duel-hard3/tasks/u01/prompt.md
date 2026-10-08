# Task u01: stale lockfiles and atomic writes

Work in $PWD. `lockfile.py` has `acquire_lock(lock_path, stale_after=10)`, `release_lock(lock_path)`, and `write_atomically(target_path, data: bytes)`. It is wrong. Fix it, standard library only. Verify yourself with stale/fresh lock races and overwrite reads.

Rules: `acquire_lock` returns True exactly when this call created the lock; creation must be atomic (no check-then-create race). A pre-existing lock older than `stale_after` seconds (by mtime) is stale: remove it and retry. A fresh lock must be left untouched and reported as False. `release_lock` removes the lock and is a silent no-op when absent. `write_atomically` must never leave a partially-written target behind (write a temp file in the same directory, flush+fsync, `os.replace`) and must leave no temp files around.
