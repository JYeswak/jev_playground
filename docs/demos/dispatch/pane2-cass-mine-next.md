# P2 (Muse) — PR #35 is already landed; go straight to the next mine

**Do not re-land PR #35.** I checked before writing this: it is merged and on `origin/main` at
`f6414c6`, and `docs/demos/upstream-repro/cass-dig-vs-invent-20260920.md` is tracked and present
(the earlier push conflict resolved). Re-landing it would be work that is already done.

Standing result to build on, from that receipt: **always-invent 0.159420290 mean loss vs
dig-iff-count>0 at 0.058 — dig BEAT on recent 120k messages.**

## Hard constraints

- **Do NOT start a second cass rebuild.** `cass search` hung because the FTS virtual table is
  missing under an in-flight rebuild. A second one makes it worse. If you need search and it is
  unavailable, say so and mine a path that does not need it.
- **No synthetic 10-case designs.** Every number comes from real corpus rows. A hand-authored
  vignette set cleared its bar twice in this lane and then scored 0.750 on 186,449 real windows.
- Codex is out of tree. Do not spawn NTM sessions.

## Units — finish one, fire its callback, then start the next YOURSELF

1. **Next CASS dig-vs-invent slice** from the 24-approach list, or the **mail→cass join** mine —
   pick the one whose data is reachable without a rebuild, and say in the callback which you
   rejected and why.
2. Pre-register the falsifier **before** scoring: write down what result would kill the approach,
   commit it, then run. That order is load-bearing here and is rule 3 of `docs/RULES.md`.
3. The bar is **beat the constant baseline on a named adversarial subset, not just in aggregate.**
   Named subsets have overturned pooled numbers 3 times out of 3 in this lane, always
   optimistically. An aggregate win with a subset failure is `HELD`, not `CLEARED`.

## Acceptance

A receipt under `docs/demos/upstream-repro/` with: the corpus and its exact denominator, the
pre-registered falsifier and its sha, the baseline, the result, and the named-subset breakdown.
`REFUSE` and `HELD` are real outcomes — state them plainly rather than reaching for CLEARED.

Do not run formatters or repo-wide gates — I verify at phase end. Exit codes unpiped; a piped
`| tail` reports tail's status and has caused two false reads tonight. Commit on create: peers
branch-switch this tree and uncommitted work has been lost twice today.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-CASSMINE-<DONE|HELD|REFUSE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
