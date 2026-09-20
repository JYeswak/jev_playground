# Honesty pass 6 — the 20 commits since pass 5 (2026-09-20)

Same classification rule as prior passes. **USER** = a non-lane reader can install, run or read it
and get value; **ENABLER** = it makes USER work possible and something runs it; **PROCESS** = it
measures, audits or describes our own work and nothing branches on it.

## Tally

```
USER 9 · ENABLER 5 · PROCESS 5 · UNKNOWN 1   (20 commits)
USER share 45%   verdict: HEALTHY
```

Pass 5 was 36%. **Up 9 points, and the mechanism is the action I wrote down last pass**: batch the
ledger appends. Pass 5 carried 12 separate `docs(wave-*)` commits to one file; this window has
**one** (`Wave ledger batch: sections 8, 9, 10, 23, 24 lines`). That single change accounts for
most of the movement, which is worth noting precisely because it means the underlying work did not
change — **the previous number was partly an artifact of my commit granularity, not of drift.**

## USER items in this window

- `docs/INTEGRATIONS.md` corrected **twice**, both times against our own recommendation: the
  0-of-28 precision caveat, then the full both-directions update once recall was ruled.
- `jev-m7r` ruling — a stranger can read why our best component is unevidenced.
- `behaviour-label.mjs` + 6 tests — a computed label anyone can run.
- `docs/RULES.md` rule 9, proven on both sides of a fix.
- R44 and its leg-1 ruling — a public refusal with a trigger someone else can defeat.

## What we got wrong, and it is the same thing every time

**Three more instances of the one defect**, bringing the session to twenty:

1. **§24's placeholder hunt** — my broader grep found 4 files to their 2; three were essays
   *teaching* not to leave the placeholder. Mention-vs-use, and it nearly made me contradict a
   correct report.
2. **My "dead transport" call** — I diagnosed pane silence as broken messaging. The instrument the
   tick names says `is_rate_limited: true`. **Absence of a signal read as evidence about its
   cause**, when the tool that answers it was one command away.
3. **R44 leg 1** — `0 fires` came from a filter in the *census*, not the rule. The shipped rule
   still fires `harm_fire 0.96` on the same probe. The pane disclosed this plainly; **the wording
   that let a census answer a question about a product was mine.**

That third one is the sharpest thing in this window: **I wrote an acceptance trigger as commands
to run rather than as a property of the shipped artifact**, and a correct execution of those
commands produced a true statement about the wrong object.

## What improved

- **Every worker disclosure this window was honest and unprompted.** "The shipped rule is
  untouched", "toy mechanics; pattern unjudged", "conductor cases on stated provenance". Each one
  saved a verification round.
- **The instruments caught me twice** — stage 95 rejected my unregistered numerals, lane-status
  rejected my fabricated digest. Both times my `STATUS.tsv` rows were wrong and the gate was
  right.
- **Six rulings closed**, including two that ended lines of work: the verification-weakening
  family abandoned, and harm-rule declared unevidenced in both directions without declaring it
  broken.

## Actions

1. **Write triggers as properties of artifacts, never as commands.** Three legs of R44 were
   satisfiable without the product changing.
2. Keep batching ledger appends — it worked, measurably.
3. `git log -- <path>` before naming an author. Zero mis-routes this window, after three last
   window; the rule is holding.

## NO-CLAIM

One reader, classifying from commit subjects plus memory of the window, not a line-by-line audit
of all 20. The USER/PROCESS boundary for rulings is contestable — I count a public ruling as USER
when a stranger could act on it, and someone could reasonably score those as PROCESS, which would
put this window nearer 25%. Pass 5's 36% and this 45% come from the same judge without an anchored
rubric, so the trend is directional, not metric.
