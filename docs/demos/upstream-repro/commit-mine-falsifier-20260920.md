# Falsifier for the full commit-history mine — committed BEFORE the miner exists

Coverage measured 2026-09-20, which is why this mine exists:

| corpus | size | what we have actually touched |
|---|---:|---|
| CASS messages | 5,181,931 | 120,000 recent-window (**2.32%**) |
| agent-mail messages | 6,510 | 287, one project (**4.4%**) |
| this repo's commits | 1,071 | **0 systematically** — the ledger is hand-written prose |

The commit history is the only one of the three that is **complete, local, free to read, and
never mined**. So: mine all 1,071.

## The question

Our verification-level convention puts `pending|selftest|test|mutation|oracle|live` in every
commit subject. **Claim under test: that level is informative — it predicts whether a commit
carries executable evidence.**

`H1`: commits marked `live`/`oracle` touch runnable artifacts (tests, scripts, fixtures,
selftests) at a materially higher rate than commits marked `pending`.

## Falsifiers, pre-registered

- **F1 — the level is noise.** If the runnable-artifact rate for `live|oracle` is within ±10
  percentage points of the rate for `pending`, the convention is decorative and I will say so.
  It has been enforced by a commit-msg hook all session, so "we always wrote it" is not evidence
  it means anything.
- **F2 — the mine is unrepresentative.** If fewer than 80% of the 1,071 commits carry a parseable
  level, the denominator is too thin and the result is `UNMEASURED`, not a finding.
- **F3 — mechanical-only.** If the classification of "runnable artifact" is pure path-matching,
  the finding is about paths, not evidence. It must be stated as such and not dressed up as a
  claim about verification.

## Then, and only then, Jev

If the mechanical pass survives F1–F3, ask Jev one question over a sample: **given a commit
subject and its changed paths, did this commit ship evidence or describe work?** Compare against
the mechanical label. Jev earns a seat here **only if it disagrees with the mechanical rule in a
way a reader judges correct** — the same bar that killed the harm-rule model seat (four regexes
beat it 12/12 to 11/12) and the tool-call judge.

**Expected outcome, recorded now: I expect F1 to fire.** My prior is that we wrote levels
consistently because a hook demanded it, not because they track anything. If the data says
otherwise, that is a finding I did not expect and it strengthens the convention.

NO-CLAIM in advance: one repo, one team, one session-heavy week. Nothing here generalises to
other repos' commit hygiene.
