# DISPATCH — pane 2 · STOP WRITING, START MEASURING · 3 units

Your queue-dry receipt (`e607a46`) was correct and it exposed something about the lane rather than
about you.

**Count what duel-2 has produced: roughly 350 KB of analysis and exactly ONE measurement.** The one
measurement is demo-1's 0.047%, and it arrived before duel-2 started. Everything since — ranks,
hunts, cross-scores, reveals, rung-2 assessments, baselines, falsification designs — is *documents
about what we would measure.* Every one of them was the right document. Collectively they are
drifting toward a document factory, which is the failure the gauntlet was built to prevent in demos
and can equally commit itself.

**Your own §3k falsifier is the exit.** You designed MU-H1's kill at rung-2 cost and split
cleanly into a label-free half and a labelled half. **The label-free half needs no human labels,
no Jev calls, no money, and roughly an hour.** Run it.

---

## UNIT 1 — RUN the label-free half of MU-H1's falsification. Real numbers, not a design.

Per `docs/demos/duel-2/FALSIFY_MUH1_COD.md` (`0f619de`), the labelled half needs 200 human-labelled
markers — expensive, and it costs Joshua's time or degrades to agent labels. **The enumeration half
answers a prior question for free: is there a denominator at all?**

Do exactly this and nothing more:
- Pick **≥10 pinned real repositories**. The vendored clones under the workspace root are already
  on disk at fixed SHAs — use them and **record the SHA of each**, because a marker census over
  moving checkouts is unreproducible.
- Enumerate TODO/FIXME/HACK/XXX markers **deterministically** — grep or AST, never model discovery.
  That distinction is the one your own rung-2 pass insisted on for MU-H1.
- Report: **markers per repo, total, markers per KLOC, and the distribution** (does one repo carry
  most of them?). State the exact command.

**The pre-registered thresholds are yours, from `0f619de`** — actionable rate <5%, Wilson-95 upper
<10%, ambiguity >20%. **This unit cannot evaluate them** because actionability needs labels. What it
*can* establish is whether the denominator supports the study at all:
- **Few markers in real repos** ⇒ MU-H1's audience is thin regardless of actionability, and it
  dies for an hour's work with nobody labelling anything.
- **Many markers** ⇒ the labelled half is worth Joshua's time, and you can say so with a number
  attached instead of a request.

**Do not estimate actionability from the marker text.** That would be the labelled half done badly
by the person with the strongest interest in the answer. Report the census; stop.

Receipt: `docs/demos/duel-2/runs/muh1-marker-census-<ISO>.json` — repos with SHAs, per-repo counts,
total, per-KLOC, distribution, the command, and a `failures` array. Commit at `[test]` **only if
you actually ran it**; `[pending]` is for designs and this is not one.

## UNIT 2 — design the falsifier for COD-H2, which you MAY NOT do

**COD-H2 pre-action abstention is the leader** (905 non-author, both rungs cleared) and §3k blocks
rung 3 until it has a falsification design. **You authored it, so you cannot design its falsifier**
— an author designing their own candidate's kill condition designs a weak one, which is the same
conflict that produced your 820-vs-550 split on demo-9.

So instead: **design falsifiers for the three pane-3-authored candidates you are a non-author of
and which have cleared rung 2** — `demo-2 admission screen` (700), `demo-5 fact ledger` (755), and
`demo-9 review signal` (550, CLEARED-conditional).

Each needs, at rung-2 cost: the single cheapest observation that would sink it, the command that
produces it, the number that constitutes failure, and **whether a label-free half exists.** demo-9's
is nearly written already — pane 3 cleared it conditionally on *beating* the `ubs` baseline rather
than producing a subset of it, and the measured baseline exists (1 critical / 6 warnings / 27 info
across our four first-party TS files, with an `eval()` positive control proving the scanner fires).

Output `docs/demos/duel-2/FALSIFY_pane3_candidates_COD.md`, ≥7,000 chars.

## UNIT 3 — the non-author audit you selected yourself

`docs/demos/duel-1/WIZARD_SCORES_MU_ON_CC.md` — pane-3-owned, never audited by a non-author, and
you identified it correctly. It is the file that scored my CC ideas, including the CC-1 mechanism
defect that turned out to be real. Audit its arithmetic and its reasoning.

Output `docs/demos/duel-1/runs/audit-scores-mu-on-cc-<ISO>.json`.

---

## REPLY-VIA — FOUR legs, leg 1 first, per unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-DONE: <full path> <sha>. chars=<N>. numbers=<the measured values>. NEXT <unit>. NO-CLAIM <limit>."`** — Unit 1 must carry **actual counts** in the callback, not a description of having counted.
2. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[duel-2] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed receipt, own files only, verification level in the subject.

## NON-GOALS

No Jev calls, no money, no labels in Unit 1. Do not design COD-H1…H5 falsifiers — you authored all
five and pane 3 owns that. Do not edit `PLAN.md`, `STATUS.tsv`, `BEAD-TEMPLATE.md`,
`contracts/*.md`, or pane 3's files. **If Unit 1 turns out to be impossible — clones absent, no
markers, ambiguous language boundaries — that is a BLOCKED callback with the command and its
output, and it is a success.**
