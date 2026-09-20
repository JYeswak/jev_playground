# jev-eval-honesty — plan delta (adopt, don't author)

Scope for this package: THREE mechanisms only. Everything else in the
evaluation-framework skill we adopt as-is and do NOT rebuild. No Jev calls
this pass; the proof commands below run in a later pass.

Adopted sources (read 2026-09-19, not re-derived):

- `~/.claude/skills/evaluation-framework/SKILL.md` — 3 evaluation modes,
  rubric process, continuous pipeline ([1] code checks → [2] model eval →
  [3] regression check → [4] gate), gate thresholds, anti-patterns, checklist.
- `~/.claude/skills/evaluation-framework/references/evaluation-modes.md`
- `~/.claude/skills/evaluation-framework/references/rubric-library.md`
- `~/.claude/skills/evaluation-framework/references/sources.md`
- `~/.claude/skills/evaluation-framework/examples/eval-config.yaml`
- Lane instruments reused verbatim:
  `work/jev-client/measure-kit.mjs::gradeQuestion(samples, threshold=0.5)`
  → `{ correct, asked, yes, trueCount, alwaysNo, alwaysYes, best, spread,
  near, scores, verdict }` with verdict `DEGENERATE | DISCRIMINATES | WEAK`;
  `work/jev-client/src/index.ts::readRow(line)` handling BOTH omp session
  row shapes — A) `{ customType: { type, data } }` (observer rows) and
  B) `{ customType: "…", data }` (harm-rule / failure rows).

## Delta 1 — outcome join with selector verification + zero-hit guard

- Framework already covers: Mode 1 code-based checks (format / content
  presence / structure) as pipeline step [1]; the "fixed test suite of
  representative examples" rule and the "evaluating on production data only"
  anti-pattern. We do NOT build a check-runner, a format validator, or a
  suite format — the skill's `evaluator.py --config eval-config.yaml` shape
  is the pattern.
- Exact delta file (later pass): `work/jev-eval-honesty/outcome-join.mjs` —
  joins keyed Jev scores to outcome labels through `readRow` (both shapes A
  and B), asserts the selector matched ≥1 row per side, and exits non-zero
  on a zero-hit join instead of reporting "no rows" as a clean result
  (the silent-empty failure recorded in `readRow`'s doc comment).
- Live proof command:
  `node work/jev-eval-honesty/outcome-join.mjs --scores <run.jsonl> --labels <labels.json>`

## Delta 2 — co-presence check

- Framework already covers: Mode 2 golden comparison (judge output vs
  reference answer) and the per-dimension score report. We do NOT build a
  grader, a rubric, or a comparison prompt — golden comparison is adopted
  whole.
- Exact delta file (later pass): `work/jev-eval-honesty/co-presence.mjs` —
  before any grading, proves each join key is present on BOTH sides (score
  row and label row); a key missing from either side is reported as a
  dropped case, never silently averaged over. This is the join-key half the
  framework assumes its fixed suite already guarantees.
- Live proof command:
  `node work/jev-eval-honesty/co-presence.mjs --scores <run.jsonl> --labels <labels.json>`

## Delta 3 — random-judge + own-constant calibration via gradeQuestion

- Framework already covers: baseline scores on current output, regression
  thresholds (pass ≥ baseline−0.3, review to −0.5, fail below), and the "no
  baseline established" anti-pattern. We do NOT build baseline storage, gate
  thresholds, or a rubric-grading prompt — adopted whole.
- Exact delta file (later pass):
  `work/jev-eval-honesty/random-judge.mjs` — runs a no-signal random judge
  over the same cases and feeds both judges through the existing
  `gradeQuestion` own-constant bar, proving the bar bites before any real
  judge is quoted.
- Live proof command:
  `node work/jev-eval-honesty/random-judge.mjs --labels <labels.json> --seeds 5`

## Regression baseline vs constant baseline

These are different bars and both must hold. The framework's regression
baseline (SKILL.md pipeline step [3], gate thresholds) asks "did this change
move scores versus last run's baseline" — it catches drift over time but
says nothing about whether a question ever carried signal. The lane's
constant baseline (`gradeQuestion`: DEGENERATE if the same verdict on every
case, else DISCRIMINATES only if correct beats the better of always-no /
always-yes plus the near-threshold count) asks "does this question beat
answering the majority every time" — it catches base rate wearing a signal's
clothes on day one. The commit-judge receipt is the standing example:
`docs/demos/upstream-repro/commit-judge-31-20260919.md` — describes
DEGENERATE (30/31 correct but yes on 31/31 against a 30/31 always-yes
constant), overstates WEAK (17/31 vs 31), omits WEAK (28/31 vs 30): no
question beats its own constant, so there is nothing worth regression-gating.
