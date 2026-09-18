# DISPATCH — pane 3 · two more contracts + the correction discipline you just found · 3 units

Your three contracts landed at **14,868 / 13,047 / 13,994 chars** — all above Jeff's 13,532-char
phase-epic scale and double his 7,363 median. That is the right depth.

**And your dry-queue audit (`7964ac2`) found a defect in MY editing practice**, which is now
doctrine: *"CC pointers stale from in-place correction edits; lesson: append corrections, don't
insert."* When I corrected `WIZARD_IDEAS_CC.md` in place, every line-number reference into it from
other documents went stale silently. Nobody gets an error; the pointers just quietly aim at the
wrong lines. Good catch — that is a whole class, not one file.

**Context that changed the depth target.** We measured Jeff's plan→bead transformation today:

```
his plan ............ 191,829 bytes / 1,367 lines
his bead text ..... 1,725,754 bytes / 195 beads  = 6.34x the plans
plan sentences verbatim inside beads .... 1,125/1,138 = 98.9%
mean beads each plan sentence appears in ... 5.35  (max 17)
```

He copies each requirement **word for word into every bead that touches it** — not partitioned,
redundantly embedded. That is why a bead can stand alone.

---

## UNIT 1 — `docs/demos/contracts/demo-1-route-backtest.md` (≥7,000 chars)

Source: `PLAN.md` §5.1. **Demo-1 has SHIPPED**, so this contract is written from measured reality
rather than intent — which makes it the most valuable one in the set, and the template for every
future demo contract.

Facts it must carry, all measured:
- Reader over real omp logs: 2 sessions, 1910 + 1183 rows, **30 turns**, 30 classifiable, 0 skipped,
  models `gpt-5.6-luna` and `muse-spark-1.3-contributor`.
- Counterfactual: actual **$7.230350988** vs counterfactual **$7.226928188** → savings
  **$0.0034228** = **0.047%**.
- **THE FINDING KILLS ITS OWN FOLLOW-ON.** Upstream measured **−60%** on *their* 237 turns
  (`jev-codex-router@8292b51`); on our turns it is 0.047%, so the live-router demo is **not
  queued**. State plainly that a demo which prevents a build is worth more than one that enables
  one — that is the demo's actual product.
- The turn-contract defect and its fix: three artifacts asserted 94 rows / **18** model-bearing rows
  / manifest "turns 1-6" / reader **1**. Cause found in code: the fixture carries explicit
  `turn_start`/`turn_end` markers and the reader ignored them. Fixed by defining "turn" **once** as
  a marker pair; the fixture now yields **6/6**. Record this as the worked example of *three
  artifacts asserting three counts is a missing shared definition, not three bugs.*
- Clean-clone verification: `git clone` → `install.sh` → **10 pass / 0 fail / exit 0**, then the
  documented fixture command → 1 session / 6 turns / 6 classifiable / 0 skipped, 5 cheap candidates.
- Three RED arms, all passing: empty classifiable set ⇒ `ERROR EMPTY_CLASSIFIABLE_SET`; model absent
  from the price table ⇒ ERROR, never a `$0` row; classifiable count below floor ⇒ WARN/ERROR, never
  a receipt that reads like a successful backtest.
- Hard constraints: **no `verdict` string** (R11); price table carries a dated `as_of`; the model
  that served a turn is a **baseline, not an oracle**.

## UNIT 2 — `docs/demos/contracts/demo-6-claim-check-notes.md` (≥7,000 chars)

Source: `PLAN.md` §5.6. Mean 767.5.

Facts it must carry:
- `jev-claims <notes.md> --evidence <dir>` — checks working-file claims against a cited evidence
  directory.
- **It is ADJACENT BUT DISTINCT from demo-3, by an arms-length ruling**, and only one gets built.
  Demo-3 is commit-triggered and parses commit-message triples; this is writer-facing over a notes
  file and an evidence directory. Different trigger, parser, evidence contract, failure boundary.
  The contract must state the build condition explicitly: **demo-3 first, and this only if demo-3
  proves the seam valuable.**
- **Its stage-1 defect is the same one demo-5 had:** "extracts verifiable working points" is not a
  mechanism — it hides a stage. Needs deterministic extraction → Choice → Noul, or RED arms guarding
  an unnamed stage.
- Carry demo-3's inherited rule: insufficient context ⇒ **withhold, never approve**.

## UNIT 3 — record the correction discipline you found

Append a section to `/Users/josh/Developer/jev/docs/demos/tick.md` (it is mine, but this finding is
yours and you should write it): **APPEND CORRECTIONS, DO NOT INSERT.** State the mechanism you
measured — an in-place correction renumbers lines, so every external line-number pointer into that
file silently aims at the wrong content, with no error anywhere. Name the concrete instance
(`WIZARD_IDEAS_CC.md` corrections vs the score files that cite its line numbers) and the remedy:
append a dated correction block and leave the original lines in place, or cite by **stable anchor**
(section heading, sha, quoted phrase) rather than line number.

This is the one exception to own-files-only this wave: I am handing you the file. Commit it
yourself so the finding carries your attribution, and do not touch anything else in `tick.md`.

---

## REPLY-VIA — FOUR legs, leg 1 first, per unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-DONE: <full path> <sha>. chars=<N>. NEXT <unit>. NO-CLAIM <limit>."`**
2. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-demo-loop-a1q] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed file, own files only, `[pending]` for specs and `[test]` for the tick.md finding if you
   demonstrate the stale-pointer mechanism with a command.

## NON-GOALS

Do not create beads. Do not edit `PLAN.md`, `BEAD-TEMPLATE.md`, or pane 2's contracts (`demo-5`,
`demo-7`, `demo-9`). Do not pad to hit the character count.
