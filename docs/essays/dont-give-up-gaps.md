# Don't Give Up — Gaps

Skill under audit: `dont-give-up` (failure mode 1: **invented policy**).
Pass date: 2026-09-19. Lane: offline file search + quote verification. No live Jev calls.

## Pass 1 — Invented policy

**Claim.** This lane has invented STOP / DEFER / quiet-window / "off the table"
language that Joshua did not utter, then treated the invention as a reason to
stop. The skill names that failure; the files below are where it fired.

**NO-CLAIM.** This pass does not write the Jeffrey-voice essay. It does not
reclassify Joshua's scoped quiet-window quote as invented. It does not treat
lane `DEFER` / `BLOCKED` / `REFUSE` as invented merely because those words
appear. A hit is invented only when (1) the user did not say it, and (2) the
text was used to walk away from a diggable hole.

### Search receipt

Required surfaces, exact commands, 2026-09-19. Empty results are listed, not
inferred.

```bash
# README
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' README.md
# HIT: README.md:803 quiet-window

# docs/INTEGRATIONS.md
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' docs/INTEGRATIONS.md
# HIT: :174 invented STOP-LIVE / off the table retraction
# HIT: :186 "not a quiet-window gate and not a reason to DEFER"

# AGENTS.md
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' AGENTS.md
# HIT: :1495 DEFER as legitimate acceptance vocabulary (not an invented ban)

# VERDICT.md — first pattern: no hits
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' VERDICT.md
# EMPTY
# follow-up for the scheduling-deferral cousin:
rg -n 'deferral|scheduling, not a blocker' VERDICT.md
# HIT: :124

# docs/demos/STATUS.tsv
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' docs/demos/STATUS.tsv
# HIT: :35 retry-in-quiet-window (UP-R8)
# follow-up:
rg -n 'deferral' docs/demos/STATUS.tsv
# HIT: :23 COD-H4 PRICED-4h-build-deferral-not-blocker

# docs/demos/**
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' docs/demos --glob '*.{md,tsv,json}'
# HIT: STATUS.tsv:35
# HIT: docs/demos/upstream-repro/ablate-rerun-classD-20260919.md:1,31
# HIT: docs/demos/upstream-repro/omp-jev-observer-20260919.md:36-43

# receipts (no receipts/ directory exists; searched the receipt locations that do)
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' docs/demos/duel-2/runs
# EMPTY

rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' foundation
# EMPTY

rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' demos
# EMPTY (first-party demos/)

# supporting ledger (not in the required list; used only to quote Joshua vs the fleet)
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' EVAL.md NEGATIVE_EVIDENCE.md
# HIT: EVAL.md:448 "No invented STOP-LIVE ban"
# HIT: NEGATIVE_EVIDENCE.md:1271-1288 Joshua quiet-window quote + R30 rule
```

Empty on this pattern (required or receipt-adjacent): `VERDICT.md` (exact
STOP/quiet-window/off-the-table pattern), `docs/demos/USAGE-MAP.md`,
`docs/demos/ORACLE-MANIFEST.tsv`, `GATES.md`, `docs/demos/duel-2/runs/`,
`foundation/`, `demos/`. There is **no** `receipts/` directory in this tree.

---

### GAP 1 — Invented "STOP-LIVE" / "registration requires human review"

**(a) Path + quote.**

`docs/demos/upstream-repro/omp-jev-observer-20260919.md:36-43`:

> ## Registration command — deliberately UNRUN
>
> `cp work/omp-jev-observer/src/observer.mjs ~/.omp/omp-extensions/omp-jev-observer.mjs`
>
> This command was not run. No file under `~/.omp` was modified by this unit.
> Registration requires human review because an extension load or hook error
> can affect every tool call in the fleet.

The later scoreboard names the invention and retracts it.
`docs/INTEGRATIONS.md:174`:

> Live omp was never taken off the table. There is **no standing ban** on
> registering into working omp profiles. The fleet invented "STOP-LIVE" /
> deferred registration as reasons not to work. This row is not an indefinite
> deferral and not quiet-window gated.

