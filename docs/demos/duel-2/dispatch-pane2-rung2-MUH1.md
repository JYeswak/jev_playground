# DISPATCH — pane 2 · rung 2 on MU-H1 · you are the non-author · 3 units

Your supersession defence (`668a783`, 13,943 chars) is the strongest single result of duel-2, and
the reason is structural: **you authored COD-H1 and argued that demo-4 survives it.** You had every
incentive to claim your own candidate subsumes a rival and you argued the opposite, with explicit
non-subsumption cases and a composition seam. That is the one configuration where self-interest
points at the truth.

Held for adjudication until pane 3 files the mirror (it must argue COD-H1 supersedes its own
demo-4). I am not ruling before both sides land — §3e, and because I have made the
"are-these-the-same-thing" error twice today.

**MU-H1 TODO-judge has now CLEARED rung 1 at your 820** (author self-graded 900, gap 80 in the
corroborating direction). It **ties demo-4's 820** and is the highest-scoring candidate with a
non-author score. `STATUS.tsv` is updated; `lane-status.sh` reports 17 candidates, all receipts
present.

**Also note a rule I had to fix because you exposed it by satisfying it.** Rung 1 demanded *two*
non-author graders — unsatisfiable with two worker panes, and **nothing marked CLEARED had ever met
it.** Now one non-author grader plus three mandatory disclosures: the author's score beside it, the
gap, and who graded. `PLAN.md` §3h.

---

## UNIT 1 — rung 2 (JEV SHAPE) on MU-H1 TODO-judge

You are the non-author. MU-H1 is `docs/demos/duel-2/DEMAND_HUNT_MU.md` (`6c101d5`); your own rung-1
assessment is `docs/demos/duel-2/HUNT_SCORES_COD_ON_MU.md` (`98a74d8`).

**Rung 2 is the rung demo-1 died on after passing the expensive rung nobody checked.** Apply the
same four questions you used on demo-4/5/2 in `RUNG2_JEV_SHAPE_COD.md`:

1. **What exactly does the Noul judge, and what is the Choice choosing among?** MU-H1's claim is
   that it judges *whether a TODO marker is still true*. Name the question text a Noul would
   receive and the candidate set a Choice would select from.
2. **Why is a chat model measurably worse?** Its author's sentence is the strongest rung-2
   statement in either hunt — *"the value is calibrated batch judgment with a receipt over hundreds
   of markers, not one clever answer; prompting per-TODO has no threshold, no comparability, no
   audit trail."* **Test it rather than accept it.** Does per-marker prompting genuinely lack
   comparability, or could a fixed rubric recover it?
3. **Is any stage secretly generation, summarization, or extraction?** MU-H1 must locate markers
   before judging them. **Locating is extraction.** Is that stage deterministic (grep/AST) or is a
   model being asked to find things? If a model extracts, that is the demo-5 defect and the
   mechanism needs the same repair: deterministic extraction → Choice over candidates → Noul
   verdict.
4. **Verdict: rung 2 CLEARED / HELD / RULED_OUT (structure only).**

Output `docs/demos/duel-2/RUNG2_MUH1_COD.md`, ≥7,000 chars.

## UNIT 2 — BASELINE AND OBLITERATE · Joshua's correction, and it un-kills two candidates

> Joshua, 2026-09-18: *"the thing is these incumbents dont use jev - lets baseline and obliterate"*

**This inverts rung 1's incumbent test, and it means I over-killed.** I ruled demo-3 RULED_OUT
because `claim-check v0.6.0` occupies the commit-msg slot, and MU-H2 RULED_OUT on `docverity
v0.5.0` + `fiberplane/drift v0.10.1`. **None of those tools use a judgment model.** They parse,
regex, and match formats. So they are not owners of the niche — **they are the control arm we have
been handed for free.**

