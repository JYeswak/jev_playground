<!-- A/B verdict migration (2026-09-18): any literal n=1 relative verdict below is historical/retracted. Current harness withholds verdicts until each arm has >=10 zero-spread samples; see compaction/ab/verdict.ts. -->

# DISPATCH — pane 3 · duel-1 cross-score: score the CLAUDE side's ideas

Bead: `jev-demo-loop-a1q` (conductor holds it; you are grading, not claiming it).
You are the **non-author, different-lineage** grader for the Claude duelist. Pane 1 wrote those
ideas; you did not. Pane 2 (codex-lineage) is grading the muse file and pane 1 is grading nothing — that is the
arms-length rule this duel exists to enforce.

## Read, in this order

1. `docs/demos/duel-1/WIZARD_IDEAS_CC.md` — **the file you are scoring.** Read all of it,
   including its long-list table, its `Cut, with the reason` block, and its declared ranking bias.
2. `docs/demos/USAGE-MAP.md` — 14 grounded Jev patterns with pinned SHAs. Every idea claims a
   section; check the claim.
3. The two receipts, because they are the only measured ground truth in this lane:
   - `compaction/runs/replay-big-20260917.json` — 179 events → 24 msgs; 13→8 msgs, 2333→1292
     chars (44.6%), `kept:0`, `failures:[]`.
   - `compaction/runs/ab-20260917.json` — `armA.score 1` vs `armB.score 3`, `verdict "B wins"`,
     at 4188 vs 1241 context bytes. **Summarization beat Jev pruning 3–1 at a third of the bytes.**
4. `AGENTS.md` §4 (Definition of Done) — the four artifacts an idea must be able to produce.

## Score each idea 0–1000

One integer per idea plus a short evaluation. The score must reflect, jointly:

- **Is it smart and true?** Does the cited USAGE-MAP section actually support it, or is the
  citation decorative? A miscited idea is capped at 400 no matter how appealing.
- **Real-world usefulness** to us (this lane, this fleet) and to AI coding agents generally.
- **Can it reach the four ship artifacts** — install script, deterministic tests *including RED
  arms*, receipt, EVAL row? An idea with no plausible RED arm cannot ship here; say so.
- **Does the utility justify the complexity and tech debt** it adds to a lane that already
  carries 7 gate stages and 3 live git hooks?
- **Readiness**: does working code with a receipt already exist in this tree, or is it a greenfield
  build wearing a citation?

## Rules of engagement

- **Be candid.** If your scores all cluster above 800 this dispatch failed. Some of these five
  ideas are weaker than the others — find which and say why, in technical specifics.
- **Do not reflexively mark down** because another model wrote them. A defensible high score with
  a reason is worth more than a low one with a sneer.
- Name the single **strongest** and the single **weakest** idea explicitly, with the sentence that
  decided it.
- If two ideas are the same idea in different clothes, say which and merge them.
- Quote the file and the line when you disagree with a claim.

## Output

`docs/demos/duel-1/WIZARD_SCORES_MU_ON_CC.md` — your scores + evaluations, one section per idea,
with a summary table (idea · score · one-line verdict) at the top. Own-files-only: stage that path
and nothing else.

## REPLY-VIA (all three, the moment it lands — DONE, BLOCKED, or NEEDS-RULING)

1. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> docs/demos/duel-1/WIZARD_SCORES_MU_ON_CC.md <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to ChartreuseTern -s "[jev-demo-loop-a1q] <OUTCOME> scores MU-on-CC" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
   (your identity: `am agents list ~/Developer/jev`; register one if you have none)
3. The scores file itself, committed with a verification level in the subject
   (`[pending]` is correct for a judgment doc — do not borrow the tree's green).

Carry: bead id · commit sha · NEXT · **NO-CLAIM** (state plainly what you did not verify — e.g.
"did not run any idea's proposed harness; scores are judgment, not measurement").

## NON-GOALS

No implementation. No beads. No edits to `WIZARD_IDEAS_CC.md` (pane 1 owns it). No PLAN.md.
Do not read `WIZARD_IDEAS_MU.md` again before you finish scoring — pane 2 is grading that one,
and your independence is the instrument.