`EVAL.md:448-449` (same retraction, ledger form):

> No invented STOP-LIVE ban. Live test surface remains pane 0 / added test
> panes.

Joshua's recorded stop on live work in this window is **not** that sentence.
`NEGATIVE_EVIDENCE.md:1271-1273` (raised by Joshua, not discovered by us):

> *"i have other testing going on locally with stuff so dont mark anything
> 100% done until we test more thoroughly in a quiet window"*

That is a claim-level hold on local-model "100% done", not a ban on
registering an observe-only fail-open hook.

The invented bar is also contradicted by a later unit that **did** register
on a working profile without a new Joshua sentence.
`docs/demos/upstream-repro/harm-rule-promoted-20260919.md:3-5,37-45`:
one `codex` working-profile registration, observe-only, first-contact rows
written, no rollback.

**(b) Why this is a dont-give-up failure.**

Failure mode 1 (invented policy) and hard rule 1 (do not invent blockers).
Checklist item 1 — "Did the user explicitly stop this path?" — is **no**.
The receipt invented a fleet-wide human-review gate, then scored "deliberately
UNRUN" as the unit's close. That is "narrate blockers as product strategy"
(`dont-give-up` What not to do). Playbook K and hard rule 7 already name the
dig: fail-open, return `undefined`, prove one live row. The offline proof in
the same file (`:26-34`, 5 tests, `undefined` on success/error/timeout) is
exactly that dig, stopped one command short of the live row.

**(c) Concrete forward move.**

Run the already-written registration on the surface the retraction itself
names, not on a mid-flight pane:

```text
# from docs/INTEGRATIONS.md:178-180
# Live test surface = pane 0, or an added test pane. Leave mid-flight panes untouched.
# Fail-open / observe-only already proven offline in omp-jev-observer-20260919.md:26-34.
```

Register the observer the same way `harm-rule-promoted-20260919.md` registered
the harm-rule: one profile, rollback commands written first, one driven
probe, quote the session rows. Do not wait for a human-review bead that
nobody filed.

---

### GAP 2 — Ban retracted in prose; the act still "has not been attempted"

**(a) Path + quote.**

`docs/INTEGRATIONS.md:174` retracts STOP-LIVE (quoted in GAP 1).
Immediately after, the same page still parks the product change.
`docs/INTEGRATIONS.md:197-199`:

> The remaining condition for calling the observer **working** is a
> **working profile under real traffic**, which has not been attempted: no
> multi-row live logger exists outside `jev-lab`, and **promoted is 0**.

`docs/INTEGRATIONS.md:186` tells the reader the preconditions "are not a
quiet-window gate and not a reason to DEFER the loop" — then the loop is
still deferred.

**(b) Why this is a dont-give-up failure.**

Hard rule 8 / failure mode 6: paperwork as progress. Retracting an invented
ban is not a product tick. The skill's done-enough line is "concrete artifact
that runs + live proof line, or one named human decision." This page named
neither a human decision nor a command that was run. "Has not been attempted"
after "there is no standing ban" is the give-up wearing a retraction.

**(c) Concrete forward move.**

Execute GAP 1's registration on pane 0 / an added test pane in the same
change that cites `INTEGRATIONS.md:174`. Replace "has not been attempted"
with a session path + row counts, or with `NOT_RUN` plus the exact next
command. A third paragraph that restates the retraction is not the move.

---

### GAP 3 — Quiet-window applied to a 502 shape error (scope leak)

**(a) Path + quote.**

Joshua's rule is scoped to **timing** on a shared box.
`NEGATIVE_EVIDENCE.md:1286-1288`:

> **Rule:** a verdict whose evidence is "it did not finish in time" requires
> a **quiet-window re-run** before it is terminal. Timing is the one
> measurement that shared hardware silently corrupts…

The LocalJev receipt's blocking evidence is not that sentence.
`docs/demos/upstream-repro/localjev-differential-20260919.md:75-83`:

