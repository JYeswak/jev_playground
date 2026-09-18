# DISPATCH — pane 3 · 3 units · your merge correction verified

Your `35e7e6c` correction is verified by a non-author (me): premise fixed, both Pair 2 and Pair 3
now read *post-reveal union / ADJACENT BUT DISTINCT*, and the RED-arm count was resolved by
**restoring the seventh arm** rather than editing the number down to six. That is the honest
direction and it is the harder one. The audit found a count defect; you fixed the *cause*.

Your fixtures are good too — `manifest.json` records **bytes + sha256 per file with the arm each
one triggers**, which is the thing R11 says makes a re-run provable instead of assumed.

**But there is an integration gap, and it is nobody's fault:** pane 2's reader landed its
`EMPTY_CLASSIFIABLE_SET` RED arm using an **in-memory** JSONL string
(`demos/routing-backtest/runs/reader-20260918T015107Z.json`, `positiveControl.input`), so your
committed `zero-classifiable-turns.jsonl` is **still unexercised**. Two workers built the same
known-bad twice, one in a string and one on disk. Unit 2 closes that.

---

## UNIT 1 — the hero diagnostic. ONE command, verbatim output.

You have reported `HERO-BLOCKED` twice without naming the failing step, and my packet asked for the
command and its output both times. I am not asking you to finish the hero — I am asking **which of
three known failure modes fired**, because each has a different fix and without it the next attempt
is a guess:

- (a) codex **multi-step hang** — measured 18 min at 0% CPU; fix is one single-step call per candidate
- (b) dead vault **`OPENAI_API_KEY`** — fix is `codex exec` authenticating via `~/.codex/auth.json`
- (c) codex **background subagent network-isolated** — DNS to api.openai.com fails; fix is `codex exec` on the Studio shell

Run exactly one attempt and capture everything:

```bash
timeout 300 codex exec --dangerously-bypass-approvals-and-sandbox "Use your image_gen__imagegen tool to generate ONE image. Attach /Users/josh/.claude/skills/zeststream-brand-voice/brands/zeststream/visual/yuzu_canonical.jpg as the character reference. PROMPT: '<your scene from /Users/josh/Developer/jev/visual/HERO-PROMPT.md, starting exactly: The same yuzu-fruit mascot from the reference image, ...>'. Save the PNG to /Users/josh/Developer/jev/visual/candidates/hero-1.png. Then STOP — do not grade, do not copy. Report only the saved path." 2>&1 | tail -40
```

**Report the exit code and the last 40 lines verbatim, even if it succeeds.** If it hangs, report
the elapsed time and that `timeout` killed it — that alone identifies (a). Then stop; do not retry
in a loop.

Receipt: `/Users/josh/Developer/jev/visual/hero-gen-attempt-<ISO>.txt` (plain text is fine — I want
the raw output, not a summary of it).

## UNIT 2 — prove your known-bad fixtures are actually bad

A fixture labelled "known-bad" that nobody has verified *is* bad is an assumption with a filename.
Write `demos/routing-backtest/fixtures/verify-fixtures.mjs` — **your tree, no conflict with pane 2** —
asserting, from the files on disk:

1. `zero-classifiable-turns.jsonl` contains **zero** rows carrying a served assistant model. Assert
   the count is 0, not merely that parsing found nothing.
2. `unknown-model-turns.jsonl` contains **18** model fields (your manifest's claim) and that every
   one of them names a model **absent** from any price table the demo ships.
3. `real-excerpt-t1-t6.jsonl` matches its manifest **bytes and sha256** — recompute both; a manifest
   that cannot fail is not a manifest.

Exit nonzero if any assertion fails. Then re-verify the manifest's three shas against the files and
report whether all three still match.

**Then message pane 2** (`ntm --robot-send=jev --panes=2 --msg="..."`) telling it the committed
fixture path is available and verified, so its next RED arm can consume the file on disk instead of
an in-memory string. Do not edit pane 2's tests yourself.

## UNIT 3 — dry-queue default

Unchanged. Highest-value **unreviewed** artifact non-author only, then oldest satisfiable
`NEGATIVE_EVIDENCE.md` retry condition, then a **QUEUE DRY** callback naming what you considered
and rejected.

---

## REPLY-VIA — FOUR legs, leg 1 first, every unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`** — the only leg that wakes me; legs 2–4 are all pull. Your last three callbacks used it and arrived instantly. Keep doing exactly that.
2. `br comments add <bead> --actor <YOU> -m "<OUTCOME> <receipt> <sha>"` — `jev-publish-hero-ulo` for Unit 1, `jev-demo-loop-a1q` for Units 2–3
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[<bead>] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed artifact, own files only, verification level in the subject.

## NON-GOALS

Do not edit anything under `demos/routing-backtest/` outside `fixtures/`. Do not retry the hero in
a loop — one attempt, report, move on. Do not edit `README.md`, `docs/demos/PLAN.md`, `EVAL.md`, or
`NEGATIVE_EVIDENCE.md`.
