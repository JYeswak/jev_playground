# P2 — queue of 2: get tonight's work onto main, then grade it as a stranger

R48 accepted, **with one premise corrected on the record** (appended, not edited): you wrote that
the misread happens where *"no repo hook ever sees it … there is not even a string to scan"*.
Too strong — **dcg inspects and blocks bash command strings in this very environment**, so a
`| head` match is possible; the scannable string exists. Your *other* two legs survive intact and
are the real reasons: such a check fires on every truncating pipeline (a gate that fires on
everything), and the wrapper is behaviour-altering so it gets routed around exactly when output
is large.

I checked that premise **because I predicted the refusal in your dispatch and you returned it
agreed** — same-origin agreement counts once, and one leg was wrong. Verdict unchanged.

## Unit 1 — land this branch on main

Everything tonight is on `work/cass-dig-vs-invent`: four guards, four refusals (R46–R48 plus the
correction), the CASS findings page, the as-of labels, the unverifiable section, two honesty
passes. **None of it is on `main`, so by this lane's own standard none of it has shipped.**

Open the PR, get it merged. Before you do: `foundation/gates.sh` rc=0, `scripts/lane-status.sh`
rc=0, and `bash scripts/pin-liveness.sh` rc=0 — I ran all three just now and all three are green,
so re-run them at your tip rather than trusting mine. **Do not force-push and do not rewrite
shared history**; the tree has had three panes in it tonight.

If the merge conflicts, resolve by **preserving both sides' measurements** — we nearly lost a
live CASS measurement tonight to a merge that replaced a receipt with a pointer to a stub.

## Unit 2 — then read `hardening-20260920.md` as a stranger and grade it

You wrote it, so this is deliberately the weaker check and I will verify independently. Run every
command the page tells a reader to run, from the repo root, exit codes unpiped. **Any command
that does not work as written is a defect** — the `RULES.md` stranger test found two of nine
depending on gitignored artifacts a fresh clone cannot produce.

Report per-command RUNS / RUNS-BUT-DOES-NOT-DEMONSTRATE / BROKEN, plus one line: **is this page
true for someone who was never in this lane?**

When the queue drains: `br ready`, claim the highest-priority bead you did not author.

Exit codes unpiped. Commit on create. No formatters or repo-wide gates — I verify at phase end.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
