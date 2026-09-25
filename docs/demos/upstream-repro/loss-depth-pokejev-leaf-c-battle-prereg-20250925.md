# PokéJev LOSS DEPTH step 4: code-leaf versus code-plus-Noul battle

**Status:** `PREPARED-NOT-MEASURED`. This file is committed before either new
leaf battle arm. No new battle is authorized until the commit containing this
file exists and the arm implementation passes its keyless selftest.

## Question and hypothesis

On the same 200 ordered team pairings, does adding three live Noul features to
the deterministic leaf model improve operational battle outcomes over the
same code-only leaf model?

- **Primary comparison:** paired win-indicator difference
  `d_k = I(code_plus_noul wins on k) - I(code_only wins on k)`, with pairs
  matched by the frozen Stage B `k` and team assignment.
- **Direction:** code-plus-Noul minus code-only. Report the mean paired
  difference in percentage points, its exact two-sided paired permutation
  p-value at alpha .05, and a confidence interval. Do not call the observed
  direction a win without the paired result.
- **Secondary operational outcomes:** each arm's win rate and Wilson 95% CI,
  own/opponent time losses, completed rows, fallback rows by reason, decision
  latency, Jev calls, input tokens, spend, and whether each arm reaches the
  fixed 70% kill line.

The held-out component result does **not** establish that Nouls help: its
paired AUC delta is +0.0117 with 95% interval [-0.009, +0.031], and 13% of
bootstrap resamples are non-positive. This battle therefore treats code-only
as the primary incumbent and code-plus-Noul as the intervention; no gain is
assumed.

## Fixed data and arms

- **N:** 200 pairings, `k=0..199`, using the existing Stage B
  `PAIR_SEED=20260925` and `teams_for(k)` protocol. Each `k` is run once in
  each arm and is the pairing unit; do not reuse a Stage B battle result as a
  new arm outcome.
- **Opponent:** pinned `AbyssalPlayer`; existing `gen9ouclock` harness and
  deadline; same side assignment, teams, and runner settings in both arms.
- **Root and opponent model:** unchanged from Stage B. Both arms retain the
  existing Jev action-prior and opponent-model calls.
- **Code-only leaf:** one frozen logistic model fit on the committed Stage A
  dev rows only, using the five code features in `leaf_c.py`; zero Jev calls
  in the leaf. The model and standardization parameters must be read from a
  committed artifact, not fitted on battle outcomes.
- **Code-plus-Noul leaf:** the same dev-only fit and five code features plus
  exactly three Nouls (`ko_now`, `danger_now`, `switch_needed`) in one
  `jev-1.13.0` request per eligible leaf turn. No extra questions, retries
  beyond the SDK policy, or post-battle refit.
- **References, not new outcomes:** the frozen-alpha reference is
  `receipt-mix-v1.json` (SHA-256
  `c6bb5e368ae9875f1e7d0a05944e2e6c356ef815b5b08cfd240edbfabc6ce17f`):
  114/200 wins (57.0%) and its zero-call control 81/200 (40.5%). These are
  contextual references only; the primary comparison is code-plus-Noul versus
  code-only.

The Stage B source and split inputs are pinned by these hashes:

| Artifact | SHA-256 |
|---|---|
| `work/loss-depth/pokejev-components/leaf-c-dev-v1.json` | `d6a6d10711bcb2fac394019cc163c4c1c993dc42d5327f65c35f4d251912d5fb` |
| `work/loss-depth/pokejev-components/leaf-c-heldout-v1.json` | `4a2159072ea4eacf8e164f22bf8141b31432ce395972fcfc8e5d5681d8b51803` |
| `work/loss-depth/pokejev-components/decision-split-v1.json` | `d10605fa534597820d159c60a723344561a40bf60ed77ff00dedaba4e05d340d` |
| `work/poke-jev/stage-b/receipt.json` | `ecfc4bf86a3b2bb8926cd929512f8cd24e50d85dc4800b60aa65640831010a13` |

## Power and N choice

