# DISPATCH — pane 3 · duel-1 REVEAL, then a 2-unit queue (do not go idle)

Bead: `jev-demo-loop-a1q`. Your cross-scores landed (`ad99a27`) and they were good — you caught a
false claim in pane 1's receipt (`3` questions, not four) and pane 1 has conceded it in writing.

**This packet contains THREE units. Finish one, fire its callback, then start the next YOURSELF.
Do not wait for a dispatch between them.** If a unit is blocked, that is a callback too — fire it
and move to the next unit in the queue.

---

## UNIT 1 (now) — the reveal: how the codex-lineage pane scored YOUR ideas

Read `docs/demos/duel-1/WIZARD_SCORES_COD_ON_MU.md` (`c221bac`) in full. Its headline:

| your idea | their score | their verdict |
|---|---:|---|
| MU-1 routing backtest | **875** | best next demo |
| MU-3 foreman-lite completion judge | **805** | credible RED arms; concurrency/state-baseline open |
| MU-4 working-point claim-checker | **735** | shippable, but claim extraction + citation-span underspecified |
| MU-5 signal-kit | **640** | correct meta-lesson, greenfield, no immediate lane payoff |
| MU-2 admission screen hook | **470** | *"the literal credential branch leaks what it claims to protect"* |

**MU-2 at 470 is the one that matters.** They are alleging your implementation sends the very
secret it exists to protect. Either that is true — in which case it is the most important finding
of this duel and you should say so plainly — or their reading is wrong and you can show the exact
lines that prove it. Do not split the difference.

Write `docs/demos/duel-1/WIZARD_REACTIONS_MU.md`: where they are right, where they are wrong and
why, and which of your own scores or ranks you now change. Quote file+line when you disagree.
Pane 1's `WIZARD_REACTIONS_CC.md` (`5343463`) is the shape to match — it concedes three hits,
pushes back on exactly one, and names what would settle the disagreement.

## UNIT 2 (self-claim on callback) — steelman the idea you scored LOWEST

You gave CC-1 (fact-ledger companion) 740, last of five. Now write the **strongest possible case
for it** — stronger than pane 1's own pitch. Pane 1 has since named the mechanism it was missing
(deterministic extractor → **Choice** over candidate lines → **Noul** verbatim check); steelman
*that* version, not the one you scored.

Output `docs/demos/duel-1/WIZARD_STEELMAN_MU.md`. The test of a good steelman: pane 1 reads it and
finds an argument for their own idea that they did not have.

## UNIT 3 (self-claim on callback) — the blind-spot probe

Read both idea files and both score files. Then answer: **what important demo did NEITHER side
propose?** Ground it in a `docs/demos/USAGE-MAP.md` section, and say why both of us missed it — the
adversarial exchange has expanded the context, and this is where the most creative output of the
whole method comes from. One to three ideas, each with its four ship artifacts sketched.

Output `docs/demos/duel-1/WIZARD_BLINDSPOTS_MU.md`.

---

## REPLY-VIA — fire all three the moment EACH unit lands (DONE, BLOCKED, or NEEDS-RULING)

1. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt path> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to ChartreuseTern -s "[jev-demo-loop-a1q] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
3. The artifact itself, committed own-files-only with a verification level in the subject
   (`[pending]` is correct for judgment docs — do not borrow the tree's green).

Carry every time: bead id · commit sha · **NEXT** (the next unit in this queue, named) ·
**NO-CLAIM** (what you did not verify).

A BLOCKED callback is a success — it routes around the unknown. Silence is the only failure.

## NON-GOALS

No implementation of any demo. No beads. No PLAN.md. No edits to `WIZARD_IDEAS_CC.md`,
`WIZARD_SCORES_COD_ON_MU.md`, or pane 1's receipt — quote them instead.
