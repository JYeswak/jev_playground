# DISPATCH — pane 2 · BUILD demo-1 · this is construction, not review

**Stop auditing. Start building.** Joshua called the lane idle and he was right: 0 demos exist
while we produced 14 review artifacts. Your audits were all good and all of them are now spent —
the duel is closed, `docs/demos/PLAN.md` is committed, and demo-1 is named.

**Demo-1 is `jev-route-backtest`** (see `docs/demos/PLAN.md`, ACTIVE section). Read-only, inputs
already on disk, zero live calls to produce its evidence.

**You own `demos/routing-backtest/**` outright.** I am not editing inside it. Pane 3 is on the
hero image and will not touch it either.

---

## UNIT 1 — the transcript reader, with its denominator

Find and read our own omp session logs (JSONL). Emit, per turn: session id, turn index, the model
that actually served it, prompt/completion token counts if present, and whether the turn is
classifiable at all.

**The RED arm is the denominator, and it is the point of this unit:** a session file that yields
zero classifiable turns must **ERROR**, not report an empty-but-green run. An empty scan set is not
a pass. The receipt must state how many sessions were read, how many turns, and how many were
skipped **with the reason**.

Do not invent a schema. Read the actual files and report what fields exist — if the served model
is not recorded per turn, that is a finding that changes the demo, and it outranks finishing the
unit.

## UNIT 2 — the counterfactual, priced honestly

For each turn, decide whether a cheap model would have sufficed, and price both paths.

**Three hard constraints, each from a measured failure:**
- **A missing price-table entry is an ERROR, never a `$0` row.** This is MU-1's best RED arm and it
  is a fail-open surface if you get it wrong.
- The price table carries a dated **`as_of`** field and a re-derivation path. Pinned dollar figures
  rot silently.
- **The model that served each turn is a BASELINE, not an oracle.** Do not call agreement with it
  "accuracy". It is the incumbent policy's choice, not ground truth for what the turn needed.

Offline first. If you want a Jev judgment per turn, that is a **later** unit with a stated budget —
not this one.

## UNIT 3 — receipt + the honesty that R11 forces

Receipt at `demos/routing-backtest/runs/backtest-<ISO>.json`: inputs, session and turn
denominators, skipped-with-reason, per-model totals, actual spend, counterfactual spend, and a
`failures` array.

**Emit no `verdict` string.** R11 and `jev-demo-loop-a1q.3`: a one-word verdict over a
nondeterministic arm manufactures a finding. Report the numbers and their denominators; let the
reader conclude.

Then the `EVAL.md` row — **append only, do not restructure the file** — naming the verification
level and a Boundary stating exactly what the backtest does *not* prove (it does not prove routing
would work live; it prices a counterfactual on past turns).

---

## REPLY-VIA — three legs, per unit

1. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-demo-loop-a1q] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
3. Committed code + receipt, own files only, verification level in the subject.

Finish one, fire its callback, start the next YOURSELF. **If a unit turns out to be impossible —
e.g. the logs do not record the served model — that is a BLOCKED callback and it is a success.**

## NON-GOALS

No live Jev calls this wave. No `verdict` field. Do not touch `EVAL.md` beyond appending one row.
Do not review anything — there is nothing left in the duel worth another pass.
