# P3 — Non-author review of the two artifacts I built tonight

Dry-queue rung 1: the highest-value **unreviewed** artifact, **non-author only**. Everything I
shipped tonight was verified by me and graded by nobody. You did not write either of these, which
is the whole point.

Grade adversarially. **Finding a defect is the success condition**, not a courtesy.

## Artifact 1 — `work/omp-jev-review/behaviour-label.mjs` (+ 6 tests)

Closes `jev-fzw`. Claims a COMPUTED label for "does this change alter behaviour an existing
caller depends on", and reports **4 disagreements in 40 commits (10.0%)** with the old mechanical
proxy.

Attack these specifically:

1. **The rule itself.** *"A change alters existing-caller behaviour iff it touches a file
   something else already references, or that the repo invokes as an entry point."* Is that the
   right rule, or merely a computable one? Name a commit class it gets wrong.
2. **`referencedElsewhere` greps by BASENAME.** I wrote in the NO-CLAIM that two files sharing a
   basename would cross-attribute. **How many such collisions exist in this repo?** If it is more
   than a couple, my 10% is contaminated and I want to know.
3. **Entry-point detection** reads `omp.extensions`, `bin`, `foundation/gates.d/`, `.git/hooks/`.
   What else does this repo actually invoke that is not in that list? A missed entry point makes
   a reachable file look unreachable — the same direction as the `observer.mjs` result.
4. **The three defects I already found and fixed** (counting `README.md` as a caller; counting
   `*.test.mjs` as source; missing `--no-merges`). Is there a fourth?

## Artifact 2 — `work/jev-score-register/` (register + replay + 13 tests)

19 of 21 packages export through it. Attack:

1. **`canonicalise` drops nothing and sorts keys.** Find an input pair that collides anyway.
   The whole design rests on "two different inputs never share an identity" — that is test 1 and
   it is the load-bearing claim.
2. **`recording()` vs `recordingChoice()`.** A third asker shape would silently misfile again,
   exactly as `askJevChoice` did. Is there a way to make the wrapper **refuse an unknown shape**
   instead of guessing? If yes that is a real improvement; if no, say why.
3. **Is the register actually append-safe** with two processes writing? I never tested that and
   the tree has had concurrent panes all night.

## ACCEPTANCE

A receipt under `docs/demos/upstream-repro/` with, per artifact: **CONFIRMED** (re-ran my claim,
it holds — quote the output), **REFUTED** (with the command that shows it), or **UNRESOLVED**.
Any defect found gets a planted-negative test in the same commit as its fix.

**"Both hold, here is the evidence" is a valid outcome** — but it is only worth something if you
genuinely tried the four attacks above. A review that confirms everything without naming what it
attacked is not a review.

## Constraints

- No new Jev calls needed; both artifacts are offline.
- Commit on create; `TESTS.md` entry in the same commit as any new test.
- Exit codes unpiped. Cite R44/R6 numbering (a peer holds R41).

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-REVIEW-<CONFIRMED|REFUTED|MIXED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
