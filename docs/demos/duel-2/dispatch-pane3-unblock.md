# DISPATCH — pane 3 · YOUR INPUTS ALREADY EXIST · verify, never wait · 3 units

**You are blocked on nothing.** Your last callback said *"NEXT Unit 3 cross-score when peer files
land."* They landed **20 minutes before you wrote that**. That is my packet's defect, not yours —
I wrote a cross-dependency with no way for you to check it, so you waited on a condition that was
already satisfied.

**The files, with full paths and shas — verify them yourself right now:**

```bash
ls -l docs/demos/duel-2/DEMAND_RANK_COD.md   # e733de8, 18,880 chars — landed 20:53
ls -l docs/demos/duel-2/DEMAND_HUNT_COD.md   # c33cd3c, 22,872 chars — landed 20:56
```

**STANDING RULE FROM NOW ON — VERIFY, NEVER WAIT.** If a unit names a dependency, run `ls` on it.
Present ⇒ proceed immediately. Absent ⇒ fire a **BLOCKED** callback naming the missing path and
take the dry-queue default. **Never hold a unit waiting for a file to appear** — you cannot observe
another pane's progress, and "when X lands" is an instruction I should never have written.

**Also relevant: you are throttled and pane 2 is not.** You disclosed two throttled search batches,
and pane 2 completed four units in the seven minutes it took you to finish one. That is a capacity
difference, not a quality difference — your throttle disclosure and your marking of unverified
citations made your hunt *more* trustworthy per char, and I recorded that in `PLAN.md` §3g. So:
**if a unit is too large for your current rate, split it and fire a callback on the first half.**
A partial unit with a receipt beats a complete unit that never lands.

---

## UNIT 1 — cross-score pane 2's rank AND hunt (this is the gauntlet's blocker)

Score `DEMAND_RANK_COD.md` and `DEMAND_HUNT_COD.md` 0–1000 on **how well the demand reasoning
holds**, not whether you agree with the ordering.

**COD-H1…COD-H5 need your rung-1 scores specifically** — `PLAN.md` §3e blocks rung 3 until hunt
candidates carry **two non-author scores**, and you are the only non-author of pane 2's five. Its
self-graded ceiling is COD-H1 at **940**, above every original including your own demo-4 at 820.

Attack specifically:
- **Is each incumbent search real?** Carry the demo-3 lesson: my recovery condition named
  `commitlint` and was *satisfied*, while `claim-check v0.6.0` — a tool I never named — owned the
  niche and killed the demo anyway. **Search the problem, not a list of tools someone named.**
- **Is any candidate generation wearing a judgment costume?** That is rung 2's kill and demo-1 died
  on it after passing the expensive rung nobody checked.
- **Is the pain voiced or asserted?** A cited complaint beats a plausible persona.

**No taste kills.** Rungs 1–2 permit structural kills only; every RULED OUT ships a retry
condition; missing evidence yields **UNASKABLE or HELD**, never a rejection. And do not raise a
score because you found the evidence a hold asked for — pane 2 resolved demo-7's hold by finding a
named user and **left the score at 560**, which is now lane doctrine.

Output `docs/demos/duel-2/HUNT_SCORES_MU_ON_COD.md`, ≥7,000 chars. **Split it if your rate demands
— scores first, prose second.**

## UNIT 2 — the supersession argument you are required to lose

Appended to your queue file earlier (`853f2b6`) and you may never have re-read it, which is the
same delivery defect. Restating it here in full:

**Does COD-H1 snapshot-bound completion evidence (940) supersede your own demo-4 foreman-lite
(820, your MU-3)?** Pane 2 authored COD-H1; **you authored demo-4**; no non-author exists; and I
have made this exact "are these the same thing" error twice today, so I am not deciding it.

**Write the strongest case that COD-H1 SUPERSEDES demo-4** — the side against your own interest.
Pane 2 is simultaneously arguing demo-4 survives, against its interest.

Strongest supersession case: COD-H1 removes the `br`/bead-graph coupling that cost demo-4 points in
every ranking, needing only a transcript, a revision and machine receipts, and its snapshot binding
invalidates a claim when a later mutation contradicts it — a strictly more general form of "did
this work actually get done".

Case you must confront: bead-acceptance judgment may be a **different question** — "does this diff
satisfy this *stated* acceptance" vs "was this claim true at the revision it was made at". If that
holds, the tracker coupling is a **feature** and both survive.

**"demo-4 survives" from its own author settles it in your favour without my intervention.**
Conceding is equally a real result: it withdraws a candidate with a retry condition.

Output `docs/demos/duel-2/SUPERSESSION_MU_argues_COD-H1.md`, ≥4,000 chars.

## UNIT 3 — dry-queue default

Unchanged, and **use it rather than idling**: highest-value unreviewed artifact non-author only;
then oldest satisfiable `NEGATIVE_EVIDENCE.md` retry condition; then a **QUEUE DRY** callback
naming what you considered and rejected.

---

## REPLY-VIA — FOUR legs, leg 1 first, per unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-DONE: <full path> <sha>. chars=<N>. NEXT <unit>. NO-CLAIM <limit>."`**
2. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[duel-2] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed file, own files only, verification level in the subject.

**Your NEXT field must never contain a wait condition.** Write the unit you are starting, not the
thing you are waiting for.

## NON-GOALS

Do not score your own MU-H1…H3 — pane 2 owns that. Do not edit `PLAN.md`, `STATUS.tsv`,
`BEAD-TEMPLATE.md`, `contracts/*.md`, or pane 2's duel-2 files.
