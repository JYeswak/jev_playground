# P2 — queue of 3. Finish one, fire its callback, START THE NEXT YOURSELF.

R46 accepted. I verified its load-bearing claim independently from the git binary
(`strings $(git --exec-path)/git` → `post-checkout` present, **`pre-checkout` absent**), so
"nothing can interpose at the losing action" is a fact about git, not an opinion. Refusing a
guard that would nag every legitimate switch in a three-pane tree is the right call, and the
trigger you recorded is the right one.

## Unit 1 — rank 2 from your own census: live numbers quoted without pinned inputs (5 instances)

You now have `pinned-denominator.sh`. **Use it on the lane's real published claims** rather than
building a third guard: walk the public surface — `README.md`, `docs/RULES.md`,
`docs/INTEGRATIONS.md`, `cass-mountain-findings-20260920.md` — and for every count that has a
regeneration command, run the guard.

Report a table: claim → claimed value → regenerated value → agree/DRIFT. **Fix the drifts.**
Where a claim has no regeneration command, that is the finding: say which numbers on our public
surface *cannot* be re-derived at all, because those are the ones that will rot silently.

Boundary to respect: the guard refuses `wc -l file` (output carries the filename). Use a command
that emits a bare count.

## Unit 2 — rank 3: callback sha omission (4 instances)

Your own packet contract says every callback carries a receipt path **and a sha**. Four of
tonight's did not. Check whether this is mechanizable: a callback is a `ntm --robot-send` string,
not a file, so a hook cannot see it — **if it is not mechanizable, write R47 with its trigger
rather than inventing a ceremony.** Same standard as R46: name why, name what would change it.

## Unit 3 — then re-run your census

With rank 1 refused and ranks 2–3 resolved, re-derive the wired-vs-prose table. **The number I
want is how the top-ranked prose-only recurrence count has moved**, not a new list. If the
ranking is unchanged, say so — a census that finds nothing new is a real result and means the
hardening pass has converged.

## Standing

`scripts/vgrep.sh` for any grep used as proof — I hit the silent-zero twice more tonight while
verifying your work, including once inside a man page that was not installed, and the guard
caught it. Exit codes unpiped. Locked export. Commit on create. No formatters or repo-wide gates;
I verify at phase end.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
