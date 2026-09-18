# JEV conductor tick — every 20 minutes. Automated. Not a human message.

You are the on-duty conductor (a pane or a process holding the conductor brief).
Joshua's standing order: the demo loop ships installable Jev demos repeatedly,
and without this tick it stops the moment the conductor goes quiet.

NO AUTO-DISPATCH EXISTS. You send project-aware dispatches by hand. This tick
only guarantees the loop is ASKED about every 20 minutes — and every dispatch
you send REQUIRES the callback contract in §2. A tick that moves nothing and
sends nothing is a tick you must explain in one line, not skip.

## 0. STAGE CENSUS — first line of every tick action, re-derived never cited

```
DEMO <HH:MMZ> backlog N · active <demo-id or none> · beads live L · closed C
```

Backlog authority: `docs/demos/PLAN.md`. WIP LIMIT IS ONE DEMO: no second demo
starts before the active one ships (install + tests + receipt + EVAL row).

## 1. CHECK ALL WORKERS

Panes are 1, 2, 3 (0 is the user shell — never dispatch it). For each worker,
read THESE THREE surfaces (a silent finished pane is indistinguishable from a
working one — missing callbacks are the norm, not the exception):

```
br list                                    # live beads; closed excluded by default
br list --status closed                    # what landed since last tick
am inbox --project ~/Developer/jev --agent <YOU>   # DONE/BLOCKED/NEEDS-RULING mail
git log --oneline -8                       # what actually committed
git status --porcelain                      # uncommitted deliveries sitting in tree
```

Never `capture-pane | grep`. Idle + no callback + fresh files = silent finish:
read the artifacts, then ask the pane directly what happened.

## 2. THE CALLBACK CONTRACT — every packet you send MUST state this

Measured 2026-09-17: six dispatches with "report here" and no path produced
zero callbacks; both finished beads were discovered by filesystem archaeology.
A missing callback is a defect in YOUR packet, not in the pane.

```
REPLY-VIA (all FOUR, fire the moment the unit lands — DONE, BLOCKED, or
NEEDS-RULING; a BLOCKED callback is a SUCCESS, it routes around the unknown):
1. THE ONLY LEG THAT WAKES THE CONDUCTOR — legs 2-4 are all PULL:
   `ntm --robot-send=jev --panes=1 --msg="CALLBACK-P<N>-<UNIT>-<DONE|BLOCKED>:
    <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
2. `br comments add <bead> --actor <YOU> -m "<OUTCOME> <receipt path> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to <CONDUCTOR>
   -s "[<bead>] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
   (find <CONDUCTOR> via `am agents list ~/Developer/jev`)
4. Receipt file in tree (runs/ or docs/), committed with own-files-only.
Carry: bead id · commit sha · NEXT (what you'd pick up unprompted) ·
NO-CLAIM (exact limit of what you proved).
```

**EVERY PACKET SHIPS A QUEUE, NOT A TASK.** A pane that finishes a single-unit
packet is idle until the next tick — up to 20 minutes of a worker doing nothing
while the conductor is between turns. Measured 2026-09-18: two panes delivered
cross-scores and both went idle waiting for a relay that only a human chase
produced. So every packet carries 2–3 numbered units and this line verbatim:
**"Finish one, fire its callback, then start the next YOURSELF. Do not wait for
a dispatch between them."** A blocked unit is a callback too — fire it and move
to the next unit. The only failure mode is silence.

The REPLY-VIA `NEXT` field is therefore not a suggestion to the conductor: it is
the pane's own next unit, named in the packet, which it self-claims.

**A QUEUE IS NOT SELF-SUSTAINING. SHIP A DRY-QUEUE DEFAULT.** Measured
2026-09-18, one hour after the clause above was written: pane 3 was given a
3-unit queue, completed all three (`11c3c33`, `3f765a9`, `fa15c47`), and went
idle anyway — because a finite queue is just a longer task list. A human chase
found it, again. So every packet also carries a standing rule for the empty
queue, in priority order: (1) review the highest-value **unreviewed** artifact
in the lane — one grader, zero graders, or an unaudited claim — non-author
only; (2) the oldest `NEGATIVE_EVIDENCE.md` item whose retry condition has
become satisfiable, or a `GATES.md` gap with no witness; (3) fire a **QUEUE
DRY** callback naming what was considered and rejected. (3) is a success. It
has never yet been true.

