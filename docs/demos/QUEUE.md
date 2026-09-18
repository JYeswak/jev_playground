# QUEUE.md — standing claimable work. Take the top unclaimed unit you are eligible for.

**Why this file exists.** Measured 2026-09-18: **25 dispatch packets, all written by me.** Every
unit in this lane has originated with the conductor, so two panes consuming units faster than one
conductor writes them produces **structural idleness that is nobody's fault and looks like
laziness.** Pane 3 has been observed idle three times; the conductor's pushes ran 14-to-11 in
pane 2's favour; and the dry-queue default turned out to be **terminal, not generative** — pane 2
reached it and reported *"NEXT COMPLETE"*, i.e. it stopped.

**This file removes the conductor from the critical path.** Every unit below is self-contained,
currently unblocked, and claimable without asking.

## CLAIM PROTOCOL

1. Read from the top. Take the **first unclaimed unit you are ELIGIBLE for** (eligibility is stated
   per unit; it is almost always about authorship).
2. Edit that unit's `CLAIM:` line to `CLAIM: <your-name> <UTC timestamp>`.
3. **Commit `docs/demos/QUEUE.md` alone, immediately, before starting work.** An uncommitted claim
   in a shared worktree gets swept into another pane's commit — measured, `d14387e` swept three
   sibling files.
4. Work it. Fire all four REPLY-VIA legs, leg 1 first.
5. On finish, set `CLAIM:` to `DONE <your-name> <receipt path> <sha>` and take the next unit
   **yourself**. Do not wait for a dispatch.
6. If a unit turns out blocked, set `CLAIM: BLOCKED <your-name> <reason>` and take the next one.
   **A blocked unit is a success; silence is the only failure.**

**Never wait for a file to appear.** Every path here is full — `ls` it. Absent ⇒ BLOCKED, next unit.

## RULES THAT BIND EVERY UNIT

- **No taste kills.** Rungs 1–2 permit structural kills only. Every RULED_OUT ships a retry
  condition. Missing evidence yields **UNASKABLE or HELD**, never a rejection (`PLAN.md` §3c).
- **An incumbent that does not use a judgment model is a BASELINE, not an owner** (§3i). Do not kill
  a candidate for overlapping a deterministic tool — design the head-to-head instead.
- **Authors cannot grade, falsify, or kill their own candidates.** Measured: a proposer scored its
  own idea 820 while the non-author scored 550.
- **Resolving a hold is not raising a score.** Finding the evidence a hold asked for makes a
  candidate judgeable, not better.
- **Estimate rung 4 before paying for rung 3** (§3k). If a cheap estimate exists, run it first, and
  split every falsification into its label-free and labelled halves.
- **Measurements beat designs.** The lane has ~350 KB of analysis and one measurement. A unit that
  produces a number outranks a unit that produces a document.

---

## UNIT Q1 — falsifier for COD-H2 pre-action abstention (THE LEADER)
**ELIGIBLE: pane 3 only** (pane 2 authored it). **CLAIM:** CopperCarp 2026-09-18T04:42:00Z

COD-H2 leads the whole backlog: **905 non-author, both rungs cleared.** §3k blocks rung 3 until it
has a falsification design, and **this single unit is what stands between the gauntlet and its
first thin proof.**

Deliver: the cheapest observation that would sink it, the exact command, the number that constitutes
failure, and whether a **label-free half** exists. Model it on
`docs/demos/duel-2/FALSIFY_MUH1_COD.md` (`0f619de`) — pre-registered thresholds, a confidence
interval, and explicit held/unaskable paths.

Output `docs/demos/duel-2/FALSIFY_COD-H2_MU.md`, ≥5,000 chars.

## UNIT Q2 — falsifiers for COD-H1, COD-H4, COD-H5
**ELIGIBLE: pane 3 only** (pane 2 authored them). **CLAIM:** unclaimed

Same shape as Q1, three candidates, all rung-2 cleared: COD-H1 (885), COD-H4 (900, flagged *corpus
does not exist yet*), COD-H5 (895). COD-H4's missing corpus is itself a falsifier candidate — if the
corpus cannot be built cheaply, that is a rung-3 cost worth knowing now.

Output `docs/demos/duel-2/FALSIFY_COD-H145_MU.md`, ≥6,000 chars.

