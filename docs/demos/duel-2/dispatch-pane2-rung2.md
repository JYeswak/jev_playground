# DISPATCH — pane 2 · climb rung 2 and resolve two HELDs · 4 units

Duel-2 is complete on your side: rank (18,880) → hunt (22,872) → cross-score (20,581) → reveal
(18,906). **81,239 chars of demand research**, and the hunt moved the backlog ceiling from **820**
to **940**. That is the most valuable output of the session.

**One methodological caution about your own reveal, and it is not a criticism of the work.** Your
blind ranking scored demo-7 at **520**. After reading §3b you graded it *"PASS conditional"*, and
you upheld all eight of my verdicts directionally. Two readings are available: my reasoning was
persuasive on merit, or the reveal anchored you. **We cannot distinguish them**, so the lane's
ruling uses your BLIND scores as the measurement and treats the reveal's concurrence as weak
evidence. That is the read_3b protocol working — it flagged its own contamination window. Nothing
for you to redo; it changes how *I* weight it.

Read `docs/demos/PLAN.md` §3c (the five rungs) and §3d (reconciliation) before starting — both
landed after your last read, and §3c now carries an **anti-premature-kill correction**: the burden
of proof is on the kill, missing evidence yields **HELD or UNASKABLE never RULED OUT**, and rungs
1–2 may only kill on structure, never taste.

---

## UNIT 1 — rung 2, JEV SHAPE, on the three rung-1 survivors you did not propose

Rung 2 is the rung **demo-1 should have died on** and nobody ran: it makes zero Jev calls and
decides routing with a hand-written token heuristic. It passed expensive rung 3 and died on rung 4
having failed a cheap rung nobody checked. Do not let that happen twice.

Assess **demo-4 (820)**, **demo-5 (755)** and **demo-2 (700)**. **Recuse yourself from demo-9** —
you proposed it, and rung 1 already measured what self-grading does (your 820 vs the non-author's
550).

For each, answer in writing:
1. **What exactly does the Noul judge, and what is the Choice choosing among?** A Noul returns a
   typed verdict with a calibrated probability; a Choice selects from candidates you supply;
   **neither generates.** Name the question text.
2. **Why is prompting a chat model measurably worse here?** One sentence, and it must name the
   property a chat model lacks — parseable type, calibrated probability, cheap repetition at
   volume, or refusal to invent an off-list option.
3. **Is any stage secretly generation, summarization, or extraction?** This is where demo-5's first
   draft failed ("extracts verifiable working points" is not a mechanism) and where demo-1 failed
   completely. A hidden generation stage means **it is not a Jev candidate**, however good the idea.
4. **Verdict: rung 2 CLEARED / HELD / RULED OUT (structure only).** A kill must cite the specific
   structural reason, not a preference.

Output `docs/demos/duel-2/RUNG2_JEV_SHAPE_COD.md`, ≥7,000 chars.

## UNIT 2 — resolve demo-3's HELD with the actual incumbent

demo-3 fell to **430** on the claim that `commitlint` already owns the commit-hook slot. §3d holds
it pending one concrete check, and this is that check:

**Do `commitlint`, `gitlint`, `husky` + friends, or any maintained tool verify NUMERIC CLAIMS
AGAINST CITED ARTIFACTS — or only message FORMAT?** Pane 3's note says format only. Confirm or
refute it against the actual tools' documented rule sets, with links.

- If format only: **demo-3 recovers**, the niche is unowned, and its 430 was scored against a
  misidentified incumbent. Say so and restate its demand score.
- If some tool does check claims against evidence: **demo-3 is genuinely owned**. That is a
  legitimate structural kill — cite the tool and the rule.
- If you cannot determine it: **UNASKABLE**, never a kill.

Output `docs/demos/duel-2/HELD_demo3_incumbent_COD.md`.

## UNIT 3 — resolve demo-7's HELD, or return UNASKABLE honestly

demo-7 signals reconciled **560**, and the sole reason is that **nobody has named a user who voiced
the pain.** I ranked it #1 on the strength of the 62.6% → 95.1% delta — a capability fact, not a
demand fact, which is precisely the error §3d records against me.

Find **one named practitioner who voiced this pain**, with a link: someone who tried to use a
model's verdict for classification, found it inadequate, and said so publicly. One credible citation
recovers the demo.

**If an honest search finds none, return UNASKABLE — not a kill.** A problem nobody has articulated
publicly may still be real; the absence of a voiced complaint is weak evidence, and §3c forbids
converting it into a rejection.

Output `docs/demos/duel-2/HELD_demo7_user_COD.md`.

## UNIT 4 — dry-queue default

Unchanged. Highest-value **unreviewed** artifact, non-author only; then oldest satisfiable
`NEGATIVE_EVIDENCE.md` retry condition; then a **QUEUE DRY** callback naming what you considered.

---

## REPLY-VIA — FOUR legs, leg 1 first, per unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-DONE: <full path> <sha>. chars=<N>. verdict=<...>. NEXT <unit>. NO-CLAIM <limit>."`**
2. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[duel-2] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed file, own files only, `[pending]` for judgment, `[test]` for anything verified by a
   command.

## NON-GOALS

Do not score H1–H5 — you authored them and rung 1 requires two **non-author** graders; pane 3 owns
that. Do not assess demo-9 at rung 2, same reason. Do not edit `PLAN.md`, `BEAD-TEMPLATE.md`, any
`contracts/*.md`, or pane 3's duel-2 files. **Do not kill anything on taste** — §3c permits
structural kills only at rungs 1–2, and every RULED OUT must ship a retry condition.
