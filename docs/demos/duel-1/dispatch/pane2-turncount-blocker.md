# DISPATCH — pane 2 · demo-1 BLOCKER `jev-demo-loop-a1q.5` · 4 units

Your queue landed complete: reader, counterfactual, receipt, EVAL row, install script, TESTS
registry, gates green. **And I clean-clone tested your install as a stranger — it passes:**
`git clone` into a temp dir → `bash install.sh` → **10 pass / 0 fail, exit 0**, and the documented
command runs and emits a receipt. The "works on my machine" class is genuinely closed. That is
good work.

**Then the denominator didn't add up, and it blocks the ship claim.**

Same file, three artifacts, three counts:

```
fixtures/real-excerpt-t1-t6.jsonl rows ......... 94
rows carrying a "model" field .................. 18   (all muse-spark-1.3-contributor)
fixtures/manifest.json purpose ................. "happy-path corpus turns 1-6"
your reader on that fixture .................... {"sessions":1,"turns":1,"classifiableTurns":1}
```

At most one is right. Your reader finds **30** turns across two real omp logs, which is plausible,
so this is specific to how the excerpt is segmented — not a general failure.

**Why it blocks:** all four ship artifacts exist, but the ONE result a stranger can reach is
**n=1**, while the fixture's own manifest says 6. A stranger runs the documented command, sees
`turns:1`, and cannot tell whether that is the corpus, the reader, or a bug. This lane's rule *"an
empty scan set is an ERROR, not a pass"* has a sibling nobody had written down: **a one-turn scan
set is not a demonstration.** And the demo's headline result — 0.047% savings over 30 turns — is
reproducible only against `~/.omp` logs a stranger does not have.

---

## UNIT 1 — rule on which count is authoritative

Re-derive all four numbers yourself and quote them. Then state **which is authoritative and why**.
My hypothesis — and it is only that, I have not read your segmentation code — is that the excerpt
holds one user prompt followed by many assistant/tool rows, so a turn rule keyed on user prompts
sees 1 while the manifest author counted assistant exchanges. **Confirm or refute it from the
code.**

## UNIT 2 — fix it at the source, and define "turn" exactly once

Three artifacts asserting three counts is **a missing shared definition, not three bugs.**

- Put the definition of a turn in **one place** and have the reader and the fixture READMEs cite
  it. If `manifest.json`'s "turns 1-6" is the wrong one, it becomes the measured number; if the
  reader's segmentation is wrong, correct the reader. **Do not fix this by editing whichever
  artifact is easier to edit.**
- `fixtures/**` is pane 3's tree. If the manifest or a README must change, **message pane 3** with
  the exact replacement text (`ntm --robot-send=jev --panes=3 --msg="…"`) rather than editing it —
  a path-limited commit on a file another pane holds sweeps their lines into your commit, which
  already happened once tonight (`d14387e`).

## UNIT 3 — make the stranger path non-vacuous, with a floor arm

- A stranger must reach a result that **shows something**: enough classifiable turns to exhibit a
  cheap-vs-frontier split, with at least one routable turn. n=1 is not a demonstration.
- **RED arm:** a run whose classifiable-turn count falls below a stated floor must **WARN or ERROR**
  rather than emit a receipt that reads like a successful backtest. Prove it fires.
- Fix `install.sh`'s closing line. It currently ends with a placeholder:
  `npm run backtest -- <session.jsonl>...`. Replace it with the exact copy-pasteable command
  against a shipped fixture. **No placeholders** is a hard rule, and a stranger should never have
  to guess an argument.

## UNIT 4 — dry-queue default

Unchanged: highest-value **unreviewed** artifact non-author only, then oldest satisfiable
`NEGATIVE_EVIDENCE.md` retry condition, then a **QUEUE DRY** callback naming what you considered
and rejected.

---

## REPLY-VIA — FOUR legs, leg 1 first, every unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`** — the only leg that wakes me.
2. `br comments add jev-demo-loop-a1q.5 --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-demo-loop-a1q.5] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed code + receipt, own files only, verification level in the subject.

**Re-run the clean-clone test yourself after Unit 3** and paste the stranger-visible denominator.
A fix I verify is worth less than a fix you can demonstrate from a fresh clone.

## NON-GOALS

Do not edit `demos/routing-backtest/fixtures/**` — message pane 3. Do not restructure `EVAL.md`
beyond correcting the row your fix invalidates. Do not touch the hero or `visual/**`.
