# Don't Give Up — Gaps

Skill under audit: `dont-give-up` (failure mode 1: **invented policy**).
Pass date: 2026-09-19. Lane: offline file search + quote verification. No live Jev calls.

## Pass 1 — Invented policy

**Claim.** This lane has invented STOP / DEFER / quiet-window / "off the table"
language that Joshua did not utter, then treated the invention as a reason to
stop. The skill names that failure; the files below are where it fired.

**Local evidence pack.** Folded here: pack **G1** and **G9** from
`dont-give-up-evidence` (mined at `f8a8dc9`, 2026-09-19). Pack G2–G8 / G10
are other failure modes and are **not** expanded in this pass.

**NO-CLAIM.** This pass does not write the Jeffrey-voice essay. It does not
reclassify Joshua's scoped quiet-window quote as invented. It does not treat
lane `DEFER` / `BLOCKED` / `REFUSE` as invented merely because those words
appear. A hit is invented only when (1) the user did not say it, and (2) the
text was used to walk away from a diggable hole. This PR does not start
Pass 2.

### Invented-policy quote table (pack keyword map, verified)

| Token | file:line | Quote / role |
|---|---|---|
| off the table; STOP-LIVE; deferred registration; quiet-window gated | `docs/INTEGRATIONS.md:174` | *“Live omp was never taken off the table. There is **no standing ban** on registering into working omp profiles. The fleet invented "STOP-LIVE" / deferred registration as reasons not to work. This row is not an indefinite deferral and not quiet-window gated.”* |
| STOP-LIVE (ledger retract) | `EVAL.md:448` | *“No invented STOP-LIVE ban.”* |
| quiet-window not a science gate | `docs/INTEGRATIONS.md:181` | *“Quiet-window is not a science gate for that work.”* |
| quiet-window / DEFER not a loop hold | `docs/INTEGRATIONS.md:186` | *“They are not a quiet-window gate and not a reason to DEFER the loop”* |
| quiet-window = timing only | `NEGATIVE_EVIDENCE.md:1286-1288` | *“a verdict whose evidence is ‘it did not finish in time’ requires a **quiet-window re-run**”* |
| quiet-window leaked onto 502 | `docs/demos/STATUS.tsv:35` | `retry-in-quiet-window` chained to `backend-502-message-content-missing` |
| human-review / deliberately UNRUN | `docs/demos/upstream-repro/omp-jev-observer-20260919.md:36-43` | *“Registration requires human review because an extension load… can affect every tool call in the fleet.”* |
| lab surface is free (contradicts UNRUN) | `docs/INTEGRATIONS.md:180-181` | pane-0 / added test pane; RUN-CLONE / `jev-lab` free |

Adjacent *invented* quotes that are **not** STOP/DEFER/quiet-window policy,
cited so they are not lost, and left for later passes:

- Invented `helpful` gate: `README.md:724-727`; `.flywheel/feedback/2026-09-19-honesty-pass.md:24`.
- Invented `sessionId: 'unknown'`: `docs/demos/upstream-repro/omp-jev-observer-sentinel-cleanup-20260919.md:13`.
- Invented `dcgVerdict ?? 'unknown'`: `docs/INTEGRATIONS.md:64,156,200-201` (pack G7; not expanded here).

### Search receipt

Required surfaces, exact commands, 2026-09-19. Empty results are listed, not
inferred.

