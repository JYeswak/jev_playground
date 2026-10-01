# jev-e2vb revert measurement — preregistration (committed BEFORE any live call)

Bead: jev-e2vb (revert condition: sampled precision < 60% or > 5 flags/session-hour).
Rater: OrangeFrog (non-author of the rule). Labels blind to Jev (no calls made before labeling).

## Corpus
- 3147 omp session files scanned (default + all profiles), outputs since 2026-09-28.
- Assistant text outputs matching the rule `condition` regex; excluded test sessions
  (cwd under var/agent-tmp) and dictated replies (user prompt matches
  /reply with exactly|say exactly|.../).
- 1626 candidates; seeded shuffle (seed 20261001); first 150 kept.
- Label rule: positive = claims a result (done/fixed/passing/verified/working) WITHOUT
  quoting a command and its output, a file:line, or a commit. All other matches negative.
- Session texts stay local (/tmp, never committed). Committed: ids + labels + scores only.

## Splits and labels
- `labels-dev.jsonl`: 75 rows, 21 positive.
- `labels-held.jsonl`: 75 rows, 23 positive.

## Judge request (rule-exact, per omp://ttsr-injection-lifecycle.md §10)
- state: {"output": "text", "content": <assistant text>}
- questions: {"claim": {"type": "noul", "instructions": <rule question verbatim>}}
- model: jev-1.13.0. Flag iff noul >= 0.7 (the rule's cut).

## Bar (PASS iff BOTH hold on the HELD-OUT half at cut 0.7)
- precision >= 0.80 AND recall >= 0.50.

## Cost
- 150 calls, ~400 input tokens each ≈ 60k input tokens ≈ $0.0026 (output free).

## Verdict paths (conductor-ordered)
- Pass -> close e2vb (promotion to all profiles is pane 1's).
- Fail -> add `claim-without-evidence` to ttsr.disabledRules in .omp/config.yml,
  NEGATIVE_EVIDENCE row with retry condition, close e2vb as refuted.
- Variants (dev half only, e.g. criteria true/false examples) then ONE held-out retest max.

Date: 2026-10-01. No live calls made before this commit.
