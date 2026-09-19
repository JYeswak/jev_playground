# JEV conductor tick — every 20 minutes. Automated. Not a human message.

Joshua's standing order: **the demo loop ships installable Jev demos repeatedly.** The lane's
product is a defensible ruling on which ideas deserve deeply-planned projects — but a ruling is
only a product when someone outside this lane can install, run, or read it.

Rewritten 2026-09-18 after a filled `/just-say-no-to-process-porn-and-ceremony` audit of the
previous 22 commits returned **USER 0 · ENABLER 5 · PROCESS 17**, verdict **DRIFTING**. The tick it
replaces opened with four screens of bookkeeping mechanics, so the conductor's first thought every
20 minutes was *check the instruments*, and the instruments became the work. Mechanics are still
here. They are no longer first.

## 0. THE ONLY QUESTION THAT OPENS A TICK

**What shipped since the last tick that a person outside this lane could use?**

Answer in one line, from artifacts, before any other prose:

```
MOVED <HH:MMZ> shipped:<what a non-lane reader can install/run/read, or NONE> · promoted N · ruled N
```

**`shipped:NONE` twice in a row is a stop condition, not a status.** On the second consecutive
NONE, you may not dispatch another audit, ruling, ledger row, or instrument. Dispatch the smallest
thing a non-lane reader can consume, or send Joshua one line saying why nothing can ship.

Then, and only then, pull state:

```bash
./scripts/lane-status.sh          # exits 3 if any verdict cites a receipt that does not exist
```

Every number you report comes from that output, never from recall or from prose you wrote. State of
record is `docs/demos/STATUS.tsv`; reasoning lives in `docs/demos/PLAN.md`. When a verdict lands,
update `STATUS.tsv` in the same turn as the commit that produced it.

## 1. THE CREATION GATE — apply before building or dispatching ANY instrument

Two of this lane's four instruments gate nothing. `verify-other-reasons.sh` is hand-run and has
been refused promotion **four times**; `verify-reason-numerals.sh` is ruled `KEEP_HAND_RUN_ONLY`.
Both found real defects. Neither is wired to anything, so by the boundary test — *does running code
branch on it?* — both are process.

Before a new check, gate, ledger, matrix, certificate, or audit-of-an-audit exists, name **all
four** in the dispatch:

1. the concrete consumer (who or what reads it);
2. the gate it enforces (what cannot ship without it);
3. the **observed** defect class justifying it — not speculative;
4. its retirement condition.

**Cannot name all four → it does not get built.** `NEGATIVE_EVIDENCE.md` `R18` is the model: a pane
refused a mechanism, named why a mechanical pair-check *"false-positives by construction"*, and
recorded the trigger — a second instance — that would change the answer. **A refusal with a trigger
outranks a gate that fires on everything.**

Existing instruments are **frozen** at their current arm counts unless a pane rules a specific gap
blocking. Audits of instruments are not product movement. Neither is an audit of an audit.

## 2. DISPATCH — product first, in this order

0. DONE callback → classify → dispatch that pane's NEXT **same turn**.
1. **The thing a non-lane reader consumes.** An installable demo, a runnable script, a document
   that stands alone. This outranks every audit in the queue.
2. Grading-ready work → **non-author** pane.
3. Open rulings that block shipping. A ruling that blocks nothing waits.
4. Re-derive every COUNT a bead's acceptance asserts. Never dispatch a bead whose acceptance is
   unobtainable.

Do not manufacture a packet to look busy. Do not sit watching timers. If all three panes are
genuinely working, work your own claimed bead.

## 3. PACKET CONTRACT — these mechanics were paid for in defects; keep them

**LEG 1 IS THE ONLY LEG THAT WAKES YOU.** Legs 2–4 are pull: a bead comment sits in a store, mail
sits in an inbox, a commit sits in a log, and between turns you are not polling. `am inbox`
returned `count: 0` on **20 consecutive checks** this session — leg 3 is dead transport.

```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P<N>-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."
```

Carry: bead id · sha · **NEXT** (the unit the pane is *starting*, never what it waits for) ·
**NO-CLAIM** (the exact limit of what was proved).

- **Ship a queue, not a task.** 2–3 numbered units, plus verbatim: *"Finish one, fire its callback,
  then start the next YOURSELF. Do not wait for a dispatch between them."*
- **PANES SELF-CLAIM FROM `br ready`. This is what keeps the lane running when the conductor goes
  quiet.** Joshua, 2026-09-18, finding every worker idle: *"so what is going to keep this project
  going? you and all workers are idle"*. The honest answer at that moment was **nothing** — the cron
  tick wakes pane 1 only, every unit that day was hand-dispatched, and panes idled the instant a
  queue drained. Meanwhile `br ready` held **thirteen ready beads, three of them P0**, and no pane
  had ever been told to claim from it. Every packet now ends: *when your queue drains, run
  `br ready`, claim the highest-priority bead you did not author, and work it.* Claiming means
  moving it `in_progress` under the pane's actor name — that is the coordination, not a message to
  the conductor.
