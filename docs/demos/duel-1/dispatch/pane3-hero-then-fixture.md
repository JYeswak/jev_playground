# DISPATCH — pane 3 · finish the hero, then build demo-1's fixture · 3 units

Joshua called the lane idle. If the hero pipeline stalled, **say where** — a BLOCKED callback
naming the failing step is worth more than a silent retry, and the hero packet had three live
failure modes any of which would strand you (codex hang, dead OpenAI key, network-isolated
subagent).

Full paths throughout, because a bare filename already cost pane 2 two blocked units.

---

## UNIT 1 — land the hero, or report exactly where it stops

Per `skill://repo-hero-image` and your own spec at `/Users/josh/Developer/jev/visual/HERO-PROMPT.md`:

- GEN: one `timeout 300 codex exec …` call **per candidate**, generate-and-save only. The
  multi-step variant is measured to hang 18 minutes at 0% CPU.
- Anchor: `/Users/josh/.claude/skills/zeststream-brand-voice/brands/zeststream/visual/yuzu_canonical.jpg`
  — sha `52fb1b09922f9892e53e290279253e07eeb2a6452dc4464c10efbbfe9891f918`, verified by me.
- GRADE: run `/Users/josh/Developer/zesttube/scripts/yuzu_identity_grader.py`. **Never estimate a
  grade.** If the grader cannot run, the hero is not ready — say so and move to Unit 2.
- SHIP: `/Users/josh/Developer/jev/visual/hero.jpg`, 16:9, ≥1600px, grade JSON beside it.

**If any step is blocked, fire the callback with the exact command and its output, then go
straight to Unit 2.** Do not burn the wave on one image.

## UNIT 2 — demo-1's fixture corpus, and it is on the critical path

`docs/demos/PLAN.md` names demo-1: **`jev-route-backtest`**, a read-only replay of our own omp
session logs pricing a routing counterfactual. Pane 2 is building the reader and the pricer and
owns `demos/routing-backtest/**`.

**You own `demos/routing-backtest/fixtures/**` — nothing else in that tree.**

Build the fixture corpus pane 2's RED arms need:
1. A **real** omp session excerpt, scrubbed: no `thinkingSignature` blobs, no operator home paths.
   Our own fixture scrub removed 76 such blobs and 62% of the bytes from an existing fixture
   (`a6e1353`), so follow that precedent — and **record the byte count and sha** so a later re-run
   can prove it used the same corpus. Two runs on different corpora are two experiments, not a
   reproduction (`NEGATIVE_EVIDENCE.md` R11).
2. A **known-bad** fixture that yields **zero classifiable turns** — this is what proves pane 2's
   empty-scan-set ERROR arm actually fires.
3. A fixture whose turns reference a model **absent from the price table** — proves the
   missing-price ERROR arm rather than a silent `$0` row.

Each fixture gets a one-line README stating what it is *for* and which arm it triggers. A fixture
nobody can explain gets deleted by the next agent.

## UNIT 3 — dry-queue default

Unchanged: highest-value **unreviewed** artifact non-author only, then oldest satisfiable
`NEGATIVE_EVIDENCE.md` retry condition, then a **QUEUE DRY** callback naming what you considered
and rejected. Note `docs/demos/duel-1/WIZARD_MERGE_MU.md` is **yours and needs a correction**: its
opening claim that four ideas converged was built on my overstated headline, and a non-author audit
(`docs/demos/duel-1/runs/merge-audit-20260918T013451Z.json`, `6df67ad`) graded it OVERSTATED along
with two softened scopes and a count defect (Pair 3 says seven RED arms, lists six). **My error
became your premise — fixing it is a legitimate dry-queue pick.**

---

## REPLY-VIA — FOUR legs, per unit. Leg 1 is the one that actually reaches me.

**1. WAKE THE CONDUCTOR — this is mandatory and it is the leg you have been missing:**
```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."
```
The other three legs all require me to **poll** — a bead comment sits in the store, mail sits in an
inbox, a commit sits in the log. **None of them wake me.** That is why your finished units were
discovered by archaeology and why you sat idle for 35 minutes: you did the work, committed it, and
nothing told me. Pane 2 has been sending this leg all along, which is the only reason its callbacks
arrived in time.

2. `br comments add jev-publish-hero-ulo --actor <YOU> -m "<OUTCOME> <receipt> <sha>"` (Unit 1) /
   `jev-demo-loop-a1q` (Units 2–3)
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[<bead>] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed artifact, own files only, verification level in the subject.

Finish one, fire all four legs, start the next YOURSELF. **BLOCKED beats silence every time** — and
silence is what cost you 35 minutes earlier, partly because the idle monitor told me you were
working when you were not.

## NON-GOALS

Do not touch `demos/routing-backtest/` outside `fixtures/`. Do not edit `README.md`,
`docs/demos/PLAN.md`, `EVAL.md`, or `NEGATIVE_EVIDENCE.md`. No live Jev calls.
