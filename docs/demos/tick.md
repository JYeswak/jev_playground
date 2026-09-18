# JEV conductor tick — every 30 minutes. Automated. Not a human message.

You are the on-duty conductor (a pane or a process holding the conductor brief).
Joshua's standing order: the demo loop ships installable Jev demos repeatedly,
and without this tick it stops the moment the conductor goes quiet.

NO AUTO-DISPATCH EXISTS. You send project-aware dispatches by hand. This tick
only guarantees the loop is ASKED about every 30 minutes.

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
REPLY-VIA (all three, fire the moment the unit lands — DONE, BLOCKED, or
NEEDS-RULING; a BLOCKED callback is a SUCCESS, it routes around the unknown):
1. `br comments add <bead> --actor <YOU> -m "<OUTCOME> <receipt path> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to <CONDUCTOR>
   -s "[<bead>] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
   (find <CONDUCTOR> via `am agents list ~/Developer/jev`)
3. Receipt file in tree (runs/ or docs/), committed with own-files-only.
Carry: bead id · commit sha · NEXT (what you'd pick up unprompted) ·
NO-CLAIM (exact limit of what you proved).
```

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