The planning analysis follows the statistical-power skill at
`/Users/josh/.claude/skills/statistical-power/SKILL.md`: alpha .05,
two-sided, target power .80, and a paired one-sample approximation on
`d_k`. Because `d_k` is bounded in [-1, +1], the table uses the conservative
worst-case `SD(d)=1`; it is a sensitivity/MDE calculation, not a post-hoc
claim of observed power. The final analysis remains the preregistered exact
paired permutation test.

| Paired samples N | 80%-power detectable absolute paired difference |
|---:|---:|
| 100 | 0.2829 (28.29 percentage points) |
| 150 | 0.2302 (23.02 percentage points) |
| 200 | 0.1991 (19.91 percentage points) |
| 250 | 0.1779 (17.79 percentage points) |
| 300 | 0.1623 (16.23 percentage points) |
| 400 | 0.1404 (14.04 percentage points) |

The held-out +0.0117 delta would require approximately 57,339 paired
samples under this conservative approximation, so N=200 cannot resolve that
small component delta. N=200 is fixed nevertheless because the question is a
same-pairing retest over the existing 200 team assignments, not a claim that a
null at this N proves equivalence.

The same scratch analysis reports that, for a single 200-battle arm, observing
at least 140 wins has probability 0.535 when the true win rate is exactly
0.70, 0.762 at 0.72, and 0.955 at 0.75. This makes the 70% threshold's
sampling uncertainty explicit.

## Clock and spend budget

The Noul request was measured live before this preregistration on 20
representative frozen dev states, explicit model `jev-1.13.0`: p50 116.5 ms,
p95 211.8 ms, min 83.2 ms, max 248.1 ms, 12,653 input tokens, and 20
requests. One request carries all three Nouls, so the added leaf cost is
**1 call/eligible leaf turn × 116.5 ms p50 = 0.1165 s p50**. Stage B's
committed p50 decision time is 1,088 ms; additive total of approximately
1.205 s is an estimate, not a measured new-arm latency. It is 8.0% of the
15-second clock. The arm must record actual p50/p95/max and own-side time
losses; a timeout is a fallback, never an imputed answer.

The measured Noul cache contains 4,334 requests and 2,746,218 input tokens,
which is $0.115341156 at $0.042/M input tokens. Using the Stage B live-arm
spend of $1.3975 as the root/opponent estimate gives an expected combined
budget of approximately:

- code-only arm: $1.3975;
- code-plus-Noul arm: $1.3975 + $0.1153 = $1.5128;
- both arms: **$2.9103**, below the fixed **$3.00** cap.

Record actual spend. Stop the live arm immediately on HTTP 402 or credit
exhaustion; do not retry beyond that stop or silently change models. If the
combined projected spend would exceed $3 before both arms have complete rows,
stop and report an incomplete partial, not a battle verdict.

## Replay and output integrity

The pre-existing Stage B HTML replays are not committed. Their integrity
manifest is `work/poke-jev/stage-b/replays-abyssal.sha256`: 200 files,
3,493,449 bytes, canonical listing SHA-256
`1d9cf603c3d28abd6e313cca638b061967753aefc8a227ce427ded231d20c0e6`.
Recompute the listing before re-running component extraction; a mismatch is a
hard stop.

New arm outputs must use distinct paths under
`work/loss-depth/pokejev-components/battle/`, record `k`, team pair, arm,
model, module/model-artifact hashes, and never overwrite the existing
frozen-alpha receipt. Every arm requires exactly 200 completed result rows
with zero unfinished or harness-error rows before analysis. Fallback-bearing
battles remain in the intention-to-treat denominator and are reported by
reason.

## Boundary

This is one same-pairing two-arm battle experiment. It does not establish
that Jev improves over a paid LLM, does not claim the three Nouls are useful
from the held-out AUC delta, and does not retune the 70% line. The references
are not a substitute for the paired code-only comparison. No battle is
permitted until this file is committed and the code-only/code-plus-Noul arms
pass their keyless tests.
