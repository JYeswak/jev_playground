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

**AUTHORIZATION — you ARE allowed to edit this file, and only these lines.** Every dispatch packet
this session ended with a NON-GOALS list telling you not to edit conductor-owned files, which
trained exactly the right caution and then collided with this protocol. Pane 3 hit that collision
and asked rather than assuming, which was correct. **Resolving it: editing a `CLAIM:` line in this
file is explicitly authorized for any pane, and it is the ONE exception to own-files-only.** Touch
nothing else here — not the unit bodies, not the rules, not another pane's claim. A `QUEUE-MARK-
REQUEST` back to pane 1 still works and costs a round trip; editing the line yourself does not.

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
- **SCARCE ELIGIBILITY OUTRANKS POSITION — and this rule exists because I broke it.** I appended a
  unit, called it *"the highest-value unit in this file"*, and put it at the **bottom**, while the
  protocol says *take the first unclaimed unit you are eligible for*. Position is the protocol;
  labels are not. Pane 3 correctly took an either-pane unit instead. **So: if a unit lists ONE
  eligible pane and you are that pane, it outranks every either-pane unit regardless of position,
  because an either-pane unit can be done by the other pane and a single-pane unit cannot.** Sole
  eligibility is the scarce resource in a two-pane lane; do not spend it on fungible work. When I
  add a unit that must run next, I will now **place it first** rather than labelling it.
- **A CONDITIONAL ELIGIBILITY LABEL MUST NAME ITS EXPIRY, or it outlives its reason — measured
  within the hour.** I marked Q7 *"pane 2 preferred"* because pane 3's sole eligibility on Q9 was
  scarce. Pane 3 then finished Q9 and reported **`NEXT dry-queue`** while Q7 and Q8 both sat
  unclaimed and available to it — because the label survived the condition that justified it.
  **The queue was not dry; my label made it look dry.** So: any narrowing I add ships the event
  that cancels it, and **if you believe the queue is dry, say which units you rejected and why**
  (the QUEUE DRY callback already requires this) — that report is what caught this defect.

---

## UNIT Q9 — RUN COD-H2's label-free falsification half. **HIGHEST VALUE UNIT IN THIS FILE.**
**ELIGIBLE: pane 3 only** (pane 2 authored COD-H2; pane 3 designed the falsifier). **CLAIM:** DONE CopperCarp `docs/demos/duel-2/runs/codh2-labelfree-20260918T040016Z.json` `db1e541` — **HEALTHY, surface only. COD-H2 took the rung-3 WIP slot.**

**Q1 and Q2 just made four candidates rung-3 eligible at once — COD-H2 905, COD-H4 900, COD-H5 895,
COD-H1 885 — and the WIP limit is ONE.** So the question stops being *which to build* and becomes
*which survives its own falsifier*, and §3k answers it: **run the label-free half before paying for
any build.**

Execute the label-free half of your own design in `docs/demos/duel-2/FALSIFY_COD-H2_MU.md`
(`f894425`) against COD-H2, the leader. **Do not build COD-H2. Do not label anything.** Run only
the part that needs no ground truth, and report the pre-registered number against the
pre-registered threshold.

**This is the exact shape that just killed MU-H1 in an hour** — a census, no labels, no Jev calls,
no money, and a verdict of `DENOMINATOR_TOO_THIN` that would otherwise have cost days. If COD-H2's
label-free half comes back thin, the lane's leader dies cheap and COD-H4 is next. **If it comes back
healthy, COD-H2 is the first candidate in this lane to earn a build.** Both outcomes are wins; the
only loss is not running it.

Report `HEALTHY` / `THIN` / `UNASKABLE` with the measured number, the threshold it was compared
against, and the command. Output `docs/demos/duel-2/runs/codh2-labelfree-<ISO>.json` plus a short
companion `.md` if the reasoning needs prose.

## UNIT Q1 — falsifier for COD-H2 pre-action abstention (THE LEADER)
**ELIGIBLE: pane 3 only** (pane 2 authored it). **CLAIM:** DONE CopperCarp `docs/demos/duel-2/FALSIFY_COD-H2_MU.md` `f894425` — 9,095 chars. **This unblocked rung 3.**

COD-H2 leads the whole backlog: **905 non-author, both rungs cleared.** §3k blocks rung 3 until it
has a falsification design, and **this single unit is what stands between the gauntlet and its
first thin proof.**

Deliver: the cheapest observation that would sink it, the exact command, the number that constitutes
failure, and whether a **label-free half** exists. Model it on
`docs/demos/duel-2/FALSIFY_MUH1_COD.md` (`0f619de`) — pre-registered thresholds, a confidence
interval, and explicit held/unaskable paths.

Output `docs/demos/duel-2/FALSIFY_COD-H2_MU.md`, ≥5,000 chars.

## UNIT Q2 — falsifiers for COD-H1, COD-H4, COD-H5
**ELIGIBLE: pane 3 only** (pane 2 authored them). **CLAIM:** DONE CopperCarp `docs/demos/duel-2/FALSIFY_COD-H145_MU.md` `8a8ec06` — 8,779 chars. All four COD candidates now falsifier-designed.

Same shape as Q1, three candidates, all rung-2 cleared: COD-H1 (885), COD-H4 (900, flagged *corpus
does not exist yet*), COD-H5 (895). COD-H4's missing corpus is itself a falsifier candidate — if the
corpus cannot be built cheaply, that is a rung-3 cost worth knowing now.

Output `docs/demos/duel-2/FALSIFY_COD-H145_MU.md`, ≥6,000 chars.

## UNIT Q3 — resolve COD-H3's open structural question
**ELIGIBLE: pane 3 only.** **CLAIM:** DONE CopperCarp `docs/demos/duel-2/RUNG2_COD-H3_resolved_MU.md` `51c2bb1` — 5,763 chars. **RULED_OUT on structure, two retry tracks.**

COD-H3 price-drift auditor is the **only** hunt candidate HELD at rung 2, on a structural question
left open in `docs/demos/duel-2/RUNG2_COD_HUNT_MU.md` (`e23251d`). Resolve it: CLEARED, or
RULED_OUT on structure with a retry condition, or **UNASKABLE**.

Output `docs/demos/duel-2/RUNG2_COD-H3_resolved_MU.md`, ≥4,000 chars.

## UNIT Q4 — baseline design: MU-H2 vs docverity + fiberplane/drift
**ELIGIBLE: pane 2 only** (pane 3 authored MU-H2). **CLAIM:** DONE WindyJaguar docs/demos/duel-2/BASELINE_MU-H2_vs_incumbents_COD.md 75cfb9f

MU-H2 outbound redaction was RULED_OUT, then **un-killed by §3i** because neither `docverity
v0.5.0` nor `fiberplane/drift v0.10.1` uses a judgment model. Design the head-to-head, modelled on
your own `docs/demos/duel-2/BASELINE_claimcheck_vs_jev_COD.md` (`2025164`): what the incumbents
provably cannot do, one shared corpus where their coverage is a strict subset, per-class metrics,
**where the incumbents win**, and a quantified ship gate stated in advance.

Output `docs/demos/duel-2/BASELINE_MU-H2_vs_incumbents_COD.md`, ≥6,000 chars.

## UNIT Q5 — demo-6's own incumbent search, on the NOTES surface
**ELIGIBLE: pane 2 only** (pane 3 authored demo-6). **CLAIM:** DONE WindyJaguar docs/demos/duel-2/HELD_demo6_incumbent_COD.md 11d0064

demo-6 claim-check-notes is HELD at 330. I had chained it to demo-3's death; that chaining was
**invalid** — demo-3 died on the commit-msg surface and demo-6 operates on a notes file checked
against an evidence directory. It must be judged on **its own** incumbent search, open-brief:
**does anything maintained check a notes/document file against a cited evidence directory?**

Carry the demo-3 lesson: my recovery condition named `commitlint`, was satisfied, and a tool I
never named (`claim-check v0.6.0`) owned the niche anyway. **Search the problem, not a tool list.**

Output `docs/demos/duel-2/HELD_demo6_incumbent_COD.md`, ≥5,000 chars.

## UNIT Q6 — MU-H3's voiced-pain search, or an honest UNASKABLE
**ELIGIBLE: pane 2 only** (pane 3 authored MU-H3). **CLAIM:** WindyJaguar 2026-09-18T04:05:02Z

MU-H3 runtime redaction is HELD at 650: real pain, but the voiced evidence is open and adjacent
OpenAI filters exist. Find **one cited complaint** from a named practitioner. **If an honest search
finds none, return UNASKABLE — not a kill.** Absence of a public complaint is weak evidence and
§3c forbids converting it into a rejection.

Output `docs/demos/duel-2/HELD_MUH3_voice_COD.md`, ≥4,000 chars.

## UNIT Q7 — falsifier for demo-7 signals starter
**ELIGIBLE: either pane** (I authored demo-7, so both of you are non-authors). **CLAIM:** DONE CopperCarp `docs/demos/duel-2/FALSIFY_demo7_MU.md` `8757b07` — **label-free half EXECUTED: 32.5 = 29.0 knowledge + 3.5 method. demo-7 repriced.**

demo-7 is HELD at 560 with its hold **resolved** — a named user exists (Oscar Beijbom, Nyckel, on
GPT confidence being badly calibrated or inversely related to correctness) and the score correctly
did not move. What it lacks is a falsifier.

Its thesis is the lane's central measurement: verdict-only **62.6%** versus five signals plus a
fitted head **95.1%**, a **32.5-point** delta. What is the cheapest observation that would show the
delta does not transfer to a user's own data? A label-free half probably exists.

Output `docs/demos/duel-2/FALSIFY_demo7_<YOURS>.md`, ≥4,000 chars.


## UNIT Q10 — the $0 weight-dominance check pane 3 designed and did not run
**ELIGIBLE: either pane.** *Pane 2 slightly preferred as non-designer of the test — this preference expires the moment pane 2 claims any other unit.* **CLAIM:** WindyJaguar 2026-09-18T04:11:50Z

`FALSIFY_demo7_MU.md` (`8757b07`) names a second falsifier and leaves it unrun, and it costs
**nothing**: committed full-fit weights show free-hosting **+9.27** and generic-sender **+12.24**
(`report.md:107` in the vendored `jev-phishing-bench@1d56e8c`). **If one weight dominates, the "five
signals" story is one signal plus decoration**, and demo-7's remaining 3.5-point method gain is
narrower still.

Read the committed weights. Report whether the fit is genuinely multi-signal or effectively
single-signal, with the numbers. Verdict: `MULTI` / `DOMINATED` / `UNASKABLE`. If `DOMINATED`, that
is **HELD for scope-narrowing, not a kill** — pane 3 already ruled on that, follow it.

Output `docs/demos/duel-2/runs/demo7-weights-<ISO>.json`.

## UNIT Q11 — **census every headline number this lane quotes but has never opened the control for**
**ELIGIBLE: either pane.** **CLAIM:** unclaimed

**This is the generalisation of the session's most expensive lesson and it is the highest-value unit
in the file.** R16 records that the lane repeated *"62.6% → 95.1%, a 32.5-point delta"* for an
entire session — in a contract, in `PLAN.md` §3m, and in my commit messages — while the source's own
no-AI control sat committed one file away at **91.6%**, making 89% of the quoted delta dataset
knowledge rather than method.

**The question this unit answers: how many more of those are there?** `docs/demos/USAGE-MAP.md` is
full of headline numbers lifted from vendored upstream repos. For each one that any live candidate
still leans on, determine: (a) does the source ship a control, baseline, or ablation arm; (b) has
anyone here opened it; (c) does the quoted number survive contact with that arm.

Prioritise numbers that a **surviving** candidate depends on — a repriced number under a RULED_OUT
candidate changes nothing. Report per-number, and say explicitly where the control does not exist
(that is a finding, not a gap in your work).

Output `docs/demos/duel-2/runs/quoted-number-census-<ISO>.json` plus a companion `.md`.

## UNIT Q12 — unblock COD-H2's build: sharpen the ambiguous classifier below 0.10
**ELIGIBLE: pane 3 only** (pane 2 authored COD-H2; pane 3 owns the classifier). **CLAIM:** CopperCarp 2026-09-18T05:10:00Z

**COD-H2 holds the lane's only rung-3 slot and its build is blocked on your own pre-condition.**
`ambiguous_share` measured **0.3765** against a **0.10** bar — 3.8× over — and by your own caveat the
cause is classing all `eval` as ambiguous when this fleet's evals are *predominantly read-side
compute*. `eval` is the largest tool in the corpus at **165,596 calls**.

Split `eval` (and any other blanket-ambiguous class) into read-side versus mutating, re-run the
label-free pass on the same 111 journals, and report the new `ambiguous_share` with its Wilson
interval. **Also report the destructive-subset share explicitly** — your caveat puts the
gate-relevant figure near **1,000 events (6.9%)** rather than 5,421 (37.3%), and the build must
target that subset.

**Pre-register the sharpened patterns before running**, in the same file, so this is a refinement
and not a re-cut. You already refused to re-cut once; hold that line.

Output `docs/demos/duel-2/runs/codh2-labelfree-sharpened-<ISO>.json`.

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
