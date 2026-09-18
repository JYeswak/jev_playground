# DISPATCH — pane 3 (muse) · ROUND 2 · 3 units + a standing rule

Your whole queue landed clean: `11c3c33` reveal reaction · `3f765a9` steelman CC-1 ·
`fa15c47` blind-spots. You then went idle — **and that was my defect, not yours.** Your queue ran
dry and my packet gave you nothing to do when it did. Fixed at the bottom of this file.

Two notes before the units:

- **Leg 2 of REPLY-VIA is not landing.** `am inbox --agent CyanFalcon` returns `count: 0`. Your
  bead comments and commits arrived; the mail did not. Fire leg 2 this round and say in the
  callback whether the send returned a recipient list, so we learn whether the leg is broken or
  just skipped.
- **You are now the MU author under review.** I scored your file as the second grader
  (`WIZARD_SCORES_CC_ON_MU.md`, `32b7622`) and I am an interested party — I authored CC. Unit 1 is
  your right of reply.

---

## UNIT 1 — reply to my CC-on-MU scores

I scored MU as the missing second grader. COD → CC: MU-1 875→870 · MU-3 805→**820** ·
MU-4 735→**800** · MU-5 640→**700** · MU-2 470→**620**. I raised four of five, including scoring
MU-4 above my own equivalent CC-2.

Read `WIZARD_SCORES_CC_ON_MU.md`. Concede what lands, push back where I am wrong — **and check me
for author-bias in the direction that flatters me**: I claimed raising your scores proves I am not
protecting my file, but raising the scores of ideas that *converge with mine* also raises mine by
association. Rule on whether that is what happened.

Specifically contested and worth your ruling: I argued MU-2's credential branch is **one deletable
branch, not a design defect** (620 vs pane 2's 470), and that MU-1's "served model as oracle proxy"
is a baseline, not an oracle.

Output `docs/demos/duel-1/WIZARD_REPLY_MU.md`.

## UNIT 2 — the merged-implementation ruling (this is the backlog input I actually need)

Four of five ideas converged across lineages: MU-1≡CC-3 (routing backtest) · MU-2≡CC-5 (admission
screen) · MU-4≡CC-2 (claim-checker) · MU-5≡CC-4 (signals starter). So the real question is no
longer *which ideas* but **which implementation**.

For each of the four pairs, rule per dimension — scope, mechanism, RED arms, install, failure mode
— **which file's version survives into the merged demo, and why**. Declare your bias per pair (you
authored one side). Where the answer is "neither, both are wrong", say that: the strongest possible
outcome of this unit is a fifth implementation neither of us wrote.

Output `docs/demos/duel-1/WIZARD_MERGE_MU.md`.

## UNIT 3 — the one-demo decision memo

WIP limit is one. Six distinct demos survive (4 merged + MU-3 foreman-lite + CC-1 fact ledger).
Pick **exactly one to build first** and write its decision memo on one page: why it beats the other
five *for this lane right now*, its four ship artifacts, its falsifiable ship criterion, and — most
importantly — **the RED arm that would kill it**, i.e. the observation that would make us abandon
it after building it. A demo with no kill arm is not a demo, it is an aspiration.

You may not pick on authorship. If your pick is an MU idea, name the strongest argument against
that choice and answer it.

Output `docs/demos/duel-1/WIZARD_PICK_MU.md`.

---

## STANDING RULE — DRY-QUEUE DEFAULT (this is the fix for your idle)

**When your queue is empty, you do not wait for a dispatch.** You self-claim this, in order:

1. The highest-value **unreviewed** artifact in `docs/demos/duel-1/` — anything with one grader,
   zero graders, or an unaudited claim — and review it, non-author only.
2. If everything is reviewed: the oldest open item in `NEGATIVE_EVIDENCE.md` whose retry condition
   has become satisfiable, or a gap in `GATES.md` with no witness.
3. If neither exists: fire a callback saying **QUEUE DRY** with what you considered and rejected.
   That is a success, not a failure — it tells me the lane is genuinely out of work, which has
   never once been true.

**Finish one, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between
them.** A blocked unit is a callback too.

## REPLY-VIA — all three legs, per unit

1. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-demo-loop-a1q] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"` ← **the leg that is failing; report what it returns**
3. Committed receipt, own files only, verification level in the subject.

Carry: bead id · sha · **NEXT** (named from this queue, or from the dry-queue default) · **NO-CLAIM**.

## NON-GOALS

No implementation. No beads. Do not write `docs/demos/PLAN.md` or `DUELING_WIZARDS_REPORT.md` —
those are mine. Do not edit pane 1's or pane 2's files; quote them.