**NEVER PUSH INTO A WORKING PANE.** `ntm --robot-send` types into the pane's
prompt, so a pane mid-unit gets interrupted and the interruption is invisible
to you. Measured 2026-09-18: pane 2 was sent a queue extension while working
through unit 3. Push ONLY to a pane that is idle or whose callback just landed.
To extend a working pane's queue, append to its queue file
(`docs/demos/**/dispatch/<pane>-*.md`) and let it read at the unit boundary, or
use `am mail`, which is pull. A DONE callback in this turn is consent; silence
is not.

**VERIFY LEG 2, DO NOT ASSUME IT.** Measured 2026-09-18: `am inbox --agent
CyanFalcon` returned `count: 0` after two panes had delivered six units. Every
bead comment and every commit landed; not one `am mail` arrived — both panes
routed callbacks through the pane relay instead. A three-leg contract with one
silently dead leg is a two-leg contract that looks like three. Read the inbox
during §1, and when a packet asks for leg 2, require the pane to report what
the send returned.

**AND CHECK THE ARTIFACTS BEFORE REPORTING A PANE'S STATE.** Measured
2026-09-18: the conductor reported pane 3 as "no callback yet" while all three
of its units sat committed in `git log`. Idle + fresh commits = silent finish,
not silence. §1 names the surfaces for a reason; inferring a pane's state from
the absence of a message is the same instrument error as trusting a summary
over a receipt.

**NAME EVERY ARTIFACT BY ITS FULL REPO-RELATIVE PATH.** Measured 2026-09-18: a packet said
*"audit `DUELING_WIZARDS_REPORT.md`"* — a bare filename — and the pane correctly reported it
BLOCKED/absent, twice, while the file sat tracked at
`docs/demos/duel-1/DUELING_WIZARDS_REPORT.md` in the pane's own tree (`a765840`, the parent of
that pane's next commit). Every other artifact in the same packet carried a full path; this one did
not, so the pane was asked to guess a directory. This is the same defect as the "report here" with
no path that produced zero callbacks — committed *in the packet that quotes the rule*. A bare
filename is a defective packet, and BLOCKED is the correct response to one.

**AN ABORTED TOOL CALL PROVES NOTHING EITHER WAY.** Measured 2026-09-18: a batched call that was
going to both send a packet and file a bead was aborted mid-flight. The bead did not exist
(re-derived: count unchanged at 15) and the send had produced no success line, yet a later pane
callback was the only hint. Do not batch a dispatch with a bead filing: on abort you cannot tell
which half landed, and "sender success is not receiver receipt" degrades to "no sender result at
all". Re-derive both sides, then re-issue the missing one alone.

**LEG 1 IS `ntm --robot-send` TO PANE 1. THE OTHER THREE DO NOT WAKE YOU.** Joshua, 2026-09-18,
after finding the whole lane idle: *"your callbacks need to tell workers to send you a message
back at pane 1 via ntm send when they are done."* The contract above lists a bead comment, mail,
and a committed receipt — and **all three are PULL.** A bead comment sits in the store, mail sits
in an inbox, a commit sits in the log; the conductor only sees any of them by polling, and between
turns the conductor is not polling. So every packet MUST require, as the FIRST leg:

```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P<N>-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."
```

**This was already the only leg that ever worked, and the evidence was sitting in plain sight.**
Every pane-2 callback this session arrived promptly — because pane 2 was sending this message
unprompted. Every pane-3 unit was discovered by archaeology, and pane 3 sat idle ~35 minutes —
because pane 3 was not. Same instructions, one pane inventing the missing leg. The conductor read
that asymmetry as "pane 2 is more diligent" instead of "my contract has no push leg", and
separately blamed `am mail` (leg 3) for a silence that a push leg would have prevented regardless.

Corollary: the conductor's own census is not a substitute. `fleet-idle-monitor` reported
`WORKING pane=%73` while pane 3 was idle, and the conductor repeated it as fact **in the same turn
it retracted a claim about that binary's false-WORKING defect**. A push callback is the only
worker-state signal that does not depend on an instrument the conductor has already measured as
unreliable.

## 3. DISPATCH — project-aware, by hand, in this order

0. DONE callback → close (conductor classifies) → dispatch that pane's NEXT
   same turn. Any miss → grade via a NON-AUTHOR pane.
1. Grading-ready beads → non-author, different pane.
2. The active demo's critical path (plan → beads → build → ship).
3. Backlog grooming only when no demo is active.
4. Re-derive every COUNT a bead's acceptance asserts before dispatching.
   Never dispatch a bead whose acceptance is unobtainable.

## 4. WHAT ARE *YOU* DOING

If all three panes are genuinely working, you are not done — hold your own
claimed bead and work it. Do not manufacture a packet to look busy, and do not
sit watching timers.
