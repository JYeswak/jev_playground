# Mining every commit: our verification levels mark documents, not evidence — 2026-09-20 `[live]`

Falsifier committed first at `docs/demos/upstream-repro/commit-mine-falsifier-20260920.md`,
before `work/commit-mine/mine.mjs` existed.

## Why this corpus

Coverage of the three corpora we talk about, measured today:

| corpus | size | touched before tonight |
|---|---:|---|
| CASS messages | 5,181,931 | 120,000 recent-window (**2.32%**) |
| agent-mail messages | 6,510 | 287, one project (**4.4%**) |
| this repo's commits | 1,071 | **0 systematically** |

The commit history was the only one complete, local, free and finite. **1,040 non-merge commits
mined**, every one, no sampling.

## The pre-registered falsifiers, honoured

- **F2 — denominator.** 1,039 of 1,040 subjects carry a parseable level = **99.9%**, bar was 80%.
  PASS. The commit-msg hook did its job.
- **F1 — is the level informative?** Runnable-artifact rate, `live|oracle` (n=306) **0.190** vs
  `pending` (n=207) **0.097**. Gap **+9.3pp**, bar was ±10pp. **F1 FIRES by 0.7 of a point.**

**I am honouring the bar I wrote rather than the result I would prefer.** The direction is the
one I hypothesised; the magnitude is under my own threshold, so the finding is *"decorative, or
at best weakly informative"* — not *"informative, nearly significant"*. Moving a pre-registered
line after seeing the data is the failure this lane exists to catch, and 0.7pp is exactly where
the temptation lives.

**F3 holds**: the classifier is path-matching. This is a claim about which paths a commit
touches, not about whether it carried evidence.

## The finding I did not predict

| level | n | touches a test | touches a script | **docs-only** |
|---|---:|---:|---:|---:|
| `oracle` | 97 | **0.000** | 0.041 | **0.804** |
| `live` | 209 | 0.120 | 0.120 | 0.502 |
| `test` | 494 | 0.087 | 0.138 | 0.383 |
| `selftest` | 30 | 0.033 | **0.667** | 0.233 |
| `pending` | 207 | 0.010 | 0.053 | 0.768 |

**`oracle` is our strongest word and it never once touched a test file.** Four in five `oracle`
commits changed only markdown. `live` is half documents. The one level that means what it says is
`selftest` — two thirds touch a script — and it is the rarest, used 30 times.

Read plainly: **the levels grade the prose we wrote about work, not the work.** That is consistent
with how they are applied — a ruling recorded in a receipt is genuinely `live` evidence *about a
measurement*, while the measurement itself landed in an earlier commit. The convention is honest
in intent and weak as a signal, and anyone reading our history to find where evidence lives
should filter on **paths, not on our adjectives**.

## No Jev call was made

The falsifier said Jev gets a seat only *if the mechanical pass survives F1–F3*. F1 fired, so the
model question was not asked. **Spending calls after the gate fired would be shopping for a
second opinion**, which is the behaviour the pre-registration exists to prevent. Same discipline
that killed the harm-rule seat and the tool-call judge.

## NO-CLAIM

One repo, one week-heavy session, 1,040 commits by effectively one author-identity. Path-matching
only. Nothing here generalises to other repos' commit hygiene, and the 0.7pp margin means a
different runnable-path definition could move this either way — which is itself a reason not to
lean on the number.

Reproduce: `node work/commit-mine/mine.mjs > /tmp/commits.jsonl` (~12s, read-only).

<!-- suggestion probe 1789922333 -->
