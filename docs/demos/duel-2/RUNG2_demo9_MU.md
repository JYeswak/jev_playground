# Duel-2 rung 2 — demo-9 review signal (non-author: pane 3 muse)

Status: structural reasoning only. Candidate: demo-9 continuous review
signal (§5.9, admitted by ruling, UNSCORED). This demo is RECUSED at
rung 1 (proposer 820 vs my 550); this assessment is its first rung-2
pass, by the eligible non-author. No contract, `PLAN.md`, or demo
implementation was edited. No Jev call was run.

## 1. What Noul judges; what Choice chooses

Primary shape is Noul-per-dimension over a deterministically supplied
diff. For each dimension in a fixed set (correctness, complexity,
changeability, modularity, tests, security — the §5.9 set), Noul answers
whether the diff *degrades* that dimension, with probability:

> This diff changes `<files>`. For the dimension `<D>`, the change
> degrades it only if the new code is worse than the old code on that
> dimension's stated meaning. Judge the diff, not the idea.

True/false criteria per dimension are caller-supplied definitions, not
model inventions; insufficient context (diff too large, language
unsupported, generated files) withholds per dimension rather than
approving. No Choice call is needed in the minimal shape: dimensions
are independent signals, not a selection.

An optional second shape is legitimate: a **Choice** severity bucket
(`none / cosmetic / substantive / blocking-advisory`) from the supplied
finite set per flagged dimension. Buckets must be caller-supplied;
severity prose must not be model-written.

## 2. Why ordinary chat is measurably worse

Tested shape. A pinned review rubric recovers comment comparability
only cosmetically: prose bots emit paragraphs whose severity lives in
adjectives, with no per-dimension probability series comparable across
diffs and no mandatory withhold when the diff exceeds understanding.
The typed contract (per-dimension probability + finite reason codes +
withhold) is what makes an FP-rate receipt possible at all — and the FP
rate is the demo's entire ship condition. A chat reviewer can sound
thorough while reviewing nothing; a dimension vector with six
probabilities cannot hide an unjudged dimension.

The sharper comparison is the §5.9-mandated one: `ubs` is deterministic
pattern matching, so per §3i it is a **baseline to beat, not an owner**.
The Jev value is exactly the dimensions patterns cannot see — design
coherence (does the change match its stated intent) and semantic
correctness beyond rule shapes. Pattern-matchable findings re-reported
with probabilities would make demo-9 an expensive `ubs` echo; the
contract must define at least two non-pattern dimensions (design
coherence, intent-match) and count their findings separately from
pattern-overlapping ones (security, tests), or the superset question
cannot even be asked.

## 3. Extraction, generation, summarization audit

Deterministic stages: diff supplied via `git diff` bytes (never a model
summary of the change — judging a summary of the diff instead of the
diff would be the demo-5 defect wearing review clothes); file/language
filtering by policy; per-dimension Noul calls; finite reason-code
mapping; receipt assembly. Forbidden: model-written review prose (the
output is dimensions + codes, never paragraphs — a prose review is
generation, and generation voids this clearance); model-selected
dimensions (the set is fixed by the contract); judging file summaries,
PR descriptions, or commit messages *instead of* the diff (input
substitution that silently narrows what was reviewed); severity
invention outside the supplied buckets.

## 4. Verdict

**CLEARED**, conditional on (a) dimensions-plus-codes output with no
prose generation, (b) at least two non-pattern dimensions counted
separately, and (c) the §5.9 advisory-only constraint (findings never
block; no exit-code enforcement until an FP rate is published — the
enforcement question is out of rung-2 scope but the shape must not
pre-install it).

Explicitly deferred, not decided: whether the findings are a strict
superset of the `ubs` baseline (1 critical / 6 warnings / 27 info, all
classified non-defect, `eval()` control firing). That is a measured
rung-3/4 comparison on a labelled diff set, and this clearance does
not pre-count it. If a measured run shows demo-9's findings are a
subset of `ubs` output with probabilities attached, the demo fails
there — structurally it clears here because disjoint-by-design
dimensions exist in the contract, not because lift is shown.

## Boundary and NO-CLAIM

Clearance covers Jev-necessity only: typed per-dimension judgment with
calibration potential that pattern matching structurally lacks. Not
claimed: calibration, demand beyond the existing 550/820 split, FP
rate, installability, cost per diff, lift over `ubs`, or that any team
will run this. No implementation, fixtures, or live calls were used;
question wordings are specified shapes, not executed prompts.