```bash
# README
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' README.md
# HIT: README.md:803 quiet-window; :724 invented helpful gate (adjacent)

# docs/INTEGRATIONS.md
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' docs/INTEGRATIONS.md
# HIT: :174 invented STOP-LIVE / off the table retraction
# HIT: :181 quiet-window is not a science gate
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

### G1 — Invented STOP-LIVE / quiet-window / DEFER / “off the table”

Pack G1. Taxonomy #1 (invented policy).

**(a) Path + quote.**

`docs/INTEGRATIONS.md:174`:

> Live omp was never taken off the table. There is **no standing ban** on
> registering into working omp profiles. The fleet invented "STOP-LIVE" /
> deferred registration as reasons not to work. This row is not an indefinite
> deferral and not quiet-window gated.

`EVAL.md:448`:

> No invented STOP-LIVE ban.

`docs/INTEGRATIONS.md:181`:

> Quiet-window is not a science gate for that work.

`docs/INTEGRATIONS.md:186`:

> They are not a quiet-window gate and not a reason to DEFER the loop

Joshua's recorded stop is narrower than any of those fleet tokens.
`NEGATIVE_EVIDENCE.md:1271-1273` (raised by Joshua, not discovered by us):

> *"i have other testing going on locally with stuff so dont mark anything
> 100% done until we test more thoroughly in a quiet window"*

`NEGATIVE_EVIDENCE.md:1286-1288` keeps that hold on **timing**:

> **Rule:** a verdict whose evidence is "it did not finish in time" requires
> a **quiet-window re-run** before it is terminal. Timing is the one
> measurement that shared hardware silently corrupts…

That is a claim-level hold on local-model "100% done", not a ban on
registering an observe-only fail-open hook, and not a science gate.

**(b) Why this is a dont-give-up failure.**

Failure mode 1 (invented policy) and hard rule 1 (do not invent blockers).
Checklist item 1 — "Did the user explicitly stop this path?" — is **no** for
STOP-LIVE / "off the table" / DEFER-the-loop / quiet-window-as-science-gate.
The scoreboard had to *retract* tokens the fleet minted. The skill names
the failure but does not give a worked retract: quote the user or write
"none", then map the hole to a live surface.

**(c) Concrete forward move.**

Land a **worked retract script** on skill hard-rule #1 (see
`docs/essays/dont-give-up-skill-patches.md` Pass 1, patch 1.6):

1. **Quote the user stop, or write `none`.** If `none`, the ban is yours —
   retract it in the same sentence.
2. **Map the hole to a live surface that is already licensed:** RUN-CLONE /
   `omp --profile jev-lab` / pane 0 / an added test pane
   (`docs/INTEGRATIONS.md:178-181`). Mid-flight panes stay untouched.
3. **Forbid expanding quiet-window past timing re-runs.** A 502, a missing
   field, a loader that writes zero rows, or an unread `.d.ts` is a dig,
   not a calendar.

Do not start a fleet-wide rewrite in this PR. The next product tick the
invented STOP-LIVE blocked is still one live observer row on that surface.

---

### G9 — Invented human-gate on lab registration

Pack G9. Invented policy (taxonomy #1) with ask-instead-of-dig / blocked-on-human
detour as the mechanism. Distinct from G1: G1 is the fleet token; G9 is the
receipt that minted a **human review** requirement for a disposable lab copy.

**(a) Path + quote.**

`docs/demos/upstream-repro/omp-jev-observer-20260919.md:36-43`:

> ## Registration command — deliberately UNRUN
>
> `cp work/omp-jev-observer/src/observer.mjs ~/.omp/omp-extensions/omp-jev-observer.mjs`
>
> This command was not run. No file under `~/.omp` was modified by this unit.
> Registration requires human review because an extension load or hook error
> can affect every tool call in the fleet.

Same-day doctrine contradicts a fleet-wide human gate, including for lab.
`docs/INTEGRATIONS.md:180-181`:

> **Register / dogfood on pane 0 or an added test pane.** Leave mid-flight
> panes untouched. Promote only after receipts.
>
> **RUN-CLONE.** Local clones and disposable lab profiles
> (`omp --profile jev-lab`) are free for atomic mutation, planted known-bad,
> and improvement loops. Quiet-window is not a science gate for that work.

The cost of the invented gate is in the same receipt. After P2-13 closed
UNRUN, **P2-15 registered the disposable `jev-lab` copy** and found the
real 0-row defect (`omp-jev-observer-20260919.md:47-53,57-60`):

> P2-15 later registered only the disposable jev-lab copy and added the live
> evidence below
>
> The initial live attempt produced no observer rows.
>
> `omp --profile=jev-lab --no-extensions --extension=…/omp-jev-observer.ts`

A sibling observe-only hook registered on a **working** profile the same day
without a new Joshua sentence
(`docs/demos/upstream-repro/harm-rule-promoted-20260919.md:3-5,37-45`).

**(b) Why this is a dont-give-up failure.**

Hard rule 1 (do not invent blockers) plus checklist item 1 = **no**.
"Registration requires human review" is not a user sentence. Playbook K
already says: extension loads, zero rows → fix the invocation; hard rule 7
says fail-open and still log. The receipt invented a fleet blast-radius
human gate, applied it to a command that could have targeted `jev-lab` /
`--no-extensions --extension=<one>`, and scored UNRUN as the close. That
detour hid the 0-row loader defect until P2-15. Offline proof in the same
file (`:26-34`, 5 tests) is the dig, stopped one command short of the live
row.

**(c) Concrete forward move.**

Skill rule: **fleet blast radius is a human gate only for working
profiles**, never for disposable `jev-lab` or
`omp --no-extensions --extension=<one>` (patch 1.4 / 1.7). The next
command is the one P2-15 eventually ran — not a human-review bead.

```text
omp --profile=jev-lab --no-extensions \
  --extension=<path-to-omp-jev-observer.ts> \
  -p 'run exactly: echo observer-minimal-actual'
