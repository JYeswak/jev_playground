# Route rows labelled: 24 rows, one turn, both questions right — effective n=1 (2026-09-19)

## Labels

`work/omp-jev-route/labels-20260920.jsonl` (24 lines): every row heavyweight TRUE,
mechanical FALSE. The turn ("Redesign the auth session boundary so refresh tokens rotate
on every use", jev-lab session 2026-09-20T00-00-47) produced 24 assistant messages, 23
eval calls + 1 todo, touching 12+ files across blackfoot/ (routers, models, migration,
tests) — multi-step reasoning, unfamiliar repo, multi-file change. All 24 rows said
heavy (0.90–0.91) / not-mechanical (0.09–0.11): 24/24 HIT on both questions, zero FP/FN.

## The honesty paragraph

This is weaker than it looks. All 24 rows judge ONE prompt in ONE session — the per-row
tally measures scorer stability (range 0.01 on both questions over 4.5 minutes), not 24
independent accuracies. Effective n=1. Against the 8/9 hand-built result, real traffic
says: correct once, stable always. No row is UNLABELLABLE (evidence is the transcript's
tool/file counts, complete for this turn), but no second distinct turn exists to label —
the turn_start era wrote zero scored rows and the twin session wrote diagnostics only.

Hindsight control, as briefed: the label comes from transcript artifacts counted by
script (message roles, tool names, file paths), not from my memory of the turn — and
there is almost no memory to contaminate: I was the lab prompter, never a participant
in the redesign reasoning, and the work happened in blackfoot/, a repo I have never
opened. The remaining bias runs the other way: a turn that sprawled across 24 messages
is trivially heavyweight in hindsight, so this label was easy; a turn correctly judged
heavy at 00:00:48 before any tool ran is the actual evidence of foresight, and there is
exactly one of those here, repeated 23 times.

## NO-CLAIM

n≈24 rows but n=1 turn, one session, one labeller who prompted it. Precision/recall
"24/24" describes stability of a single correct judgment. The hand-built 8/9 remains
the accuracy claim; this does not extend it.