> 502 upstream did not return an OpenAI chat completion: TypeError: message
> content is missing
>
> **BLOCKED** — not SUBSTITUTE or NOT-SUBSTITUTE. The failure is a
> LocalJev/oMLX backend completion error on the pinned differential
> workload, after the feasibility probe itself worked.

The status row then joins the 502 to quiet-window as if they were one
blocker. `docs/demos/STATUS.tsv:35`:

> `NOT-ANSWERABLE-backend-502-message-content-missing-no-complete-denominator-40case-never-ran-retry-in-quiet-window-see-NEGATIVE_EVIDENCE-retry-condition`

The same receipt already showed the representative long-state call
**succeeds** with `message.content` present
(`localjev-differential-20260919.md:122-124`, `:187-197`). So the 502 is a
workload/shape hole, not a "did not finish in time" verdict.

**(b) Why this is a dont-give-up failure.**

Invented policy by **expansion**: a user-said, narrow timing hold was
rewritten as the retry for a TypeError. Hard rule 2 (keep kills narrow)
and playbook K (fix the invocation; don't abandon the feature). Checklist
item 1 is yes for *timing-as-100%-done* and **no** for *stop diagnosing a
502*. Filing `retry-in-quiet-window` on a response-shape error is how a
scoped user sentence becomes a fleet ban.

**(c) Concrete forward move.**

Split the STATUS `blocked_on` into two named conditions:

1. **502 shape** — isolate one pinned request that reproduces
   `message content is missing` (the receipt already has a succeeding
   long-state body to diff against). Quiet-window is not this arm.
2. **Incomplete 40-case vector** — R30 quiet-window re-run, only for the
   timing/contention claim.

Do not leave a single hyphen-chain that lets the next pane treat a parser
error as a calendar hold.

---

### GAP 4 — README publishes quiet-window as a standing freeze

**(a) Path + quote.**

`README.md:802-804`:

> **Open questions, honestly.** Class-D (does the agent's answer change?) is
> unmeasured: the ablate-and-rerun harness is built and frozen, its model
> arms pending a quiet window. Two verdicts are unsafe pending the same
> window. Everything else above ran.

The class-D receipt is conductor-steered for the **shared local oMLX box**,
not a general science gate.
`docs/demos/upstream-repro/ablate-rerun-classD-20260919.md:1-7`:

> PREPARED-NOT-MEASURED (arms pending a quiet window)
>
> …Per conductor steering this is the expected terminal outcome tonight,
> not a deferral: the box is shared…

`docs/INTEGRATIONS.md:181` already retracts the over-read:

> Quiet-window is not a science gate for that work.

**(b) Why this is a dont-give-up failure.**

The one-night, one-box hold is a user/conductor sentence. The README drops
the scope ("tonight", "same oMLX server", "don't mark 100% done") and
publishes a standing "pending a quiet window" over class-D **and** "two
verdicts." A later pane that reads only the README will invent the science
gate `INTEGRATIONS.md:181` just retracted. That is how invented policy
reproduces: the scoped quote lives in `NEGATIVE_EVIDENCE.md`; the public
status line does not.

**(c) Concrete forward move.**

Rewrite `README.md:802-804` to quote Joshua's sentence and name the
affected box (local oMLX / LocalJev + class-D model arms). State the
negative: hosted TypeSafe API and every offline recompute are
**unaffected** (`NEGATIVE_EVIDENCE.md:1283-1284`). Point RUN-CLONE / jev-lab
/ hosted live work at `docs/INTEGRATIONS.md:181`, not at "the same window."

---

### GAP 5 — "Deferral is scheduling" for a priced 4-hour build

**(a) Path + quote.**

`VERDICT.md:123-124`:

> **COD-H4, tool-result replay (900):** unaskable — corpus absent
> (4-hour build priced); the deferral is scheduling, not a blocker.

`docs/demos/STATUS.tsv:23`:

> `UNASKABLE-corpus-absent-manifest-missing-PRICED-4h-build-deferral-not-blocker`

**(b) Why this is a dont-give-up failure.**

"Scheduling, not a blocker" is quiet-window's cousin: a calendar word used
to walk away from a hole whose cost is already priced. The user did not
say "wait for a free afternoon." `AGENTS.md:1498-1503` (Joshua, same day)
says selection and closure are ours; a computable next step is not an
escalation. A 4-hour local corpus build is either (i) start it under `hub`
(skill playbook F/H; R29 in `NEGATIVE_EVIDENCE.md` already names `hub
start` vs `&`), or (ii) the **one** named human decision if 4 hours of
shared-box time is the paid/irreversible class. Calling it "not a blocker"
while leaving it unstarted is invented DEFER.

**(c) Concrete forward move.**

Pick one, write it on the STATUS row, and do it:

- **Start:** `hub start` the priced 4-hour corpus build; receipt the PID and
  the completion marker. or
- **Halt:** one line — "human decision: authorize 4h corpus construction on
  this box?" — and stop. No more scheduling prose.

---

### GAP 6 — Lane `DEFER` is a real word; the skill does not discriminate

**(a) Path + quote.**

`AGENTS.md:1494-1496` (Joshua's acceptance shape, not a fleet invention):

> Never "make it pass". `DEFER`, `BLOCKED`, `REFUSE` and
> `PREPARED-NOT-MEASURED` are real outcomes and are preferred over a
> manufactured number.

That vocabulary was then used to park a **file read**.
`docs/demos/omp-seam-fqo-20260919.md:7,48-51,54-56`:

> allowed set: REFUSE L4-as-Jev-pruning, DEFER L4-as-boundary behind a named
> probe.
>
> **DEFER:** L4-as-boundary behind one concrete probe — read
> `SessionMessageEntry` linkage in `entries.d.ts` …
>
> Boundary: zero live calls; no session touched. All evidence read from the
> shipped runtime on disk…

The same receipt's amendment (`:58-79`) then does the read, withdraws Reason
1, and **still** leaves DEFER standing — now on Reason 2 (Jev does not
write `summary` prose). The first DEFER was a walk-away from a `.d.ts` that
was already on disk.

A **non-invented** DEFER, for contrast:
`docs/demos/duel-2/runs/audit-q105-promotion-20260918T140000Z.json:33-35`
names three untested symlink/hardlink classes and refuses to promote on a
green live run. That is checklist item 2 (narrow cost-benefit) plus a named
next arm, not an invented ban.

**(b) Why this is a dont-give-up failure.**

The skill's failure mode 1 lists `DEFER` next to STOP-LIVE as if the token
itself were the bug. In this lane the token is legal. The bug is DEFER
**without** (user stop | narrow kill with cheaper substitute | one named
human decision | the named probe executed). `omp-seam-fqo` failed that test
on the first close; Q105 did not. An agent following the skill literally
will either (i) treat every lane DEFER as invented and re-litigate honest
holds, or (ii) treat `AGENTS.md:1495` as a license to park.

**(c) Concrete forward move.**

Patch the skill (see `docs/essays/dont-give-up-skill-patches.md` Pass 1):
`DEFER` is invented iff the named next command was not run **and** the user
did not stop the path. For `omp-seam-fqo`, convert the first DEFER to the
amendment's actual state: REFUSE L4-as-Jev-pruning on Reason 2; keep the
alignment probe only if someone still needs a summarizer-gated L4, and then
run it on a throwaway keyed session rather than filing it as a follow-up
bead.

---

### What this pass is not claiming

- That quiet-window itself is illegitimate. Joshua said it; R30 is the
  scoped form. The defect is using it as a science gate or as the retry for
  a 502.
- That `AGENTS.md:328-330` ("No unattended live loops") is invented. That
  is user-said billing policy.
- That every HELD row in `STATUS.tsv` is invented policy. Most name a
  corpus, a lift bar, or a concurrence kill.
- That working-profile dogfood was completed. It was not. GAP 1–2 are
  the hole.

### Next lever (Pass 1 close)

Register the observe-only observer on pane 0 or an added test pane
(INTEGRATIONS.md:178-180), with rollback written first, and quote one live
row. That is the product tick the invented STOP-LIVE blocked. Pass 2
(over-learned kill) is a different mission.