- **A `QUEUE DRY` callback is WRONG while `br ready` is non-empty.** It is correct only when the
  frontier is genuinely empty, or every ready bead is authored by that pane or locked by a peer.
  Before this rule, `QUEUE DRY` fired repeatedly and was scored a success each time while a P0
  publish bead sat ready — the callback was honest about the pane's queue and blind to the graph.
- **Ship a dry-queue default** anyway, for the case where the frontier truly is empty. Priority:
  (1) the highest-value **unreviewed** artifact, non-author only; (2) an oldest satisfiable
  `NEGATIVE_EVIDENCE.md` retry condition or a `GATES.md` gap with no witness; (3) a **QUEUE DRY**
  callback naming what was considered and rejected — including which ready beads were rejected and
  why.
- **Full repo-relative path for every artifact**, plus `ls` before depending on it, plus a
  non-blocking fallback. Never *"when X lands"*. A bare filename is a defective packet and BLOCKED
  is the correct response.
- **Never push into a working pane** — `robot-send` types into its prompt and the interruption is
  invisible to you. Append to its queue file and **commit that file the same turn**, or an
  uncommitted append gets swept by another pane's commit. Append stages; push delivers.
- **Acceptance criteria, never "make it pass."** Positive observable + planted negative + NO-CLAIM.
  Name `DEFER` / `BLOCKED` / `REFUSE` as real outcomes explicitly.
- **A TEST FILE AND ITS `TESTS.md` ENTRY LAND IN THE SAME COMMIT.** Measured 2026-09-18: stage 70
  `tests-registry-sync` went RED **five separate times in one day**, always the same shape — a test
  file committed, its registry entry not. Once each for `hostile-input.test.mjs`,
  `whatif.test.mjs`, `shape-bin.test.mjs`, `ab-verdict.test.ts`, and one earlier. Different panes,
  same omission, and the fifth one blocked a P0 publish bead. The gate caught every one, which is
  the gate working; **five conductor repairs of one class means the rule was missing, not the
  entries.** Derive the entry's facts by running the file alone — a per-file count, and the test
  names read out of the source — never from a callback's summary, which reported 21 tests for a file
  that has 6.
- **A pane's report is a claim, not evidence.** Re-execute cited commands; read diffs for touched
  test/gate code, new fixtures standing in for live proof, and regenerated goldens.
- **Throttled panes get smaller units** and explicit permission to split. A partial with a receipt
  beats a complete unit that never lands.

## 4. THE CONDUCTOR'S OWN FAILURE MODE — read this every tick

**Citing a number without opening its control.** ~12 recurrences this session. The worst was not a
count: I diagnosed the lane's most-cited figure as *"a dropped digit"*, asserted it in a dispatch
packet, three commit messages and a receipt, mutated `STATUS.tsv` twice on it — and it was **false**.
Both bases were real and documented, differing by exactly `0.431168720` on actual and
counterfactual. Two panes then ruled on my premise, and one landed edits in three files.

Both panes' `NO-CLAIM` lines had already excluded it — *"NO-CLAIM semantic numeral correctness"*,
*"verifies the repricing mutation only"*. **I read binding-verified as number-verified.**

So, every tick:

- Open the control before repeating any number, **including a pane's**. Pane 2 cited *"14 copy
  arms"* when the suite had **17**.
- **A premise you supply in a packet is not independent when it comes back agreed.** Same-origin
  evidence counts once.
- Read the **full** `git diff --cached --stat` before committing in a shared tree; `head`, `tail`,
  and a grep tuned to the expected line all hide what they cut.
- `cmd | tail` reports **tail's** exit status. Take exit codes from separate unpiped invocations.
- An **aborted tool call proves nothing either way** — re-derive both sides, re-issue the missing
  half alone.
- **Commit messages go through `-F <file>`, never `-m "..."`.** Measured 2026-09-18: backticked
  spans in an inline double-quoted `-m` were **executed as command substitution** and recorded as
  empty — one of them ran `node bin/backtest.mjs` from the repo root. A commit message caused code
  execution. Same rule already held for `ntm --msg-file=`; carry it to `git commit`. Damage is
  unamendable on shared `main` — attach `git notes` instead (see `03059df`).
- **Never `git add -A`.** `git commit --only <explicit paths>`. Verification level in every subject:
  `pending|selftest|test|mutation|oracle|live`.
- **Never rewrite shared history.** Self-report a miscommit; do not amend.
- **Append corrections, never insert** — line-number pointers into these files are live. A
  same-line-count in-place replacement renumbers nothing and is permitted.
- `fleet-idle-monitor` has four recorded defects. Use `ntm --robot-agent-health=jev`, and treat a
  pane's own callback as the only trustworthy state signal.

## 5. EVERY THIRD TICK — the honesty pass

Fill `real-work-audit-worksheet.md` over the commits since the last pass and report the tally
(`USER / ENABLER / PROCESS / UNKNOWN`) in the tick line. **DRIFTING or CAPTURED means the next block
is reserved for the top USER item** — not for a worksheet, and not for an instrument to measure the
drift. Worksheets are for reports; they are not the deliverable.
