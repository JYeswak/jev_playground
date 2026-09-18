# JEV conductor tick — every 20 minutes. Automated. Not a human message.

You are the on-duty conductor (a pane or a process holding the conductor brief).
Joshua's standing order: the demo loop ships installable Jev demos repeatedly,
and without this tick it stops the moment the conductor goes quiet.

NO AUTO-DISPATCH EXISTS. You send project-aware dispatches by hand. This tick
only guarantees the loop is ASKED about every 20 minutes — and every dispatch
you send REQUIRES the callback contract in §2. A tick that moves nothing and
sends nothing is a tick you must explain in one line, not skip.

## 0. PULL LIVE STATUS — FIRST ACTION OF EVERY TICK, BEFORE ANY PROSE

```bash
./scripts/lane-status.sh          # exits 3 if any verdict cites a receipt that does not exist
```

**Run it before you write a single sentence of status.** Joshua, 2026-09-18: *"your cron should
remind you to pull live status - keep close tabs on what work has been done, what is left, it
should not come from memory - it needs to be up to date."*

**The defect this fixes is subtler than forgetting to check.** The conductor's status reports were
assembled from **prose it had written itself** — `PLAN.md` sections, its own commit messages, its
own summaries of pane callbacks. That is memory with extra steps, and it degrades silently: a
verdict recorded in a paragraph cannot be checked against the artifact it claims, so a stale or
invented state reads exactly like a current one.

`docs/demos/STATUS.tsv` is therefore the **machine-readable state of record** — one row per
candidate with rung, score, verdict, author and receipt path. The script renders it, **verifies
every cited receipt exists on disk**, and derives everything else live: bead counts, artifact
bytes, uncommitted deliveries, recent commits, worker panes.

**It is a gate, and it discriminates in both directions** (measured 2026-09-18): a planted row
citing a nonexistent receipt flags **exactly 1 of 16** and exits **3**; the unmodified state
reports **15 candidates, every receipt present**, exit **0**. A detector that fired on every row
would not have discriminated — that was the first version, and it was wrong.

**When a verdict lands, update `STATUS.tsv` in the same turn as the commit that produced it.** A
verdict that exists only in a commit message is invisible to the next tick, which is how the lane
ended up reporting state from memory in the first place.

```
DEMO <HH:MMZ> backlog N · active <demo-id or none> · beads live L · closed C
```

Census line still required, and **every number in it comes from the script's output, not from
recall**. Backlog authority: `docs/demos/PLAN.md` for reasoning, `docs/demos/STATUS.tsv` for state.
WIP LIMIT IS ONE DEMO, and rung 3 is currently blocked (`PLAN.md` §3e).

## 0b. WHY PANE 3 KEPT GOING IDLE — three causes, measured 2026-09-18

Joshua: *"pane 3 keeps going idle - are you not dispatching them, are they not calling back, what
is failing"*. Diagnosed from the artifacts, and **two of the three are conductor defects**.

**Cause 1 — I wrote a wait condition and gave no way to check it.** Duel-2 Unit 3 said *"score the
other pane's ranking"*, a cross-dependency. Timeline:

```
20:56  pane 2 hunt lands      <- pane 3's Unit-3 inputs existed from here
21:03  pane 2 reveal lands    <- pane 2 COMPLETE, all four units
21:16  pane 3 hunt lands      <- 13 min later, still on Unit 2
       pane 3 callback: "NEXT Unit 3 cross-score WHEN PEER FILES LAND"
```

**The files had landed twenty minutes earlier.** Pane 3 held a unit waiting on a condition already
satisfied, because it cannot observe another pane's progress and I never gave it a check.
**Whoever finishes first hits the wait**: pane 2 never blocked only because it was second.
**RULE: every dependency ships with `ls <full path>` plus a non-blocking fallback** — present ⇒
proceed, absent ⇒ BLOCKED callback naming the path, then the dry-queue default. **Never write
"when X lands".** And a pane's `NEXT` field must name the unit it is *starting*, never the thing it
is waiting for.

**Cause 2 — I under-dispatched it.** Packet count at diagnosis: **12 to pane 2, 9 to pane 3.** 25%
fewer. Not deliberate; it accumulated because pane 2's faster callbacks created more dispatch
moments, and §3.0 dispatches on callback. **A fast pane pulls dispatch attention away from a slow
one, and the conductor mistakes the resulting idleness for the slow pane's fault.**