A maintained incumbent that does the narrow deterministic version of a task is the **best possible
baseline**: installable, pinned, and already trusted. "Here is the maintained tool, here is ours,
here is the measured delta on the same corpus" is a far stronger demo than any greenfield build,
and it is exactly the *"genuine deep story & impact"* the gauntlet exists to find.

**Design the head-to-head for `claim-check v0.6.0` vs a Jev claim-checker.** Not a build — a
design, cheap, at rung-2 cost:

1. **What can it provably not do?** Read its documented rule set. It verifies **numeric test-count
   claims** against pytest/Vitest/Jest output. Enumerate claim classes outside that: non-count
   numerics, percentages, claims citing arbitrary artifacts rather than test runners, claims whose
   evidence is prose, claims that are *true but stale*.
2. **The shared corpus.** One fixture set both tools run on, where the incumbent's supported subset
   is a **strict subset** of the corpus. Our own history is a real source: the claim audit found
   **19 EXACT, 4 WRONG, 37 UNVERIFIABLE** across four documents, and two of the four WRONG were
   residual instances of an already-corrected error.
3. **The head-to-head number.** Precision and recall for each tool on the same corpus. **The demo
   ships only if the delta is large enough that a stranger switches** — a real-but-trivial delta is
   demo-1's 0.047% death restated.
4. **Where the incumbent WINS, and say so.** It is deterministic, free, offline, and needs no key.
   A Jev checker costs money and latency per claim. **If the honest answer is "use claim-check for
   test counts and ours for everything else", that is a composition seam, not a defeat** — and it
   is what your own demo-4 defence established for COD-H1.
5. **Name the failure mode that would sink it:** the out-of-scope claim classes are rare in
   practice, so we would obliterate the incumbent on a corpus nobody encounters. **That is a base
   rate question and it costs an hour** — specify the command.

Output `docs/demos/duel-2/BASELINE_claimcheck_vs_jev_COD.md`, ≥7,000 chars.

## UNIT 3 — the cheapest thing that would make MU-H1 wrong

A **falsification design**, not a kill attempt. If MU-H1 reached rung 3, what single cheapest
observation would sink it? Strongest candidate: **TODO markers in real repos are overwhelmingly
still true**, so a truth-judge finds almost nothing and its value is a rounding error — demo-1's
death restated, where 0.047% was real, reproducible and operationally worthless. A base-rate check
on a real corpus costs an hour and is exactly the rung-4 measurement that killed demo-1. **Run it
early rather than after building.**

Also consider: stale-marker judgments may be unverifiable without human labels, making the
calibration claim untestable; and the receipt may be the product while nobody reads receipts.

Name the cheapest one, the command that produces it, and the number that constitutes failure.
§3c's design is cost rising 10× per rung — this unit moves a rung-4 kill into rung-2 cost.

Output `docs/demos/duel-2/FALSIFY_MUH1_COD.md`, ≥4,000 chars.

## UNIT 4 — dry-queue default

Unchanged: highest-value unreviewed artifact non-author only; then oldest satisfiable
`NEGATIVE_EVIDENCE.md` retry condition; then a **QUEUE DRY** callback naming what you considered.

---

## REPLY-VIA — FOUR legs, leg 1 first, per unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-DONE: <full path> <sha>. chars=<N>. verdict=<...>. NEXT <unit>. NO-CLAIM <limit>."`**
2. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[duel-2] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed file, own files only, verification level in the subject.

**Every dependency in this packet carries its full path — run `ls` on it and proceed. Never wait
for a file to appear**; absent ⇒ BLOCKED callback naming the path, then the dry-queue default.

## NON-GOALS

Do not adjudicate the supersession — both sides file, I rule. Do not score your own COD-H1…H5.
Do not edit `PLAN.md`, `STATUS.tsv`, `BEAD-TEMPLATE.md`, `contracts/*.md`, or pane 3's files. **No
taste kills**; structural only at rungs 1–2, every RULED_OUT ships a retry condition.
