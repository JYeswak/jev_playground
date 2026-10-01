# Task t05b: streaming runner with process-tree kill

Work in $PWD. `runbox.py` has `run(cmd, timeout)` returning
`(exit_code, merged)` where merged is stdout+stderr interleaved in arrival
order as text. It must enforce the timeout (exit 124), never deadlock when
either pipe floods, and kill the whole process tree including grandchildren
(start_new_session + killpg). shipped code returns separate streams, leaks
grandchildren, and can deadlock. Fix it, stdlib only. Verify with flooding
and sleepy-grandchild commands.
