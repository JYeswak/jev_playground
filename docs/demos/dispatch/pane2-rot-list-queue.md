# P2 — queue of 3: make the un-checkable numbers checkable

The hardening pass has **converged**: rank 1 and rank 2 are both refused with triggers (R46,
R47), ranking unchanged, no fifth instance across 54 lines of ledger growth. I accept that, and
I verified both refusals independently — R46's "no pre-checkout hook" is confirmed from the git
binary itself (`post-checkout` present, `pre-checkout` absent).

So stop hardening. **The open product gap is your own Unit 1 second table: the public numbers
that have NO regeneration command.** Those are the ones that rot silently, because
`pinned-denominator.sh` cannot check what cannot be regenerated. You named three families.

## Unit 1 — the live-harvest family needs as-of labels

These are counts over a corpus that grows (`77,767 → 78,242` is the documented drift). A bare
number is wrong the day after it is written. Give each one an **as-of label and a regeneration
command**, so the sentence reads as a measurement at a time rather than a standing fact.

Where the corpus is reachable, re-derive today's value and record both. Where it is not, say so
in the sentence itself — **"as of 2026-09-18, not re-derivable today"** is honest and a bare
number is not.

## Unit 2 — the 19-numerator re-sweep

Your audit says this needs a re-sweep. Do the sweep, publish the new value with its denominator
and the command, and **state what changed** — if it moved, that is evidence for the whole
as-of-label argument; if it held, that is evidence the family is more stable than feared. Both
outcomes are worth the run.

## Unit 3 — wire what you can, then stop

For every claim you gave a regeneration command in Units 1–2, add it to the
`pinned-denominator.sh` sweep so the next audit runs it automatically. **Do not build a fourth
guard.** If a claim still cannot be regenerated after your best attempt, list it under a single
heading — *numbers a reader cannot verify and neither can we* — and leave it there. That list,
short and honest, is a better artifact than a guard that pretends to cover it.

## Standing

`scripts/vgrep.sh` for proof-greps, `scripts/pinned-denominator.sh` for counts,
`scripts/pin-liveness.sh` before pinning any new STATUS digest — that last one is new tonight and
fires on exactly the defect that took the lane RED an hour ago.

On your wrong-branch commit: **unwinding it and preserving the peer's lines was the right call.**
The tree branch-switches under us and that is the fourth instance tonight. Keep committing on
create; it is still the cheapest protection we have.

Exit codes unpiped. Commit on create. No formatters or repo-wide gates — I verify at phase end.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
