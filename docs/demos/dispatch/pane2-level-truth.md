# P2 — make the verification level mean what it says. Queue of 3.

Measured tonight over **all 1,040 non-merge commits** (`commit-mine-result-20260920.md`):

| level | n | touches a test | docs-only |
|---|---:|---:|---:|
| `oracle` | 97 | **0.000** | **0.804** |
| `live` | 209 | 0.120 | 0.502 |
| `test` | 494 | 0.087 | 0.383 |
| `selftest` | 30 | 0.033 | 0.233 |
| `pending` | 207 | 0.010 | 0.768 |

**Our strongest word never once touched a test file.** The levels grade the prose we wrote about
work, not the work. That is the defect. The fix is not to write better subjects — we have a hook
that has enforced the vocabulary all session and it produced this table. **The fix is that the
vocabulary is wrong and the hook enforces the wrong thing.**

## Unit 1 — propose the corrected vocabulary, with counts

The honest reading is that a receipt commit genuinely *is* evidence — evidence **about** a
measurement that landed earlier — and we have no word for that, so it gets called `oracle`.
So add one, and make the strong words mean executable change.

Draft (argue with it, do not just implement it):

- `receipt` / `doc` — the commit records or explains a result. Markdown only. **This is where
  ~80% of today's `oracle` and ~50% of `live` belong.**
- `test` / `selftest` — the commit changes a test or a selftest.
- `live` / `oracle` — the commit changes **runnable** code or fixtures and its claim was produced
  by running something.
- `pending` — unverified.

**Re-label the 1,040 mechanically under the proposal and report the confusion matrix**: how many
commits keep their level, how many move, and to what. If the proposal moves more than ~40% of
history, it is a rewrite of the past rather than a fix for the future — say so, and prefer a
rule that only binds going forward.

## Unit 2 — enforce it where it can actually bind

The commit-msg hook already parses the subject; it can also see the staged paths. Extend
`.git/hooks/commit-msg-verification-level.sh` (or the foundry equivalent — **check which one is
live before editing**, both exist) so that:

- `oracle|live` on a **docs-only** diff is REFUSED with the suggestion `receipt`;
- `test|selftest` with no test/script path is REFUSED;
- everything else passes silently.

**Creation Gate applies in full** — consumer, gate, observed defect (the table above), retirement
condition. **Measure the false-positive rate against the 1,040 before wiring**: if it would have
blocked legitimate commits, narrow it or refuse and record R49. A hook that fires on correct work
is worse than the decorative levels we have now.

## Unit 3 — a selftest, and only then wire it

`scripts/selftest-level-truth.sh` on the pattern of the other four: arms plant a docs-only
`[oracle]` commit message and require REFUSE, plant a legitimate `[receipt]` and require PASS,
plant a `[test]` with a real test path and require PASS. Stage 80 discovers it by glob — **no new
gate stage.**

If Unit 2's measurement says the rule cannot be made precise, **R49 with a trigger is the correct
outcome** and is worth as much as the hook.

Exit codes unpiped. `scripts/vgrep.sh` for proof-greps. Commit on create. No formatters or
repo-wide gates — I verify at phase end.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