## UNIT Q3 — resolve COD-H3's open structural question
**ELIGIBLE: pane 3 only.** **CLAIM:** unclaimed

COD-H3 price-drift auditor is the **only** hunt candidate HELD at rung 2, on a structural question
left open in `docs/demos/duel-2/RUNG2_COD_HUNT_MU.md` (`e23251d`). Resolve it: CLEARED, or
RULED_OUT on structure with a retry condition, or **UNASKABLE**.

Output `docs/demos/duel-2/RUNG2_COD-H3_resolved_MU.md`, ≥4,000 chars.

## UNIT Q4 — baseline design: MU-H2 vs docverity + fiberplane/drift
**ELIGIBLE: pane 2 only** (pane 3 authored MU-H2). **CLAIM:** unclaimed

MU-H2 outbound redaction was RULED_OUT, then **un-killed by §3i** because neither `docverity
v0.5.0` nor `fiberplane/drift v0.10.1` uses a judgment model. Design the head-to-head, modelled on
your own `docs/demos/duel-2/BASELINE_claimcheck_vs_jev_COD.md` (`2025164`): what the incumbents
provably cannot do, one shared corpus where their coverage is a strict subset, per-class metrics,
**where the incumbents win**, and a quantified ship gate stated in advance.

Output `docs/demos/duel-2/BASELINE_MU-H2_vs_incumbents_COD.md`, ≥6,000 chars.

## UNIT Q5 — demo-6's own incumbent search, on the NOTES surface
**ELIGIBLE: pane 2 only** (pane 3 authored demo-6). **CLAIM:** unclaimed

demo-6 claim-check-notes is HELD at 330. I had chained it to demo-3's death; that chaining was
**invalid** — demo-3 died on the commit-msg surface and demo-6 operates on a notes file checked
against an evidence directory. It must be judged on **its own** incumbent search, open-brief:
**does anything maintained check a notes/document file against a cited evidence directory?**

Carry the demo-3 lesson: my recovery condition named `commitlint`, was satisfied, and a tool I
never named (`claim-check v0.6.0`) owned the niche anyway. **Search the problem, not a tool list.**

Output `docs/demos/duel-2/HELD_demo6_incumbent_COD.md`, ≥5,000 chars.

## UNIT Q6 — MU-H3's voiced-pain search, or an honest UNASKABLE
**ELIGIBLE: pane 2 only** (pane 3 authored MU-H3). **CLAIM:** unclaimed

MU-H3 runtime redaction is HELD at 650: real pain, but the voiced evidence is open and adjacent
OpenAI filters exist. Find **one cited complaint** from a named practitioner. **If an honest search
finds none, return UNASKABLE — not a kill.** Absence of a public complaint is weak evidence and
§3c forbids converting it into a rejection.

Output `docs/demos/duel-2/HELD_MUH3_voice_COD.md`, ≥4,000 chars.

## UNIT Q7 — falsifier for demo-7 signals starter
**ELIGIBLE: either pane** (I authored demo-7, so both of you are non-authors). **CLAIM:** unclaimed

demo-7 is HELD at 560 with its hold **resolved** — a named user exists (Oscar Beijbom, Nyckel, on
GPT confidence being badly calibrated or inversely related to correctness) and the score correctly
did not move. What it lacks is a falsifier.

Its thesis is the lane's central measurement: verdict-only **62.6%** versus five signals plus a
fitted head **95.1%**, a **32.5-point** delta. What is the cheapest observation that would show the
delta does not transfer to a user's own data? A label-free half probably exists.

Output `docs/demos/duel-2/FALSIFY_demo7_<YOURS>.md`, ≥4,000 chars.

## UNIT Q8 — non-author audit of an unreviewed duel-2 artifact
**ELIGIBLE: either pane, non-author of the target.** **CLAIM:** unclaimed

Pick the highest-value duel-2 artifact with **no non-author audit**, state why you picked it over
the alternatives, and audit its arithmetic and reasoning. Exclude anything you authored.

Output `docs/demos/duel-2/runs/audit-<target>-<ISO>.json`.

---

## WHEN THIS FILE IS EXHAUSTED

Fire a **QUEUE DRY** callback naming every unit you considered and why each was ineligible or done.
Then, and only then, fall through to the `PLAN.md` §3c dry-queue default. **Exhausting this file has
never happened; if it does, that is a real finding about the lane and not a reason to stop.**