**Cause 3 — pane 3 is throttled and I sized its units as if it were not.** It disclosed two
throttled search batches; pane 2 completed four units in the seven minutes pane 3 took for one.
That is **capacity, not quality** — pane 3's throttle disclosure and its marking of unverified
citations made its output more trustworthy per char, not less (`PLAN.md` §3g). **RULE: a throttled
pane gets smaller units and explicit permission to split** — a partial unit with a receipt beats a
complete unit that never lands.

**Cause 4, and it is the one I would have missed** — a queue-file append is **staging, not
delivery.** Unit 5 was appended to pane 3's queue file at `853f2b6`, after pane 3 had already read
that file. It may never have re-read it. The append rule (§3) avoids interrupting a working pane,
but **the append must still be pushed at the pane's next callback**, or it sits unread forever.
Append to stage; push to deliver.

**What was NOT the cause:** pane 3 not calling back. It fired leg-1 callbacks on every unit it
completed, and its receipts are all committed. The pane's reporting was sound throughout.

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

**COMMIT A QUEUE-FILE APPEND IN THE SAME TURN.** The mechanism above — append to the pane's queue
file instead of pushing into its prompt — has a hazard measured within minutes of its first use.
An uncommitted append sits in a shared worktree where **any** pane's next commit can absorb it.
Measured 2026-09-18: the conductor appended units 4–5 to `pane2-demo1-build.md`, and pane 3's
`d14387e` swept that file plus two of pane 2's source files into a commit about a steelman audit.
Content intact, attribution wrong. So: append, then commit that one file immediately, before the
turn ends.

**`git author` CANNOT ATTRIBUTE A COMMIT TO A PANE HERE.** All three panes commit as the same
identity — `git log -1 --format=%an` returns `Josh <joshua@zeststream.ai>` for every one of them.
Measured 2026-09-18: the conductor read `d14387e`'s message ("COD steelman") and attributed it to
pane 2, when pane 3 authored it while *auditing* pane 2's steelman. **Attribution comes from the
commit-message convention and the pane's own callback — never from `%an`, and never from guessing
at the subject line.** Pane 3's self-report was the only reliable signal, and it arrived because
the pane volunteered it.

**NEVER VERIFY A COMMIT'S CONTENTS FROM A TRUNCATED `--stat`.** Pane 3's stated cause for the
miscommit was reading a tail-cut `--stat` and missing the extra files. The conductor makes the same
error in the same family constantly — `| head`, `| tail`, and a grep tuned to the expected line all
hide what they cut. Before committing in a shared tree, read the **full** `git diff --cached
--stat`, and count the files rather than eyeballing them.

**RULING ON A MISCOMMIT: DO NOT REWRITE SHARED HISTORY.** `d14387e` swept three sibling files.
The content is correct and complete, the tree is clean, and nothing was lost — only the commit
message misdescribes what it carries. Amending or reverting shared `main` to repair attribution is
strictly worse than a note: it rewrites history other panes have already built on, to fix
bookkeeping. The correct response is what pane 3 did — self-report, refuse to amend, escalate the
fix direction — plus a conductor note recording what actually landed where.

## 4. WHAT ARE *YOU* DOING

If all three panes are genuinely working, you are not done — hold your own
claimed bead and work it. Do not manufacture a packet to look busy, and do not
sit watching timers.

## 5. APPEND CORRECTIONS, DO NOT INSERT (finding: pane 3, audit `7964ac2`)

An in-place correction renumbers lines, so every external line-number
pointer into that file silently aims at the wrong content afterward —
with no error anywhere. Measured instance: `WIZARD_IDEAS_CC.md`
corrections shifted CC lines ~8–17 downward, orphaning five cited ranges
in the cross-scores (e.g. CC:166–168 meant a determinism bullet at
scoring time and means a section header now — demonstrated by
`git show ad99a27:<file> | sed -n '166,168p'` vs current bytes).
Remedy, in order: append a dated correction block and leave the original
lines in place; or cite by stable anchor (section heading, sha, quoted
phrase) rather than line number. A correction that breaks pointers is a
second defect wearing a fix.
