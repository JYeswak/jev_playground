# Wave: learn Jev, then apply it — from pane 1 AmberWillow

Joshua: "My goal is to learn as much about jev and start applying it to our own systems. that is
the goal of this repo." And tonight: "focus more on jev." The W7.0 fresh runs are mostly in
(receipts `docs/demos/upstream-repro/*-w70-*.md`, EVAL.md sections by SunnyTiger). This wave turns
them into knowledge a stranger can read and into three applications in our own systems.
Depth directive and W7.0 standard still bind. Gated commits. Agent Mail is in recovery: coordinate
by `ntm send`; SunnyTiger stays sole EVAL.md writer until 05:00Z.

## Pane 5 — SunnyTiger: W7.3 "What the clones teach about Jev"

Write `notes/deep/w73-what-clones-teach.md`: the findings a builder needs, each one sentence plus
the receipt path and line that backs it. Cover at least: where Jev beat an incumbent (T6) and where a
floor tied or beat it (T5: jev-benchmark lexical 58/60 > Jev 52/60 is the model case of a seat that
should be refused); what calibration looks like at the N we have (T7, including "not observable");
stability (T8 flip rates); thresholds (jevcal: per-question thresholds fit on t001–t200 transfer to
t201–t400 — say exactly what transferred and what did not); transport behaviour (T9: the JS SDK leak
and our `jev-client` fix); cost per answered question where measured. Then a table: question shape
(noul/choice/score) × task class × verdict (SELF / FLOOR / INCUMBENT) × receipt. No sentence without
a receipt; a finding seen once says "one run". Callback `CALLBACK-P5-W73-DONE`. Pane 1 folds it into
README.

## Pane 3 — TopazRaven: W7.4 rank and pick three applications

Input: `notes/deep/clone-ledger.tsv` (14 `apply` rows) plus every W7.0 receipt. Score each apply row
with AGENTS.md's selection rule, in order: ground truth exists today; positive-class prevalence;
cost to measure; decision leverage — and one more column from tonight: the clone's W7.0 result class
(an application whose source seat was FLOOR is refused unless the application changes the task).
Write `notes/deep/w74-ranking.tsv` with every input number cited. Take the top three. For each,
create a bead (`br create`, WHAT/WHY/ACCEPTANCE, label `jev,w74`, parent `jev-deep-kit-8q7`)
naming the omp surface or product path it lands on, the preregistered bar, the planted negative,
and the incumbent arm. Commit the bar files as `[pending]` before any live call. Do not build yet;
callback `CALLBACK-P3-W74-DONE` with the three bead ids and why each beat the fourth.

## Pane 2 — RedMaple (grok): planning round 2

The plan has integrated round 1 from four reviewers (panes 2, 3, 5, 6; log in Appendix E) and grew
W7.0 (the testing standard). Read `docs/PLAN-DEEP-KIT-20260922.md` at `e106eb7` whole, then apply the
planning-workflow review prompt (verbatim in your `p2-wave1.md` Part B) as round 2. Write
`notes/deep/review-r2-p2.md`. Focus where round 1 could not look: W7.0 (is each test able to fail?
does the class profile route every clone correctly given what the W7.0 receipts actually did?),
W7.3/W7.4 (are they specified tightly enough that two panes would produce the same ranking?), and
the Phase C bead conversion (what in §4 cannot become a bead as written?). At least one removal.
Callback `CALLBACK-P2-R2-DONE`.
