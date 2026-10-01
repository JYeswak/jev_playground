# Task t05: bounded subprocess runner

Work in $PWD. `runbox.py` has `run(cmd, timeout)` returning
`(exit_code, stdout, stderr)` (stdout/stderr as str). It must: enforce the
timeout (return exit_code 124 with partial output on expiry), never deadlock
on large stderr while stdout is small (and vice versa), and never leave a
runaway child (kill the process group). It is wrong. Fix it, standard
library only. Verify yourself with slow and chatty commands.
