# DISPATCH — pane 2 · duel-1 STEELMAN, then a 2-unit queue (do not go idle)

Bead: `jev-demo-loop-a1q`. Your cross-scores landed (`c221bac`). The MU-2 finding — *"the literal
credential branch leaks what it claims to protect"* — is the sharpest thing either grader produced;
pane 3 is being asked to answer it directly.

**This packet contains THREE units. Finish one, fire its callback, then start the next YOURSELF.
Do not wait for a dispatch between them.** A blocked unit is also a callback: fire it, move on.

---

## UNIT 1 (now) — steelman the idea you killed

You scored MU-2 (context-admission screen hook) **470**, your lowest. Now write the **strongest
possible case for it** — stronger than its author's own pitch — *assuming the credential-leak defect
is fixed*. State the fix you would accept as part of the steelman (what must the screen never send,
and how would a test prove it never sends it).

This is the highest-signal unit in the method: an agent forced to steelman the idea it just killed
usually discovers either that the idea was better than its implementation, or that the defect is
structural and no fix exists. Say which, plainly.

Output `docs/demos/duel-1/WIZARD_STEELMAN_COD.md`.

## UNIT 2 (self-claim on callback) — the blind-spot probe

You have now read one full idea file and scored it. Read the other
(`docs/demos/duel-1/WIZARD_IDEAS_CC.md`), plus `WIZARD_SCORES_MU_ON_CC.md` and
`WIZARD_REACTIONS_CC.md`, then answer: **what important demo did NEITHER duelist propose?**

Ground each candidate in a `docs/demos/USAGE-MAP.md` section (14 patterns, pinned SHAs) and say why
both models missed it. Your lineage is the one that differs most from both duelists, which makes
your blind-spot list the most valuable of the three.

Output `docs/demos/duel-1/WIZARD_BLINDSPOTS_COD.md`. One to three ideas, each with its four ship
artifacts sketched (install · tests incl. RED arms · receipt · EVAL row).

## UNIT 3 (self-claim on callback) — verify the numbers, do not trust them

Both duelist files cite measured receipts. Pane 3 already found one false claim in pane 1's file
(it said four recall questions; `jq '.questions | length'` on `compaction/runs/ab-20260917.json`
returns **3** — so arm B scored 3/3, not "3–1"). **Assume there are more.**

Re-derive every numeric claim in `WIZARD_IDEAS_CC.md`, `WIZARD_IDEAS_MU.md`, and both score files
against the artifacts they cite (`compaction/runs/*.json`, `foundation/runs/*.json`,
`docs/demos/USAGE-MAP.md`, the vendored clones' pinned SHAs). Report each as EXACT / WRONG (with the
true value) / UNVERIFIABLE (no artifact names it).

Output `docs/demos/duel-1/runs/claim-audit-<ISO8601>.json` — machine-readable, one row per claim:
`{file, line, claim, cited_artifact, rederived_value, verdict}`. This is not busywork: it is the
first real fixture for the claim-check demo both duelists ranked in their top two.

---

## REPLY-VIA — fire all three the moment EACH unit lands (DONE, BLOCKED, or NEEDS-RULING)

1. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt path> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to ChartreuseTern -s "[jev-demo-loop-a1q] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
3. The artifact itself, committed own-files-only, verification level in the subject.
   Unit 3 may legitimately claim `[test]` if you re-derive with commands; units 1–2 are `[pending]`.

Carry every time: bead id · commit sha · **NEXT** (the next unit in this queue, named) ·
**NO-CLAIM** (what you did not verify).

If you have no Agent Mail identity: `am agents register --project ~/Developer/jev --program omp
--model <yours>` and let it auto-generate the name.

## NON-GOALS

No implementation of any demo. No beads. No PLAN.md. No edits to either `WIZARD_IDEAS_*.md` or to
pane 3's score file — quote them instead.
