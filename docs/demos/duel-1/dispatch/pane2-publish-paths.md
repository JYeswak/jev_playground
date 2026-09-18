# DISPATCH — pane 2 · publish-path scrub · 3 units

Your BLOCKED callback was correct and useful: `a6e1353` scrubbed 76 `thinkingSignature` fields and
134 machine paths out of both fixtures, refreshed the replay receipts, and left the publishability
gate honestly unproven because `bin/check.sh` and `CHECK_SH_PUBLISH_LEDGER` do not exist in this
repo. **Do not wait on that.** It is filed; these three units are all reachable now.

**I measured the remaining surface across the whole tracked set.** Denominator: 91 tracked files.
`/Users/[a-z]+` matches **40 times in 7 files**. Positive control: all 40 are `/Users/josh`, so the
pattern fires. Your fixture scrub did not cover these because they are not fixtures.

```
compaction/runs/ab-20260917.json                     12   <- UNIT 1 (yours)
.beads/issues.jsonl                                  ~22  <- mine, bead bodies I wrote
NEGATIVE_EVIDENCE.md                                  2   <- mine
.flywheel/worksheets/2026-09-17-lane-substrate.md     2   <- mine
GATES.md                                              1   <- mine
githooks/commit-msg                                   1   <- UNIT 2 (yours)
upstream/MANIFEST.tsv                                 1   <- mine (sync-docs generator)
```

I am taking the prose and the generator. You take the receipt and the hook.

---

## UNIT 1 — the receipt, by RE-RUN, never by retro-edit

`compaction/runs/ab-20260917.json` embeds 12 absolute fixture paths
(`/Users/josh/Developer/jev/compaction/fixtures/seed-svc/...`).

**The rule that matters here, and you already applied it correctly once:** a receipt is evidence of
what actually ran. Hand-editing its bytes converts evidence into assertion. You produced *fresh*
replay receipts rather than rewriting the old ones — do the same here.

1. Fix the **producer** first so it records repo-relative paths (`compaction/fixtures/...`), not
   absolute ones. An absolute path in a receipt is also a reproducibility defect, not only a
   publish defect: nobody else can re-run it.
2. Re-run the A/B and emit a new receipt.
3. **The re-run must reproduce the original verdict.** The old receipt measured 3 questions
   (`q1,q2,q3`), `armA.score 1` vs `armB.score 3`, 4188 vs 1241 context bytes, verdict "B wins".
   If the fresh run disagrees, that is a finding and outranks the scrub — report it, do not paper
   over it.
4. Leave the old receipt in place unless the conductor rules otherwise; superseding is a record,
   deletion is not.

## UNIT 2 — the hook's hardcoded home

`githooks/commit-msg:22` prints a re-run hint containing
`"${FOUNDRY_DIR:-/Users/josh/Developer/foundry}"`. The fallback embeds an operator home directory
in a file we are about to publish.

Fix so the **default carries no home path** — e.g. print the hint only when `FOUNDRY_DIR` is set,
and otherwise name the variable the reader must set. Keep the hook's behaviour identical on the
happy path.

**Verify both directions, or it is not verified:** (a) with `FOUNDRY_DIR` set, the hint still
points where it should; (b) unset, the message is useful and leaks nothing. Then confirm
`foundation/gates.sh` is still ALL GREEN and that a real commit still passes and a subject with no
verification level still FAILS — the hook's whole job.

## UNIT 3 — dry-queue default

On finishing Unit 2, self-claim from the standing rule: review the highest-value **unreviewed**
artifact in the lane, non-author only. Right now the strongest candidate is
`DUELING_WIZARDS_REPORT.md` if I have landed it (I am writing it now) — it will be a synthesis
built on *your* convergence ruling, and it will have zero graders. Audit whether I represented
your ruling faithfully or softened it in my favour.

If that file does not exist yet, fall through the rule: oldest satisfiable
`NEGATIVE_EVIDENCE.md` retry condition, or a `GATES.md` gap with no witness, then a **QUEUE DRY**
callback naming what you considered and rejected.

---

## REPLY-VIA — and leg 2 is now known to work

**Measured this turn:** I ran the positive control. `am mail send` from CyanFalcon to CyanFalcon
landed and `am inbox --agent CyanFalcon` went from `count: 0` to `count: 1`. **The transport is
fine.** So a missing mail is now a missed step, not a broken tool.

1. `br comments add jev-publish-redteam-7s0 --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-publish-redteam-7s0] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
3. Committed receipt, own files only, verification level in the subject.

Carry: bead id · sha · **NEXT** · **NO-CLAIM**. Finish one, fire its callback, then start the next
YOURSELF. Do not wait for a dispatch between them. A blocked unit is a callback too.

## NON-GOALS

Do not touch `NEGATIVE_EVIDENCE.md`, `GATES.md`, `.flywheel/**`, `upstream/MANIFEST.tsv`,
`scripts/sync-docs.sh`, `README.md`, or `LICENSE` — all mine this wave, and a path-limited commit
on a shared file sweeps the other lane's lines into your commit. Do not chase `bin/check.sh`.
