# DISPATCH — pane 3 · rung 2 on COD-H1…H5 · you are the ONLY eligible grader · 3 units

**Your supersession filing settled a question I could not.** You argued that COD-H1 supersedes your
own demo-4 and **withdrew demo-4's standalone slot** — with a retry condition rather than as a
gesture. Pane 2, author of COD-H1, had simultaneously argued the opposite (demo-4 survives).
Opposite verdicts, both against their authors' interest.

**Adjudicated in your favour on the asymmetry** (`PLAN.md` §3j): defending a rival is cheap;
withdrawing your own candidate is the most expensive thing an author can do. COD-H1 takes the
backlog slot, demo-4 is **retained as a downstream integration** — not ruled out — and your
contract file stands as the integration spec. **demo-4 was the highest-scoring original at 820 with
both rungs cleared**; you gave up a passing candidate on the argument. That is the first time that
has happened here.

Your rung-1 scores on pane 2's hunt also flipped its ranking: its self-graded #1 (COD-H1, 940) is
your #5 at **885**, and **COD-H2 leads at 905**. Every gap negative — the corroborating direction.
And you caught pane 2 applying asymmetric standards to demo-9 versus demo-4, which is the
authorship bias the recusal rule exists for.

---

## UNIT 1 — rung 2 (JEV SHAPE) on COD-H1…COD-H5. This is the gauntlet's only open blocker.

All five cleared rung 1 with your non-author scores (885–905), above every original. **None has a
rung-2 assessment, and pane 2 cannot give one — it authored all five. You are the only eligible
grader in the session.**

Source: `docs/demos/duel-2/DEMAND_HUNT_COD.md` (`c33cd3c`, 22,872 chars). Your own rung-1 pass:
`docs/demos/duel-2/HUNT_SCORES_MU_ON_COD.md` (`ead8119`). Worked examples of the shape I want:
`docs/demos/duel-2/RUNG2_JEV_SHAPE_COD.md` (`36a142b`) and `docs/demos/duel-2/RUNG2_MUH1_COD.md`
(`beea578`) — note the second one **tested** the author's chat-model claim and found it *partly*
recoverable rather than accepting it.

For each of the five, four questions:

1. **What does the Noul judge, and what is the Choice choosing among?** Name the question text. If
   no Choice is needed, say so — MU-H1's assessment concluded exactly that, and it is a valid answer.
2. **Why is a chat model measurably worse?** Name the property it lacks: parseable type, calibrated
   probability, tunable threshold, cheap repetition at volume, refusal to invent an off-list option.
   **Test the claim rather than accept it** — a fixed rubric can often recover comparability, and
   the honest finding is usually "recovers syntax, not calibration".
3. **Is any stage secretly generation, summarization, or extraction?** This is the rung **demo-1
   died on** after passing the expensive rung nobody ran — it makes zero Jev calls and decides
   routing with a hand-written token heuristic. Locating things is extraction: if a model does the
   locating rather than grep/AST, the mechanism needs the demo-5 repair.
4. **Verdict per candidate: rung 2 CLEARED / HELD / RULED_OUT (structure only).**

**Prioritise COD-H2** (905, the leader) and **COD-H4** (900, flagged "corpus doesn't exist yet" in
your own rung-1 pass — that flag is a rung-3 cost, so check whether it is also a rung-2 problem).

Output `docs/demos/duel-2/RUNG2_COD_HUNT_MU.md`, ≥7,000 chars. **Split it if your rate demands —
verdicts first, prose second. A partial unit with a receipt beats a complete one that never lands.**

## UNIT 2 — non-author rung 2 on demo-9, which has never had one

demo-9 review-signal is **RECUSED**, not cleared: its proposer scored it 820 while you scored it
550, and a 270-point authorship-conflicted split cannot stand as a rung-1 pass. It has **no rung-2
assessment at all**.

You are the non-author. Same four questions. Its specific risk is stated in `PLAN.md` §5.9: **it
fails if its findings are a subset of what `ubs` already reports**, and there is a measured `ubs`
baseline on our four first-party TS files — 1 critical / 6 warnings / 27 info, every finding
classified non-defect, with an `eval()` positive control proving the scanner fires.

Per §3i, note that `ubs` **does not use a judgment model**, so it is a **baseline to beat, not an
owner**. The question is whether demo-9's findings are a strict superset.

Output `docs/demos/duel-2/RUNG2_demo9_MU.md`, ≥4,000 chars.

## UNIT 3 — dry-queue default

Highest-value unreviewed artifact non-author only; then oldest satisfiable `NEGATIVE_EVIDENCE.md`
retry condition; then a **QUEUE DRY** callback naming what you considered.

---

## REPLY-VIA — FOUR legs, leg 1 first, per unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-DONE: <full path> <sha>. chars=<N>. verdicts=<...>. NEXT <unit>. NO-CLAIM <limit>."`**
2. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[duel-2] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed file, own files only, verification level in the subject.

**Every path above is full — `ls` it and proceed. Never wait for a file to appear**; absent ⇒
BLOCKED callback naming the path, then the dry-queue default. **Your `NEXT` names the unit you are
starting, never what you are waiting for.**

## NON-GOALS

Do not score your own MU-H1…H3. Do not edit `PLAN.md`, `STATUS.tsv`, `BEAD-TEMPLATE.md`,
`contracts/*.md`, or pane 2's files. **No taste kills** — structural only at rungs 1–2, every
RULED_OUT ships a retry condition, missing evidence yields **UNASKABLE or HELD**. And per §3i, an
incumbent that does not use a judgment model is a **baseline, not an owner** — do not kill a
candidate for overlapping a deterministic tool.
