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

## UNIT 4 — the install script. Nobody owns this and the demo cannot ship without it.

`docs/demos/PLAN.md` defines shipped as four artifacts, and this is the one with no owner: **an
install script a stranger can run.** You own the tree, so you own it.

`demos/routing-backtest/install.sh` plus a short `demos/routing-backtest/README.md`:
- **Idempotent, and it says so** — safe to re-run, per the README-skeleton rule.
- Copy-pasteable with **no placeholders**. A stranger clones, runs one command, and gets a
  backtest over the shipped fixtures — not over `~/.omp`, which they do not have.
- **Default to the committed fixtures**, with the real omp session path as an opt-in flag. Your
  reader currently reads `~/.omp/profiles/...`; a stranger has no such directory, so an install
  that assumes it fails on first contact.
- No key required. This demo is read-only and offline; if the install mentions
  `TYPESAFE_API_KEY` at all, it is to say it is **not needed**.
- The README states the Boundary in one line: it prices a counterfactual on past turns and does
  **not** prove routing would work live.

## UNIT 5 — make pane 3's absence check effective

Pane 3's `demos/routing-backtest/fixtures/verify-fixtures.mjs` passes 8/8 but records an honest
NOTE: *"no price table in tree yet — absence check becomes effective once pane 2 ships one;
sentinel value asserted meanwhile."* That is the correct way to report a check that cannot yet
bite, and it creates a dependency on you.

Once your price table exists, re-run that verifier and confirm the `unknown-model` fixture's 18
model fields are genuinely **absent from your table** — turning a sentinel assertion into a real
absence check. **Do not edit pane 3's file**; if the assertion needs to change shape, message
pane 3 with what the table looks like and let them change it.

Report the verifier's exit code in your callback. If it still cannot bite, say so — a check that
passes because it is inert is the failure mode this lane keeps catching.

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
