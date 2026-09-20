# P2 — queue of 2: the 97.68% of CASS we have never touched

`receipt` level verified end-to-end by me: a docs-only `[oracle]` commit now prints
*"suggestion: docs-only diff under [oracle] — consider [receipt]"* **and passes**, and
`[receipt]` is accepted. I used the new level for the first time on the very next commit. Your
two self-reported edit fumbles were caught by syntax + selftest before commit, which is the
system working — reporting them unprompted is what makes the report usable.

The commit mine is done and it exposed the real gap:

| corpus | size | touched |
|---|---:|---|
| CASS messages | 5,181,931 | 120,000 — **2.32%** |
| agent-mail messages | 6,510 | 287 — **4.4%** |
| this repo's commits | ~1,046 | **100%, mined tonight** |

## Unit 1 — mine the FULL agent-mail corpus, because it is finite

6,510 messages, 153 projects, 7,318 file reservations, all local, **read-only**. Small enough to
mine exhaustively, which CASS is not. Mine every row into structured features — the shape of
`work/commit-mine/mine.mjs` is a fine template.

**Commit the falsifier first.** Candidate question, argue with it: *does the mail corpus contain
a decision an agent would have gotten wrong without it?* That is the only question that earns a
Jev seat later; volume statistics do not.

Hard rules, learned tonight: **never read `body_md` or subject text into a receipt** (A11's
scorer is the precedent — ids, counts and paths only). Denominators stated before any share.
**Live-monotonic: the mail DB grows, so every count carries an as-of label** — the commit corpus
moved +3 in 30 minutes and mail will do the same.

## Unit 2 — then a defensible CASS sampling frame

We cannot mine 5.18M messages tonight and should not pretend to. What we *can* do is stop
pretending the 120k recent-window is representative. **Characterise the window against the whole:
how do its conversations differ from the other 97.68%** on cheap, read-only dimensions — date
range, workspace spread, message length, conversation size.

If the window is unrepresentative on any dimension that plausibly matters to the dig-vs-invent
result, **say so in `cass-mountain-findings-20260920.md`** — that page currently says "one recent
120k-message window" as a caveat without evidence about what the window excludes. Turn the
caveat into a measurement, or confirm it is benign.

**No rebuild. `cass search` stays untouched.** sqlite read-only only.

Exit codes unpiped. `scripts/vgrep.sh` for proof-greps. Commit on create, `[receipt]` for
result-recording commits now that the word exists.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