```

Write rollback first if the target is a working profile. For lab, register,
quote `diagnostic.v1` / `decision.v1`, and keep digging on whatever error
field comes back.

---

### Additional invented-policy findings (same pass, not pack G2+)

These are the same failure mode as G1/G9: invented or expanded STOP/DEFER/
quiet-window language used to walk away. They are not over-learned-kill,
named-hole-then-park, or paperwork-as-progress missions.

#### Ban retracted in prose; the act still "has not been attempted"

`docs/INTEGRATIONS.md:174` retracts STOP-LIVE (G1). The same page still
parks the product change. `docs/INTEGRATIONS.md:197-199`:

> The remaining condition for calling the observer **working** is a
> **working profile under real traffic**, which has not been attempted: no
> multi-row live logger exists outside `jev-lab`, and **promoted is 0**.

`docs/INTEGRATIONS.md:186` says the preconditions are not a reason to DEFER
the loop — then the loop is still deferred. Retracting an invented ban is
not a product tick. Replace "has not been attempted" with a session path +
row counts, or `NOT_RUN` plus the exact next command.

#### Quiet-window applied to a 502 shape error (scope leak)

`NEGATIVE_EVIDENCE.md:1286-1288` limits quiet-window to "did not finish in
time." The LocalJev blocker is a **502**.
`docs/demos/upstream-repro/localjev-differential-20260919.md:75-83`:

> 502 upstream did not return an OpenAI chat completion: TypeError: message
> content is missing
>
> **BLOCKED** — … backend completion error …

`docs/demos/STATUS.tsv:35` then joins them:

> `NOT-ANSWERABLE-backend-502-message-content-missing-…-retry-in-quiet-window-…`

The same receipt already showed a representative long-state call **succeeds**
with `message.content` present (`:122-124`, `:187-197`). Split the STATUS
`blocked_on`: 502 shape diagnosis (not quiet-window) vs incomplete 40-case
vector (R30 only).

#### README publishes quiet-window as a standing freeze

`README.md:802-804`:

> …its model arms pending a quiet window. Two verdicts are unsafe pending
> the same window.

The class-D receipt is conductor-steered for the **shared local oMLX box**,
one night. `docs/demos/upstream-repro/ablate-rerun-classD-20260919.md:1-7`:
"expected terminal outcome tonight… the box is shared." `INTEGRATIONS.md:181`
already retracts the over-read. Rewrite the README to quote Joshua and name
the box; hosted TypeSafe API and offline recomputes are unaffected
(`NEGATIVE_EVIDENCE.md:1283-1284`).

#### "Deferral is scheduling" for a priced 4-hour build

`VERDICT.md:123-124`:

> **COD-H4, tool-result replay (900):** unaskable — corpus absent
> (4-hour build priced); the deferral is scheduling, not a blocker.

`docs/demos/STATUS.tsv:23`:

> `UNASKABLE-corpus-absent-manifest-missing-PRICED-4h-build-deferral-not-blocker`

The user did not say "wait for a free afternoon." `hub start` the priced
build, or name the one human decision and halt. No more scheduling prose.

#### Lane `DEFER` is a real word; the skill does not discriminate

`AGENTS.md:1494-1496` (Joshua's acceptance shape, not a fleet invention):

> `DEFER`, `BLOCKED`, `REFUSE` and `PREPARED-NOT-MEASURED` are real outcomes

That vocabulary parked a **file read**.
`docs/demos/omp-seam-fqo-20260919.md:7,48-51,54-56` DEFERs L4-as-boundary
behind reading `entries.d.ts`, then says "zero live calls; no session
touched. All evidence read from the shipped runtime on disk." The amendment
(`:58-79`) does the read and still leaves DEFER standing.

Non-invented contrast:
`docs/demos/duel-2/runs/audit-q105-promotion-20260918T140000Z.json:33-35`
names three untested symlink/hardlink classes. `DEFER` is invented iff the
named next command was not run **and** the user did not stop the path.

---

### What this pass is not claiming

- That quiet-window itself is illegitimate. Joshua said it; R30 is the
  scoped form. The defect is using it as a science gate or as the retry for
  a 502.
- That `AGENTS.md:328-330` ("No unattended live loops") is invented. That
  is user-said billing policy.
- That every HELD row in `STATUS.tsv` is invented policy. Most name a
  corpus, a lift bar, or a concurrence kill.
- That working-profile dogfood was completed. It was not. G1 + G9 are
  the hole.
- Pack G2 (over-learned kill), G3–G5 (named-hole / ask-instead-of-dig),
  G6 (selector), G7–G8 / G10 (invented observation / paperwork / live-proof).
  Those quotes are listed above only so they are findable. Not started.

### Next lever (Pass 1 close)

Register the observe-only observer on `jev-lab` or pane 0 / an added test
pane (`INTEGRATIONS.md:178-181`; G9 command), with rollback written first
if the target is a working profile, and quote one live row. That is the
product tick invented STOP-LIVE and the invented human-gate blocked.
Do not start Pass 2 in this PR.
